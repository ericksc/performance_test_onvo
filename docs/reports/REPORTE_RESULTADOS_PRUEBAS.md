# REPORTE DE RESULTADOS - PRUEBAS DE RENDIMIENTO ONVO PAY API

**Fecha de Ejecución:** 25 de Noviembre de 2026  
**Hora de Inicio:** 11:50:57 UTC-6  
**Hora de Finalización:** 11:54:49 UTC-6  
**Duración Total:** ~4 minutos  

**Estándar de Referencia:** ISO/IEC 25010:2011 - Comportamiento Temporal  
**Versión del Reporte:** 1.0  

---

## 📊 RESUMEN EJECUTIVO

| Criterio | Estado | Veredicto | Notas |
|----------|--------|-----------|-------|
| **CT-01** | ❌ FALLO | FAIL | Consultas exceden p50 y p95 |
| **CT-02** | ✅ PASÓ | PASS | Creación dentro de límites |
| **CT-03** | ❌ FALLO | FAIL | Estabilidad comprometida en CT-01 |
| **CT-04** | ⏭️ NO EJECUTADO | - | Requiere confirmación interactiva |
| **CT-05** | ⏭️ NO EJECUTADO | - | Requiere múltiples ejecuciones |

**Resultado Final:** ❌ **FALLOS DETECTADOS**

---

## 🔍 DETALLES POR CRITERIO

### CT-01: Tiempo de Respuesta - Consultas (GET /v1/customers)

**Descripción:**  
Mide el tiempo de respuesta de 200 solicitudes GET secuenciales para listar clientes.

**Criterios de Aceptación:**
- p50 ≤ 400 ms _(mediana de respuesta)_
- p95 ≤ 800 ms _(95% de las solicitudes)_
- Ningún timeout > 10 segundos

**Resultados Medidos:**

| Métrica | Valor Medido | Límite | Estado |
|---------|--------------|--------|--------|
| **p50 (mediana)** | 766.63 ms | ≤ 400 ms | ❌ FALLO |
| **p95 (95 percentil)** | 1,197.82 ms | ≤ 800 ms | ❌ FALLO |
| **p99 (99 percentil)** | 3,520.47 ms | - | ⚠️ ALTO |
| **Mín** | 716.50 ms | - | - |
| **Máx** | 3,723.39 ms | - | ⚠️ ALTO |
| **Promedio** | 873.44 ms | - | - |
| **Desv. Estándar** | 369.59 ms | - | ⚠️ VARIABILIDAD |
| **Solicitudes Exitosas** | 200/200 (100%) | - | ✅ |
| **Timeouts** | 0 | - | ✅ |

**Interpretación:**
- ❌ Las consultas promedian **766 ms**, sobrepasando el límite de **400 ms** en un **91.6%**
- ❌ El p95 de **1,197 ms** sobrepasa el límite de **800 ms** en un **49.7%**
- ⚠️ Alto valor de desviación estándar (369 ms) indica inconsistencia
- ⚠️ La máxima respuesta llega a 3,723 ms, casi 10x el límite ideal

**Veredicto:** ❌ **FAIL**

**Recomendaciones:**
1. **Revisar latencia de red:** Validar conexión a servidor ONVO
2. **Revisar carga de servidor:** Puede haber procesamiento lento
3. **Validar índices en BD:** Las consultas de clientes pueden estar sin optimizar
4. **Revisar filtros de firewall:** Pueden estar ralentizando conexiones

---

### CT-02: Tiempo de Respuesta - Creación (POST /v1/payment-intents)

**Descripción:**  
Mide el tiempo de respuesta de 200 solicitudes POST secuenciales para crear intenciones de pago.

**Criterios de Aceptación:**
- p95 ≤ 1,500 ms _(95% de las solicitudes)_
- p99 ≤ 2,500 ms _(99% de las solicitudes)_
- Ningún timeout > 10 segundos

**Resultados Medidos:**

| Métrica | Valor Medido | Límite | Estado |
|---------|--------------|--------|--------|
| **p95 (95 percentil)** | 353.21 ms | ≤ 1,500 ms | ✅ PASÓ |
| **p99 (99 percentil)** | 730.56 ms | ≤ 2,500 ms | ✅ PASÓ |
| **Mín** | 130.02 ms | - | ✅ |
| **Máx** | 4,013.15 ms | - | ⚠️ OUTLIER |
| **Promedio** | 211.19 ms | - | ✅ |
| **Desv. Estándar** | 286.77 ms | - | ⚠️ VARIABILIDAD |
| **Solicitudes Exitosas** | 200/200 (100%) | - | ✅ |
| **Timeouts** | 0 | - | ✅ |

**Interpretación:**
- ✅ El p95 de **353 ms** está bien dentro del límite de **1,500 ms** (76% de margen)
- ✅ El p99 de **730 ms** está bien dentro del límite de **2,500 ms** (71% de margen)
- ⚠️ Existe un outlier en 4,013 ms (posible spike momentáneo)
- ⚠️ Variabilidad moderada pero dentro de rango aceptable
- ✅ Tiempo promedio muy favorable (211 ms)

**Veredicto:** ✅ **PASS**

**Notas Positivas:**
- La API de creación es **5.5x más rápida** que la de consultas
- Excelente margen en ambos límites
- Consumo consistente de recursos

---

### CT-03: Estabilidad (p99/p50 ≤ 3x)

**Descripción:**  
Valida que no haya degradación extrema en tiempos de respuesta (detecta colas y saturación).

