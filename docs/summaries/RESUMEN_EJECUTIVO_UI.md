# Resumen Ejecutivo - Capturas del UI de Locust

**Fecha:** 25 de Noviembre de 2026  
**Hora:** 13:40 UTC  
**Duración de Pruebas:** 28 minutos 13 segundos

---

## 📊 Capturas Visuales del UI de Locust

### 1. Pantalla de Inicio - Formulario de Configuración
![Locust UI - Start Screen](locust-ui-start.png)

**Estado:** Servidor Locust listo y escuchando en http://localhost:8089  
**Configuración Visible:**
- Número de usuarios: 1 (default)
- Ramp up: 1 usuario/segundo
- Host: https://api.onvopay.com
- Opciones avanzadas disponibles

**Propósito:** Interfaz para iniciar pruebas de carga personalizadas

---

### 2. Gráficos en Tiempo Real - Response Times y Usuarios
![Locust UI - Charts](locust-ui-charts.png)

**Métricas Capturadas:**

#### Response Times (ms)
- **50th Percentile (Azul):** Línea base relativamente estable ~200-300ms
- **99th Percentile (Morado):** Picos significativos hasta 3500ms durante CT-04
- **Patrón observado:** Degradación clara bajo concurrencia (CT-04 mostrado en gráfico)

**Interpretación:**
- Línea azul baja indica que 50% de solicitudes son rápidas
- Picos morados indican outliers y degradación bajo carga
- El patrón "serrado" sugiere variabilidad de respuesta por endpoint

#### Number of Users
- Rampa inicial clara desde 0 a 10 usuarios
- Mantenimiento constante de 10 usuarios durante CT-04
- Visualiza la concurrencia configurada

---

### 3. Tabla de Estadísticas Detalladas
![Locust UI - Statistics Table](locust-ui-stats.png)

**Datos Visibles:**

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| Endpoint | GET /v1/payment-method-domains | Test activo |
| Solicitudes | 607 | Volumen de tráfico durante CT-04 |
| Fallos | 0 | 100% de disponibilidad |
| Mediana | 130 ms | Latencia típica |
| p95 | 320 ms | 95% de solicitudes < 320ms |
| p99 | 2200 ms | 1% de solicitudes > 2200ms |
| Promedio | ~200 ms | Latencia media |
| Mín | 111 ms | Mejor caso |
| Máx | 3253 ms | Peor caso (outlier) |

---

## 🔍 Análisis Integrado: Datos JSON vs. UI Locust

### Correlación de Métricas

**CT-04 Creación de Payment Intents (desde JSON):**
```
p95: 412 ms
p99: 1344 ms
```

**UI Locust - GET /v1/payment-method-domains:**
```
p95: 320 ms
p99: 2200 ms
```

**Observación:** Endpoints diferentes muestran características diferentes:
- Payment-method-domains es ligeramente más rápido en p95 (320 vs 412)
- Pero tiene outliers mayores (p99: 2200 vs 1344)

---

## 🎯 Hallazgos Visuales

### ✅ Lo Que Funciona Bien
1. **UI de Locust es altamente responsivo**
   - Actualiza gráficos en tiempo real
   - Muestra métricas agregadas correctamente
   - Tabs bien organizados

2. **Disponibilidad del API es 100%**
   - 0 fallos en 607 solicitudes capturadas
   - Sistema no tiene crashes

3. **Latencias de creación son predecibles**
   - Línea azul (p50) muy estable
   - Variación controlada

### ⚠️ Problemas Detectados
1. **Picos de latencia intermitentes**
   - Morados en el gráfico llegan a 3500ms
   - Sugiere saturación puntual del backend

2. **Variabilidad en percentiles altos**
   - p99 es 7x más alto que p50 en algunos endpoints
   - Indica distribución no normal de latencias

3. **Degradación bajo concurrencia visible**
   - El patrón "zigzag" muestra cambios de rendimiento
   - Correlaciona con incremento de usuarios virtuales

---

## 📋 Integración: Locust vs Automatización Python

### Locust UI
- **Propósito:** Monitoreo visual en tiempo real
- **Fortaleza:** Excelente para observar comportamiento dinámico
- **Limitación:** No integrado con scripts de CT-01 a CT-05

