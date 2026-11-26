# 🧪 Pruebas de Rendimiento - Índice de Acceso Rápido

## 📂 Archivos principales

### Documentación

| Archivo | Descripción | Leer cuando... |
|---------|-------------|----------------|
| [**PERFORMANCE_TESTS_README.md**](./PERFORMANCE_TESTS_README.md) | Guía de uso rápido | Quieres ejecutar pruebas |
| [**TEST_DOCUMENTATION.md**](./TEST_DOCUMENTATION.md) | Marco teórico completo | Quieres entender los criterios |
| [**PRUEBAS_QUICKSTART.md**](./PRUEBAS_QUICKSTART.md) | Inicio en 5 minutos | Tienes prisa |

### Scripts

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| [**test_onvo_performance.py**](./test_onvo_performance.py) | Suite principal de pruebas | Lógica de los 5 criterios (CT-01 a CT-05) |
| [**run_performance_tests.py**](./run_performance_tests.py) | Script de ejecución | `python run_performance_tests.py` |

### Resultados

Los resultados se guardan en:
```
test_results_BASELINE_YYYYMMDD_HHMMSS.json
test_results_CT04_YYYYMMDD_HHMMSS.json
test_results_CT05_YYYYMMDD_YYYYMMDD_HHMMSS.json
```

---

## 🚀 Comenzar ahora

### 1. Setup inicial (2 min)

```bash
# Configura tu llave API (una sola vez)
python configurar_clave.py
```

### 2. Ejecutar pruebas rápidas (5 min)

```bash
# Ejecuta CT-01, CT-02, CT-03
python run_performance_tests.py
```

### 3. Ver resultados

```bash
# Archivo JSON con todos los datos
cat test_results_BASELINE_*.json

# O visualizar en VS Code
code test_results_BASELINE_*.json
```

---

## 📊 Criterios en 60 segundos

```
CT-01: ¿Qué tan rápido responde la API en lectura?
       Límite: p50 ≤ 400ms, p95 ≤ 800ms
       Duración: ~2 min

CT-02: ¿Qué tan rápido responde al crear datos?
       Límite: p95 ≤ 1500ms, p99 ≤ 2500ms
       Duración: ~2 min

CT-03: ¿Qué tan consistentes son las respuestas?
       Límite: p99 ≤ 3 × p50
       Duración: instantáneo (usa CT-01 y CT-02)

CT-04: ¿Mantiene rendimiento con 10 usuarios simultáneos?
       Límite: p95 aumenta máximo 30%, errores ≤ 1%
       Duración: ~6 min

CT-05: ¿Es el rendimiento consistente en el tiempo?
       Límite: variación ≤ 20% entre ejecuciones
       Duración: ~15-20 min (3 ejecuciones)
```

---

## 🎯 Casos de uso comunes

### Establecer línea base inicial

```bash
# Día 1
python run_performance_tests.py

# Día 2 (frananja diferente)
python run_performance_tests.py

# Día 3 (hora diferente)
python run_performance_tests.py

# Comparar los 3 resultados (variación debe ser ≤ 20%)
```

### Monitoreo semanal

```bash
# Ejecuta semanalmente
python run_performance_tests.py

# Compara con línea base anterior
# Si p95 aumentó > 20%, investigar
```

### Evaluar escalabilidad

```bash
# Ejecuta CT-04 con carga moderada
python run_performance_tests.py --ct-04 --users 10 --duration 300

# Si p95 aumenta > 30%, la API no escala bien
```

### Verificar antes de deploy

```bash
# Ejecuta CT-01, CT-02, CT-03 rápidamente
python run_performance_tests.py

# Debe pasar todos los criterios
# Archivo: test_results_BASELINE_*.json
```

---

## 📈 Interpretar resultados en 5 pasos

1. **Abre el archivo JSON:**
   ```bash
   cat test_results_BASELINE_*.json
   ```

2. **Busca "verdict": "PASS" o "FAIL":**
   - PASS ✓ = Criterio cumplido
   - FAIL ✗ = Criterio no cumplido

3. **Si hay FAIL, revisa la métrica:**
   - CT-01 FAIL → p50 o p95 superiores al límite
   - CT-02 FAIL → p95 o p99 superiores al límite
   - CT-04 FAIL → p95 aumentó > 30% o errores > 1%

