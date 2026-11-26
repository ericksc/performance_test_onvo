# 🧪 Pruebas de Rendimiento para API ONVO Pay

Suite completa de pruebas de rendimiento basada en **ISO/IEC 25010:2011** (Comportamiento Temporal)

## 📚 Tabla de Contenidos

- [Inicio Rápido](#inicio-rápido)
- [Criterios de Prueba](#criterios-de-prueba)
- [Uso Detallado](#uso-detallado)
- [Interpretación de Resultados](#interpretación-de-resultados)
- [FAQ](#faq)

---

## Inicio Rápido

### 1. Configurar llave API (primera vez)

```bash
python configurar_clave.py
# Pega tu llave onvo_test_secret_key_...
```

### 2. Ejecutar pruebas rápidas (CT-01, CT-02, CT-03)

```bash
python run_performance_tests.py
```

**Duración:** ~5 minutos  
**Genera:** `test_results_BASELINE_YYYYMMDD_HHMMSS.json`

### 3. Ver documentación completa

```bash
# En VS Code o tu editor
cat TEST_DOCUMENTATION.md
```

---

## Criterios de Prueba

| Criterio | Nombre | ¿Qué mide? | Duración |
|----------|--------|-----------|----------|
| **CT-01** | Consultas | Tiempo de lectura sin concurrencia (200 req) | ~2 min |
| **CT-02** | Creación | Tiempo de escritura sin concurrencia (200 req) | ~2 min |
| **CT-03** | Estabilidad | Consistencia (p99 ≤ 3×p50) | Inmediato |
| **CT-04** | Concurrencia | Rendimiento con 10 usuarios (5 min) | ~6 min |
| **CT-05** | Repetibilidad | Consistencia en el tiempo (3 ejecuciones) | ~15 min |

### Criterios de aceptación

```
CT-01: p50 ≤ 400 ms, p95 ≤ 800 ms (consultas)
CT-02: p95 ≤ 1500 ms, p99 ≤ 2500 ms (creación)
CT-03: p99 ≤ 3 × p50 (todas las operaciones)
CT-04: p95 aumenta máximo 30%, errores ≤ 1%
CT-05: Variación ≤ 20% entre ejecuciones
```

---

## Uso Detallado

### Ejecutar suite completa (todos los criterios)

```bash
python run_performance_tests.py --all
```

**⚠️ Tiempo total:** ~30 minutos (incluye 3 ejecuciones con intervalos)

### Ejecutar criterios específicos

```bash
# Solo CT-01 (consultas)
python run_performance_tests.py --ct-01

# Solo CT-02 (creación)
python run_performance_tests.py --ct-02

# CT-01 y CT-02
python run_performance_tests.py --ct-01 --ct-02

# CT-04 (concurrencia) con parámetros personalizados
python run_performance_tests.py --ct-04 --users 20 --duration 600

# CT-05 (repetibilidad) con 5 ejecuciones
python run_performance_tests.py --ct-05 --exec 5 --interval 600
```

### Parámetros disponibles

```bash
python run_performance_tests.py --help

Opciones:
  --all                   Ejecutar todos los criterios
  --ct-01                 Solo CT-01
  --ct-02                 Solo CT-02
  --ct-03                 Solo CT-03
  --ct-04                 Solo CT-04 (concurrencia)
  --ct-05                 Solo CT-05 (repetibilidad)
  --requests N            Solicitudes por test (default: 200)
  --users N               Usuarios para CT-04 (default: 10)
  --duration N            Duración CT-04 en segundos (default: 300)
  --exec N                Ejecuciones para CT-05 (default: 3)
  --interval N            Intervalo entre ejecuciones CT-05 (default: 300s)
```

### Uso directo desde Python

```python
from test_onvo_performance import ONVOPerformanceTest
import os

# Obtiene llave
api_key = os.getenv("ONVO_TEST_SECRET_KEY")

# Crea tester
tester = ONVOPerformanceTest(api_key, num_requests=200)

# Ejecuta criterios individuales
tester.ct_01_query_response_time()
tester.ct_02_creation_response_time()
tester.ct_03_stability()

# O todos de una vez
results = tester.run_all_tests()
```

---

## Interpretación de Resultados

### Archivo de salida

```json
{
  "CT-01": {
    "clientes": {
      "stats": {
        "p50": 350.5,      // Mediana: tiempo típico
        "p95": 750.3,      // 95% de solicitudes < 750ms
        "p99": 820.1,      // 99% de solicitudes < 820ms
        "stdev": 125.4     // Desviación estándar
      },
      "successful": 200,
      "timeouts": 0,
      "verdict": "PASS"
    }
  },
  ...
}
```

### Interpretación por criterio

#### CT-01: Consultas normales ✓

```
p50: 350 ms - tiempo típico
p95: 750 ms - incluso consultas lentas < 800ms
Veredicto: PASS
```

**Significa:** API rápida en lectura

#### CT-02: Creación más lenta (normal) ✓

```
p95: 1200 ms - escritura más lenta que lectura
p99: 2000 ms - algunas operaciones lentas pero dentro del límite
Veredicto: PASS
```

**Significa:** Procesamiento en servidor es normal

#### CT-03: Estabilidad consistente ✓

```
p99/p50 ratio: 2.0 (< 3.0)
Veredicto: PASS
```

**Significa:** Respuestas predecibles, sin colas largas

#### CT-04: Comportamiento bajo carga ✓

```
p95 baseline: 800 ms
p95 con 10 usuarios: 920 ms
Aumento: 15% (< 30%)
Errores: 0.5% (< 1%)
Veredicto: PASS
```

**Significa:** API es escalable

#### CT-05: Rendimiento consistente en el tiempo ✓

```
Ejecución 1: 750 ms
Ejecución 2: 800 ms
Ejecución 3: 770 ms
Variación: 6% (< 20%)
Veredicto: PASS
```

**Significa:** Ninguna degradación detectada

---

## Resultados problemas comunes

### ❌ CT-01: p95 > 800 ms

**Posibles causas:**
1. Red lenta
2. Servidor sobrecargado
3. Cambio reciente en infraestructura

**Acciones:**
- Reintentar desde otra máquina/red
- Contactar ONVO si es consistente
- Revisar logs de servidor

### ❌ CT-04: p95 aumenta > 30%

**Posibles causas:**
1. API no es escalable
2. Límite de conexiones alcanzado
3. Rate limiting

**Acciones:**
- Revisar respuestas 429
- Aumentar interval entre solicitudes
- Contactar ONVO sobre límites de concurrencia

### ❌ CT-05: Variación > 20%

**Posibles causas:**
1. Degradación en hora específica
2. Mantenimiento en servidor
3. Cambios en carga de red

**Acciones:**
- Ejecutar CT-04 durante alta variación
- Consultar con ONVO sobre mantenimientos
- Revisar logs

---

## Workflow recomendado

### Establececer línea base (una vez)

```bash
# Día 1
python run_performance_tests.py --ct-01 --ct-02 --ct-03
# Archivo: test_results_BASELINE_20240101_100000.json

# Día 2 (franjai horaria diferente)
python run_performance_tests.py --ct-01 --ct-02 --ct-03
# Archivo: test_results_BASELINE_20240102_150000.json

# Día 3 (hora diferente)
python run_performance_tests.py --ct-01 --ct-02 --ct-03
# Archivo: test_results_BASELINE_20240103_090000.json

# Comparar variación entre los 3 archivos
# Si variación ≤ 20%, usar como línea base oficial
```

### Monitoreo periódico

```bash
# Semanal: ejecutar CT-01, CT-02, CT-03
python run_performance_tests.py

# Mensual: ejecutar CT-01, CT-02, CT-03, CT-04
python run_performance_tests.py --ct-04

# Trimestral: ejecutar todo (incluye CT-05)
python run_performance_tests.py --all
```

### Detectar degradación

```bash
# Comparar nuevo resultado con línea base
# Si p95 > línea base × 1.2 (20% aumento), investigar
```

---

## FAQ

### P: ¿Cuánto tiempo toman las pruebas?

A:
- CT-01 + CT-02 + CT-03: ~5 minutos
- Agregar CT-04: +6 minutos (~11 min total)
- Agregar CT-05: +20 minutos (~30 min total)

### P: ¿Puedo ejecutar desde múltiples máquinas?

A: Sí, pero los resultados incluirán latencia de red. Los tiempos serán diferentes según ubicación de máquina. Para consistencia, usa la misma máquina.

### P: ¿Qué significa p95?

A: Percentil 95. El 95% de solicitudes responden en ese tiempo o menos. El 5% puede ser más lento.

### P: ¿Por qué descartar 10 primeras solicitudes?

A: "Calentamiento" - permite que cache, conexiones, etc. se establezcan. Las primeras solicitudes son artificialmente lentas.

### P: ¿Qué son los timeouts?

A: Solicitudes que superan 10 segundos. Se registran por separado como problema grave.

### P: ¿Debo revisar cada resultado?

A: Sí. Revisa:
1. Veredicto (PASS/FAIL)
2. Si hay timeouts
3. Si hay respuestas 429 (rate limit)

### P: ¿Los umbrales son fijos?

A: No. Pueden ajustarse según contexto:
- Sistema financiero crítico → umbrales más estrictos
- Prototipo interno → umbrales más relajados

---

## Referencia técnica

### Métricas

| Métrica | Descripción |
|---------|-------------|
| **p50** | Mediana, tiempo típico |
| **p95** | 95% de solicitudes responden en este tiempo |
| **p99** | 99% de solicitudes responden en este tiempo |
| **stdev** | Desviación estándar (variabilidad) |

### Endpoints probados

| Operación | Endpoint | Método |
|-----------|----------|--------|
| Listar clientes | `/v1/customers?limit=1` | GET |
| Listar intenciones | `/v1/payment-intents` | GET |
| Crear intención | `/v1/payment-intents` | POST |

### Configuración de red

- Reintentos automáticos (3x con backoff)
- Timeout: 15 segundos por solicitud
- Sesión HTTP con keep-alive

---

## Documentación relacionada

- [TEST_DOCUMENTATION.md](./TEST_DOCUMENTATION.md) - Marco teórico completo
- [https://docs.onvopay.com/api](https://docs.onvopay.com/api) - API ONVO
- [ISO/IEC 25010:2011](https://en.wikipedia.org/wiki/ISO/IEC_25010) - Estándar de calidad

---

**Última actualización:** 2024-11-25  
**Versión:** 1.0  
**Contacto:** Equipo de Calidad y Pruebas