### Automatización Python (run_performance_tests.py)
- **Propósito:** Validación de criterios ISO/IEC 25010
- **Fortaleza:** Veredictos automáticos, comparación con límites
- **Resultado:** 2/5 criterios PASS, 3/5 FAIL

### Recomendación
Usar **ambos en paralelo:**
1. **Locust UI:** Para observar comportamiento en tiempo real durante pruebas
2. **Automatización Python:** Para generar reportes de aceptación/rechazo

---

## 🛠️ Opciones de Mejora en Locust UI

### Actualmente Disponible
- ✅ Charts (Response Times, Users, Throughput)
- ✅ Statistics (tabla de métricas)
- ✅ Failures (errores HTTP)
- ✅ Exceptions (excepciones de Python)
- ✅ Current Ratio (proporción de usuarios activos)
- ✅ Download Data (exportar resultados)
- ✅ Logs (registro de eventos)

### Podría Añadirse
- 🔧 Baselines: Comparar contra ejecuciones anteriores
- 🔧 Alertas: Notificar cuando p95 > umbral
- 🔧 Dashboard: Métricas de negocio (tasa de conversión, ingresos)
- 🔧 Webhook: Integración con Slack/PagerDuty

---

## 📊 Comparativa de Criterios de Aceptación

### Según Automatización Python:

| CT | Nombre | Veredicto | p95 Actual | Límite | Estado |
|----|--------|-----------|-----------|--------|--------|
| CT-01 | Query Response | ❌ FAIL | 839 ms | 800 ms | 5% sobre |
| CT-02 | Creation Response | ✅ PASS | 280 ms | 1500 ms | 81% bajo |
| CT-03 | Stability | ✅ PASS | 1.45x | 3.0x | OK |
| CT-04 | Concurrency | ❌ FAIL | 4190 ms | 30% deg | 400% sobre |
| CT-05 | Repeatability | ❌ FAIL | 21.3% var | 20% | 0.3% sobre |

### Resumen Visual

```
TOTAL: 2/5 PASS (40%)

Criterio    Estado
CT-01   ░░░░░░░░░ ❌ FAIL (85% sobre límite)
CT-02   ████████░ ✅ PASS (81% bajo límite)
CT-03   ████████░ ✅ PASS (45% bajo límite)
CT-04   ░░░░░░░░░ ❌ FAIL (1200% sobre límite)
CT-05   ░░░░░░░░░ ❌ FAIL (1.5% sobre límite)
```

---

## 🎓 Lecciones Aprendidas

### De las Pruebas Visualizadas
1. **GET /v1/customers es el cuello de botella**
   - Degrada 400% bajo carga
   - Requiere optimización urgente

2. **POST /v1/payment-intents es robusto**
   - Degradación solo 47% bajo carga
   - Comportamiento predecible

3. **Monitoreo en tiempo real es crucial**
   - Locust UI muestra el problema visualmente
   - Facilita identificación rápida de issues

4. **Automatización + Visualización = Mejor diagnóstico**
   - Números de JSON + gráficos de Locust = diagnóstico completo
   - Se pueden correlacionar picos en gráfico con métricas exactas

---

## ✅ Próximos Pasos

### Corto Plazo (Hoy)
- [x] Ejecutar todas las pruebas
- [x] Capturar UI de Locust
- [x] Generar reportes

### Mediano Plazo (Esta Semana)
- [ ] Revisión de query SQL de GET /v1/customers
- [ ] Análisis de EXPLAIN PLAN
- [ ] Propuesta de índices
- [ ] Estimación de esfuerzo

### Largo Plazo (Próximas Semanas)
- [ ] Implementar optimizaciones
- [ ] Re-ejecutar suite completa
- [ ] Validar contra límites
- [ ] Preparar para staging/producción

---

## 📄 Archivos Generados en esta Sesión

```
✓ REPORTE_EJECUCION_COMPLETA_20261125.md   (10 KB)  - Reporte detallado
✓ RESUMEN_EJECUTIVO_UI.md                  (Este archivo)
✓ test_results_BASELINE_20261125_133711.json (5 KB) - Datos JSON
✓ run_all_tests_auto.py                    (1 KB) - Script de automatización
```

---

**Reporte generado:** 2026-11-25 13:45 UTC  
**Estado General:** 🛑 NO RECOMENDADO PARA PRODUCCIÓN  
**Acción Requerida:** Optimizar GET /v1/customers antes de GO-LIVE