4. **Compara con ejecución anterior:**
   - Mismo día: diferencia esperada ≤ 5%
   - Días distintos: diferencia esperada ≤ 20%
   - Si diferencia > 20%: investigar cambios

5. **Decide acción:**
   - Todos PASS → continuar monitoreo normal
   - Algunos FAIL → investigar causa
   - FAIL nuevo vs PASS anterior → degradación detectada

---

## ⚙️ Personalizar pruebas

### Cambiar número de solicitudes

```bash
# 500 solicitudes por prueba (demora más)
python run_performance_tests.py --requests 500

# 100 solicitudes (rápido pero menos preciso)
python run_performance_tests.py --requests 100
```

### Cambiar parámetros de concurrencia

```bash
# 20 usuarios durante 10 minutos
python run_performance_tests.py --ct-04 --users 20 --duration 600

# 5 usuarios durante 2 minutos (rápido)
python run_performance_tests.py --ct-04 --users 5 --duration 120
```

### Cambiar frecuencia de repetibilidad

```bash
# 5 ejecuciones con 1 minuto entre ellas
python run_performance_tests.py --ct-05 --exec 5 --interval 60

# 2 ejecuciones (rápido)
python run_performance_tests.py --ct-05 --exec 2 --interval 300
```

---

## 🔍 Troubleshooting

### "ONVO_TEST_SECRET_KEY no está configurada"

```bash
# Ejecuta configurador
python configurar_clave.py

# Verifica que se creó .env
cat .env
```

### "Error: Cannot connect to API"

```bash
# Verifica conectividad
curl https://api.onvopay.com/v1/customers -H "Authorization: Bearer YOUR_KEY"

# Verifica llave en Dashboard de ONVO
# Llave debe empezar con: onvo_test_secret_key_
```

### "Muchos timeouts (> 10 segundos)"

1. Revisa tu conexión de red
2. Intenta desde otra máquina
3. Contacta a ONVO si es persistente

### "p95 siempre > 800ms"

1. Normal si estás lejos del servidor ONVO
2. Incluye latencia de red
3. Compara con ejecución anterior

---

## 📚 Referencias rápidas

### Métricas (en milisegundos)

```
p50  = Percentil 50 = Mediana = tiempo típico
p95  = Percentil 95 = 95% de solicitudes responden en este tiempo
p99  = Percentil 99 = 99% de solicitudes responden en este tiempo
stdev = Desviación estándar = variabilidad
```

### Umbrales por criterio

```
CT-01 (Lectura):     p50 ≤ 400ms,  p95 ≤ 800ms
CT-02 (Escritura):   p95 ≤ 1500ms, p99 ≤ 2500ms
CT-03 (Estabilidad): p99 ≤ 3 × p50
CT-04 (Concurrencia): p95 ≤ +30%,  errores ≤ 1%
CT-05 (Repetibilidad): variación ≤ 20%
```

---

## 🎓 Aprende más

| Tema | Referencia |
|------|-----------|
| **Percentiles** | [PERFORMANCE_TESTS_README.md](./PERFORMANCE_TESTS_README.md#faq) |
| **ISO/IEC 25010** | [TEST_DOCUMENTATION.md](./TEST_DOCUMENTATION.md#marcocoteórico) |
| **API ONVO** | https://docs.onvopay.com/api |
| **Interpretación** | [PERFORMANCE_TESTS_README.md](./PERFORMANCE_TESTS_README.md#interpretación-de-resultados) |

---

## 📝 Hoja de trucos

```bash
# Ejecutar solo CT-01 (lectura)
python run_performance_tests.py --ct-01

# Ejecutar solo CT-02 (escritura)
python run_performance_tests.py --ct-02

# Ejecutar solo CT-04 (concurrencia)
python run_performance_tests.py --ct-04

# Ver ayuda completa
python run_performance_tests.py --help

# Ejecutar con 50 solicitudes (rápido)
python run_performance_tests.py --requests 50

# Ejecutar CT-05 con solo 2 ejecuciones
python run_performance_tests.py --ct-05 --exec 2
```

---

**Versión:** 1.0  
**Última actualización:** 2024-11-25  
**Estado:** Listo para usar
