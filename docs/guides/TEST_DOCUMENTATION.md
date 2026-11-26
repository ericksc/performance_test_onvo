# Suite de Pruebas de Rendimiento para API ONVO Pay

## 📋 Índice

1. [Introducción](#introducción)
2. [Marco Teórico](#marco-teórico)
3. [Criterios de Prueba](#criterios-de-prueba)
4. [Instalación](#instalación)
5. [Uso](#uso)
6. [Resultados e Interpretación](#resultados-e-interpretación)
7. [Referencias](#referencias)

---

## Introducción

Este documento describe una suite completa de pruebas de rendimiento para la API REST de ONVO Pay, basada en el estándar ISO/IEC 25010:2011, con énfasis en el atributo de **comportamiento temporal** (time behaviour).

**Objetivo:** Evaluar sistemáticamente el tiempo de respuesta de operaciones críticas en la API y establecer una línea base de rendimiento que permita detectar degradaciones.

**Alcance:** 
- Pruebas de caja negra desde la perspectiva del consumidor
- Endpoints: `GET /v1/customers`, `GET /v1/payment-intents/{id}`, `POST /v1/payment-intents`
- Modo de prueba: llaves con prefijo `onvo_test_secret_key_`
- Tiempos observados incluyen latencia de red

---

## Marco Teórico

### ISO/IEC 25010:2011 - Eficiencia del Desempeño

Según la norma internacional, la **eficiencia del desempeño** es un atributo de calidad no funcional que comprende tres subatributos:

1. **Comportamiento temporal** (Time behaviour) ← Nuestro enfoque
2. Utilización de recursos (Resource utilisation)
3. Capacidad (Capacity)

El **comportamiento temporal** se define como "el grado en que los tiempos de respuesta, procesamiento y tasas de rendimiento de un sistema cumplen con los requisitos establecidos".

### Por qué es importante en sistemas financieros

- Los tiempos de respuesta afectan directamente la experiencia del usuario
- Pueden influir en el tiempo total de procesamiento transaccional
- Permiten detectar problemas preventivamente
- Son observables desde la perspectiva del cliente

### Metodología de medición

**Definición de tiempo de respuesta:**
```
Tiempo de respuesta = Tiempo de recepción completa de respuesta - Tiempo de envío de solicitud
(Medido en el cliente, incluye latencia de red)
```

**Supuestos:**
- Mediciones desde un mismo equipo y red
- Se descartan primeras 10 solicitudes (calentamiento)
- Solo se consideran respuestas exitosas (2xx)
- Errores y timeouts se contabilizan por separado
- Expresión en milisegundos (ms)
- Métricas: mediana (p50), p95, p99 (no promedio simple)

---

## Criterios de Prueba

### CT-01: Tiempo de respuesta de consultas

**¿Qué mide?**
Tiempo de respuesta de operaciones de lectura sin concurrencia.

**Procedimiento:**
1. Descartar 10 solicitudes iniciales (calentamiento)
2. Medir 200 solicitudes GET secuenciales:
   - `GET /v1/customers?limit=1` (listar clientes)
   - `GET /v1/payment-intents` (listar intenciones de pago)
3. Registrar solo respuestas 2xx
4. Calcular p50 y p95

**Criterio de aceptación:**
```
p50 ≤ 400 ms Y p95 ≤ 800 ms (en CADA operación)
Ninguna solicitud supera 10 segundos
```

**Interpretación:**
- **p50 (mediana)**: tiempo típico de respuesta
- **p95**: tiempo en 95% de solicitudes (colas ocasionales)
- Valores superiores sugieren:
  - Problemas de red
  - Carga en servidor
  - Fallos en endpoints

**Ejemplo de PASS:**
```
GET /v1/customers
  p50: 350 ms ✓ (< 400 ms)
  p95: 750 ms ✓ (< 800 ms)
  
GET /v1/payment-intents
  p50: 320 ms ✓ (< 400 ms)
  p95: 620 ms ✓ (< 800 ms)
```

---

### CT-02: Tiempo de respuesta de creación

**¿Qué mide?**
Tiempo de respuesta de operaciones de escritura sin concurrencia (más procesamiento en servidor).

**Procedimiento:**
1. Descartar 10 solicitudes iniciales
2. Medir 200 solicitudes POST secuenciales:
   - `POST /v1/payment-intents` (crear intención de pago)
3. Usar datos válidos de prueba
4. Registrar solo respuestas 2xx
5. Calcular p95 y p99

**Criterio de aceptación:**
```
p95 ≤ 1500 ms Y p99 ≤ 2500 ms
Ninguna solicitud supera 10 segundos
```

**Interpretación:**
- **p99**: tiempo en 99% de solicitudes
- Valor más alto que CT-01 (normal: escritura requiere más procesamiento)
- Si p95 > 1500 ms:
  - Validación lenta
  - Almacenamiento lento
  - Fila de procesamiento

**Ejemplo de PASS:**
```
POST /v1/payment-intents
  p95: 1200 ms ✓ (< 1500 ms)
  p99: 2100 ms ✓ (< 2500 ms)
```

---

### CT-03: Estabilidad de respuestas

**¿Qué mide?**
Consistencia y previsibilidad del rendimiento (detecta colas largas).

**Procedimiento:**
1. Usar datos de CT-01 y CT-02
2. Para cada operación, calcular ratio: `p99 / p50`
3. Comparar con umbral

**Criterio de aceptación:**
```
p99 ≤ 3 × p50 (en TODAS las operaciones)
```

**Interpretación:**
- **Ratio cercano a 1**: respuestas muy consistentes (ideal)
- **Ratio = 2-3**: variación moderada (aceptable)
- **Ratio > 3**: colas largas, degradación bajo carga
  - Algunos usuarios esperan mucho más que otros
  - Señal de saturación o problemas puntuales

**Ejemplo:**
```
GET /v1/customers
  p50: 300 ms, p99: 700 ms
  Ratio: 700/300 = 2.33 ✓ (< 3)
  
GET /v1/payment-intents
  p50: 150 ms, p99: 600 ms
  Ratio: 600/150 = 4.0 ✗ (> 3)
  → Algunas consultas muy lentas, investigar
```

---

### CT-04: Comportamiento bajo concurrencia

**¿Qué mide?**
Cómo se degrada el rendimiento con usuarios simultáneos.

**Procedimiento:**
1. Establecer línea base (p95 de CT-01 y CT-02)
2. Ejecutar 10 usuarios virtuales concurrentes
3. Duración: 5 minutos
4. Mezcla: 60% consultas, 40% creación
5. Registrar:
   - p95 de cada operación
   - Tasa de errores 5xx
   - Timeouts (> 10s)
   - Respuestas 429 (rate limit)

**Criterio de aceptación:**
```
p95 aumenta máximo 30% respecto a línea base
Tasa de errores ≤ 1%
Respuestas 429 se registran aparte
```

**Interpretación:**
- **Degradación ≤ 30%**: API escalable
- **Degradación > 30%**: posible cuello de botella
- **Errores 5xx**: problemas en servidor
- **Errores 429**: límite de uso alcanzado (esperar y reintentar)

**Ejemplo:**
```
Línea base (CT-01): p95 = 800 ms
Concurrencia (CT-04): p95 = 950 ms
Degradación: 950/800 - 1 = 18.75% ✓ (< 30%)

Errores: 50/5000 solicitudes = 1% ✓ (≤ 1%)
```

---

### CT-05: Repetibilidad y degradación

**¿Qué mide?**
Consistencia del rendimiento entre diferentes momentos (detecta degradaciones en el tiempo).

**Procedimiento:**
1. Ejecutar CT-01 y CT-02 en 3 momentos distintos:
   - Día 1, hora 10:00
   - Día 2, hora 14:00
   - Día 3, hora 09:00 (franjas y días diferentes)
2. Registrar p95 de cada ejecución
3. Calcular variación máxima respecto a mediana

**Criterio de aceptación:**
```
Variación ≤ 20% respecto a línea base (mediana de 3 ejecuciones)
```

**Interpretación:**
- **Variación ≤ 20%**: rendimiento estable
- **Variación > 20%**: posible degradación
  - Cambios en infraestructura
  - Cambios en carga
  - Problemas intermitentes

**Ejemplo:**
```
Ejecución 1: p95 = 750 ms
Ejecución 2: p95 = 820 ms
Ejecución 3: p95 = 780 ms
Mediana: 780 ms

Variación máx: (820 - 780) / 780 = 5.1% ✓ (< 20%)
Rendimiento ESTABLE
```

---

## Instalación

### Requisitos

- Python 3.8+
- pip
- Conexión a internet

### Pasos

1. **Clona o descarga el proyecto:**
```bash
cd c:\work\poc_onvo
```

2. **Configura tu llave de API:**
```bash
python configurar_clave.py
# Pega tu llave onvo_test_secret_key_...
```

3. **Instala dependencias (si es necesario):**
```bash
pip install requests urllib3
```

4. **Verifica configuración:**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ONVO_TEST_SECRET_KEY', 'NO CONFIGURADO')[:30])"
```

---

## Uso

### Ejecutar suite completa

```bash
# Desde la carpeta raíz
python test_onvo_performance.py
```

**Salida esperada:**
```
██████████████████████████████████████████████████████████████████
SUITE COMPLETA DE PRUEBAS - ONVO PAY API
ISO/IEC 25010:2011 - Comportamiento Temporal
██████████████████████████████████████████████████████████████████
Inicio: 2024-11-25T11:30:00.000000
Llave API: onvo_test_secret_key_...

======================================================================
CT-01: Tiempo de respuesta de consultas
======================================================================
...
```

### Ejecutar criterio específico

```bash
# En un script Python personalizado
from test_onvo_performance import ONVOPerformanceTest
import os

api_key = os.getenv("ONVO_TEST_SECRET_KEY")
tester = ONVOPerformanceTest(api_key)

# Ejecuta solo CT-01
results = tester.ct_01_query_response_time()

# O solo CT-02
results = tester.ct_02_creation_response_time()

# O solo CT-04 (concurrencia)
results = tester.ct_04_concurrency(num_users=10, duration_sec=300)
```

### Parámetros configurables

```python
# Número de solicitudes por test
tester = ONVOPerformanceTest(api_key, num_requests=200)

# Concurrencia (CT-04)
tester.ct_04_concurrency(num_users=10, duration_sec=300)

# Repetibilidad (CT-05)
tester.ct_05_repeatability(executions=3, interval_sec=300)
```

---

## Resultados e Interpretación

### Archivo de salida: `test_results.json`

```json
{
  "CT-01": {
    "clientes": {
      "stats": {
        "min": 120.5,
        "max": 850.2,
        "mean": 350.1,
        "median": 345.0,
        "p50": 345.0,
        "p95": 720.3,
        "p99": 820.1,
        "stdev": 125.4
      },
      "successful": 200,
      "timeouts": 0,
      "verdict": "PASS"
    }
  },
  "CT-02": {
    "stats": {
      "p50": 580.0,
      "p95": 1250.5,
      "p99": 1900.2
    },
    "successful": 200,
    "timeouts": 0,
    "verdict": "PASS"
  },
  ...
}
```

### Interpretación de resultados

#### Caso 1: Todos PASS ✓

```
✓ CT-01_clientes: PASS
✓ CT-01_payment_intents: PASS
✓ CT-02: PASS
✓ CT-03_CT-01_clientes: PASS
✓ CT-03_CT-02: PASS
```

**Acción:** 
- API cumple umbrales de rendimiento
- Mantener monitoreo periódico

---

#### Caso 2: Fallos en CT-01

```
✗ CT-01_clientes: FAIL
  p95: 950 ms (límite: 800 ms)
```

**Posibles causas:**
1. Problema de red (latencia aumentada)
2. Servidor ONVO bajo carga
3. Base de datos lenta
4. Cambio en infraestructura

**Acciones:**
1. Reintentar desde otra red/máquina
2. Revisar dashboard de ONVO
3. Contactar soporte ONVO
4. Ajustar umbral si es consistente

---

#### Caso 3: Fallos en CT-04

```
✗ CT-04: FAIL
  p95 aumenta 45% (límite: 30%)
  Error rate: 2.5% (límite: 1%)
```

**Posibles causas:**
1. API no es escalable
2. Límite de conexiones alcanzado
3. Problema de autenticación bajo carga
4. Rate limiting activado

**Acciones:**
1. Revisar respuestas 429
2. Aumentar interval entre solicitudes
3. Contactar soporte ONVO sobre límites
4. Considerar pool de conexiones

---

#### Caso 4: Fallos en CT-05

```
✗ CT-05: FAIL
  Variación clientes: 35% (límite: 20%)
  Ejecución 2: 950 ms (vs mediana: 650 ms)
```

**Posibles causas:**
1. Degradación en hora específica
2. Mantenimiento en servidor
3. Cambios en carga

**Acciones:**
1. Revisar logs en hora de alta medición
2. Consultar con ONVO sobre mantenimientos
3. Ejecutar CT-04 en ese momento

---

## Referencias

### Documentación

- **ISO/IEC 25010:2011** - Systems and software engineering — System and software quality models
- **ONVO Pay API Docs** - https://docs.onvopay.com/api
- **RFC 7231** - HTTP/1.1 Semantics and Content

### Métricas y percentiles

- **p50 (Mediana)**: valor central de la distribución
- **p95**: valor bajo el cual cae el 95% de las solicitudes
- **p99**: valor bajo el cual cae el 99% de las solicitudes

### Herramientas utilizadas

- `requests` - Cliente HTTP
- `statistics` - Cálculos de percentiles
- `concurrent.futures` - Pruebas de concurrencia

---

## Notas Finales

- **No es prueba de carga extrema**: CT-04 con 10 usuarios es concurrencia moderada
- **Incluye latencia de red**: No mide solo rendimiento de servidor
- **Basado en estándares internacionales**: ISO/IEC 25010:2011
- **Adaptable**: Umbrales pueden ajustarse según contexto

---

**Documento generado:** 2024-11-25  
**Versión:** 1.0