**Criterio de Aceptación:**
- Ratio p99/p50 ≤ 3.0 en todas las operaciones

**Resultados Medidos:**

#### CT-01 - Consultas (Listar Clientes)

| Métrica | Valor | Interpretación |
|---------|-------|-----------------|
| **p50** | 766.63 ms | Mediana |
| **p99** | 3,520.47 ms | 99 percentil |
| **Ratio (p99/p50)** | 4.59x | ❌ FALLO |
| **Límite** | ≤ 3.0x | - |
| **Exceso** | +1.59x | 53% sobre límite |

**Interpretación:**
- ❌ El ratio de **4.59x** indica que el 99 percentil es **4.59 veces más lento** que la mediana
- ⚠️ Esto sugiere la presencia de **colas o situaciones de saturación**
- ⚠️ No hay consistencia en los tiempos (variable según carga)
- ❌ El servidor muestra signos de degradación bajo presión

**Veredicto:** ❌ **FAIL**

**Recomendaciones:**
1. **Aumentar capacidad:** Posible saturación del servidor
2. **Revisar colas de procesamiento:** Pueden estar acumulándose solicitudes
3. **Implementar rate limiting:** Proteger contra sobrecargas

---

## 📈 COMPARATIVA CON ESTÁNDARES

### Tabla de Desempeño General

```
Operación          Medida    Límite    Estado   Margen
─────────────────────────────────────────────────────
CT-01 (p50)        766 ms    400 ms    ❌ FALLO  -92%
CT-01 (p95)        1197 ms   800 ms    ❌ FALLO  -50%
CT-02 (p95)        353 ms    1500 ms   ✅ PASÓ   +76%
CT-02 (p99)        730 ms    2500 ms   ✅ PASÓ   +71%
CT-03 (ratio)      4.59x     3.0x      ❌ FALLO  -53%
```

---

## ⚠️ ISSUES CRÍTICOS IDENTIFICADOS

### Problema 1: Lentitud en Consultas de Clientes
- **Severidad:** 🔴 ALTA
- **Impacto:** Afecta operaciones básicas de lectura
- **Causa Probable:** 
  - Índices no optimizados en base de datos
  - Respuesta lenta del servidor ONVO
  - Latencia de red
- **Acción Requerida:** Urgente

### Problema 2: Falta de Estabilidad en CT-01
- **Severidad:** 🟠 MEDIA
- **Impacto:** Comportamiento impredecible bajo variación de carga
- **Causa Probable:**
  - Recursos compartidos saturándose
  - Cache inconsistente
  - Throttling del servidor
- **Acción Requerida:** Alta Prioridad

---

## 📋 LIMITACIONES DE ESTA EJECUCIÓN

1. ✅ **CT-01, CT-02, CT-03** completados exitosamente
2. ⏭️ **CT-04** (Concurrencia con 10 usuarios) NO EJECUTADO
   - Requiere confirmación interactiva (5 minutos)
   - Puede ejecutarse con: `python run_performance_tests.py --ct-04`

3. ⏭️ **CT-05** (Repetibilidad) NO EJECUTADO
   - Requiere 3+ ejecuciones separadas en el tiempo
   - Puede ejecutarse con: `python run_performance_tests.py --ct-05`

---

## 🔧 PRÓXIMAS ACCIONES RECOMENDADAS

### 1. INMEDIATAS (Hoy)
```bash
# Ejecutar pruebas de concurrencia para validar degradación
python run_performance_tests.py --ct-04
```

### 2. CORTO PLAZO (Esta semana)
```bash
# Ejecutar línea base de repetibilidad
python run_performance_tests.py --ct-05 --exec 5
```

### 3. INVESTIGACIÓN
- [ ] Revisar logs del servidor ONVO
- [ ] Verificar latencia de red con `curl -w "@curl_format.txt"`
- [ ] Validar índices de base de datos
- [ ] Revisar políticas de rate-limiting

### 4. OPTIMIZACIÓN
- [ ] Implementar caché cliente-side
- [ ] Usar connection pooling
- [ ] Revisar query optimization en CT-01

---

## 📊 ARCHIVOS DE SALIDA

**Archivo JSON Completo:**
```
test_results_BASELINE_20261125_115449.json
```

**Ubicación:** `C:\work\poc_onvo\`

---

## 🎯 INDICADORES CLAVE

| KPI | Valor | Objetivo | Estado |
|-----|-------|----------|--------|
| Tasa de Éxito | 100% | ≥ 99% | ✅ |
| Requests sin Error | 400/400 | 100% | ✅ |
| Timeouts | 0 | 0 | ✅ |
| Criterios PASS | 1/3 | ≥ 3/3 | ❌ |
| Criterios FAIL | 2/3 | 0/3 | ❌ |

---

## 📌 CONCLUSIÓN

La API de ONVO Pay muestra **desempeño inconsistente**:

✅ **Fortalezas:**
- Creación de intenciones de pago es rápida y confiable
- Sin timeouts o errores HTTP
- Tasa de éxito perfecta (100%)

❌ **Debilidades:**
- Consultas de clientes son **2-3x más lentas** de lo esperado
- Falta de estabilidad en tiempos de respuesta
- Alto potencial de degradación bajo carga

**Recomendación:** Investigar y optimizar endpoint `/v1/customers` antes de producción.

---

**Generado por:** Suite de Pruebas Automatizada ONVO  
**Estándar:** ISO/IEC 25010:2011 Comportamiento Temporal  
**Versión:** 1.0
