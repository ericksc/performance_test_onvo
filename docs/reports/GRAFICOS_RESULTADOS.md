# Gráficos de Resultados - Pruebas de Rendimiento ONVO Pay

**Fecha:** 25 de Noviembre de 2026  
**Hora:** 13:40 UTC  
**Status:** ✓ Gráficos generados exitosamente

---

## Resumen Visual de Resultados

Se han generado **4 gráficos principales** que visualizan los resultados de las pruebas de rendimiento (CT-01 a CT-05).

---

## Gráfico 1: Resultados de Criterios de Aceptación

**Archivo:** `graficos/01_resultados_criterios.png`

### Descripción
Gráfico de barras horizontales mostrando el veredicto PASS/FAIL de cada criterio.

### Hallazgos Clave
```
CT-01  [FAIL]  ❌ - Tiempo de respuesta consultas
CT-02  [PASS]  ✓  - Tiempo de respuesta creación
CT-03  [PASS]  ✓  - Estabilidad (p99/p50)
CT-04  [FAIL]  ❌ - Concurrencia moderada
CT-05  [FAIL]  ❌ - Repetibilidad

TOTAL: 2/5 PASS (40%)
```

### Visual
- **Barras Verdes:** Criterios PASS (CT-02, CT-03)
- **Barras Rojas:** Criterios FAIL (CT-01, CT-04, CT-05)

---

## Gráfico 2: Comparativa de Latencias (CT-01 vs CT-02)

**Archivo:** `graficos/02_latencias_ct01_ct02.png`

### Descripción
Dos gráficos de barras lado a lado comparando latencias de los dos endpoints principales.

### CT-01: GET /v1/customers (IZQUIERDA)

**Métricas:**
- p50:   739 ms (límite: 400 ms) ❌ **85% SOBRE**
- p95:   839 ms (límite: 800 ms) ❌ **5% SOBRE**
- p99: 1073 ms

**Visual:**
- Línea roja (límite p50 = 400ms)
- Línea naranja (límite p95 = 800ms)
- Las barras azules SUPERAN ambos límites

**Conclusión:** Latencias base inaceptables

### CT-02: POST /v1/payment-intents (DERECHA)

**Métricas:**
- p95:  280 ms (límite: 1500 ms) ✓ **81% BAJO**
- p99:  735 ms (límite: 2500 ms) ✓ **71% BAJO**

**Visual:**
- Línea naranja (límite p95 = 1500ms)
- Línea roja (límite p99 = 2500ms)
- Las barras verdes están BAJO ambos límites

**Conclusión:** Latencias excelentes

### Comparación Directa
```
POST es 2.7x MÁS RÁPIDO que GET

GET p95:  839 ms
POST p95: 280 ms
Diferencia: 559 ms (3x más lento)
```

**Implicación:** Problema específico en endpoint de consultas, no en la API en general.

---

## Gráfico 3: Degradación bajo Concurrencia (CT-04)

**Archivo:** `graficos/03_degradacion_ct04.png`

### Descripción
Dos gráficos comparando latencia BASELINE vs BAJO CARGA (10 usuarios virtuales).

### CT-04: GET /v1/customers (IZQUIERDA)

**Degradación Observada:**
```
Baseline (sin carga):     839 ms
Bajo carga (10 usuarios): 4190 ms

Degradación: 399.6% (límite: 30%)
```

**Visual:**
- Barra verde (Baseline): Pequeña, ~839 ms
- Barra roja (Bajo carga): ENORME, ~4190 ms
- Línea naranja punteada: Límite de 30% degradación (1091 ms)
- La barra roja ESTÁ 4x POR ENCIMA del límite permitido

**Estado:** 🔴 CRÍTICO

**Interpretación:**
- Sistema COLAPSA bajo carga moderada
- 10 usuarios virtuales hace que latencias se multipliquen por 5x
- NO es viable en producción

### CT-04: POST /v1/payment-intents (DERECHA)

**Degradación Observada:**
```
Baseline (sin carga):     280 ms
Bajo carga (10 usuarios): 412 ms

Degradación: 47% (límite: 30%)
```

**Visual:**
- Barra verde (Baseline): ~280 ms
- Barra naranja (Bajo carga): ~412 ms (apenas sobre límite)
- Línea roja punteada: Límite de 30% degradación (364 ms)
- La barra naranja está ligeramente por encima

**Estado:** 🟠 MARGINAL (apenas falla)

**Interpretación:**
- Creación de payment intents es más robusto
- Degrada menos bajo carga
- Apenas 17% por encima del límite

### Hallazgo Principal

**GET se degrada 8.5x más que POST bajo carga:**
- GET: 399.6% degradación
- POST: 47% degradación

Esto confirma un problema arquitectónico específico en el endpoint de consultas.

---

## Gráfico 4: Variabilidad en Repetibilidad (CT-05)

**Archivo:** `graficos/04_varianza_ct05.png`

### Descripción
Dos gráficos de líneas mostrando latencias en 3 ejecuciones sucesivas (con 300s intervalo).

### CT-05: GET /v1/customers (IZQUIERDA)

**Valores p95 por ejecución:**
```
Ejecución 1: 994.89 ms
Ejecución 2: 817.30 ms  (mejora)
Ejecución 3: 877.63 ms  (sube un poco)

Varianza: 13.4% (límite: 20%)
```

**Visual:**
- Línea azul con puntos en cada ejecución
- Línea roja punteada: Media (~897 ms)
- Área sombreada: Rango de desviación estándar
- La línea está DENTRO de la zona sombreada

**Estado:** ✓ PASS (bien dentro del límite)

**Interpretación:**
- Comportamiento relativamente consistente
- Mejora en ejecución 2 (posible warmup)
- Variabilidad controlada

### CT-05: POST /v1/payment-intents (DERECHA)

**Valores p95 por ejecución:**
```
Ejecución 1: 288.50 ms
Ejecución 2: 237.27 ms  (mejora significativa)
Ejecución 3: 237.78 ms  (se estabiliza)

Varianza: 21.3% (límite: 20%)
```

**Visual:**
- Línea verde con cuadrados en cada ejecución
- Línea roja punteada: Media (~254 ms)
- Área sombreada: Rango de desviación
- La línea está en el BORDE de la zona sombreada

**Status:** ❌ FAIL (apenas 0.3% sobre límite)

**Interpretación:**
- Caída significativa en ejecución 2 (warmup de caché?)
- Luego se estabiliza en ejecución 3
- Primera ejecución es 22% más lenta que las subsecuentes
- Comportamiento predecible pero con variabilidad

**Causa Probable:** Inicialización de recursos, warmup de caché, o garbage collection en primera ejecución.

---

## Análisis Integrado

### Conclusiones Principales

1. **El problema es en GET /v1/customers, no en la API en general**
   - POST es 2.7x más rápido
   - POST degradación 47% vs GET 400%
   - POST varianza 21% vs GET 13%

2. **GET /v1/customers es el cuello de botella crítico**
   - Latencia base 85% sobre límite (739ms vs 400ms)
   - Degrada 400% bajo carga (límite 30%)
   - Sistema inutilizable con 10+ usuarios concurrentes

3. **POST /v1/payment-intents funciona bien**
   - Latencias excelentes (CT-02 PASS)
   - Degradación marginal bajo carga (CT-04 FAIL por 17%)
   - Variabilidad apenas sobre límite (CT-05 FAIL por 0.3%)

4. **La arquitectura backend necesita optimización urgente**
   - Índices de base de datos ineficientes (probable)
   - Falta de caché
   - Queries N+1 no optimizadas
   - Pool de conexiones limitado

---

## Recomendaciones por Gráfico

### De Gráfico 1 (Resultados Generales)
- 🛑 NO RECOMENDADO PARA PRODUCCIÓN
- Requiere correcciones antes de GO-LIVE
- Prioridad: Resolver 3 criterios FAIL

### De Gráfico 2 (Latencias)
- 🔴 CRÍTICO: GET /v1/customers está lejos del límite
- ✓ BUENO: POST /v1/payment-intents bien optimizado
- Acción: Investigar diferencias arquitectónicas entre endpoints

### De Gráfico 3 (Degradación)
- 🔴 CRÍTICO: GET degrada 400% bajo carga
- Acción: Inmediata - optimizar índices DB
- Acción: Implementar caché para consultas de clientes
- Acción: Revisar query SQL con EXPLAIN PLAN

### De Gráfico 4 (Varianza)
- GET: Comportamiento estable ✓
- POST: Comportamiento con warmup (mejora en ejecución 2)
- Acción: Implementar warmup en startup de aplicación

---

## Próximos Pasos

### Inmediato (Hoy)
1. Revisar query SQL de GET /v1/customers
2. Ejecutar EXPLAIN PLAN
3. Identificar índices faltantes

### Esta Semana
1. Crear índices recomendados
2. Implementar caché (Redis/Memcached)
3. Re-ejecutar CT-01 y CT-04

### Próxima Semana
1. Validar mejoras
2. Re-ejecutar suite completa
3. Comparar gráficos (antes vs después)

---

## Generación de Gráficos

**Script usado:** `generate_charts.py`  
**Fecha de generación:** 2026-11-25 13:50 UTC  
**Formato:** PNG (150 dpi)  
**Librería:** matplotlib

---

## Importancia de los Gráficos

Estos gráficos **demuestran visualmente** lo que los números en JSON nos decían:

```
JSON datos numéricos     →    Gráficos visuales
  (abstracto)                  (concreto)
   
739 ms p50           →  Barra grande SOBRE línea roja
399.6% degradación   →  Barra gigante ROJA vs pequeña verde
21.3% varianza       →  Línea apenas en BORDE de zona sombreada
```

Los gráficos facilitan:
- ✓ Comunicación a stakeholders
- ✓ Identificación rápida de problemas
- ✓ Priorización de acciones
- ✓ Comparación antes/después de optimizaciones

---

**Estado:** 🎉 Captura gráfica completada  
**Archivos:** 4 gráficos PNG en carpeta `graficos/`  
**Listo para:** Presentación a stakeholders y equipo de desarrollo
