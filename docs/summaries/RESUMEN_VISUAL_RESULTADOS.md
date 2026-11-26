# 📊 RESUMEN VISUAL - RESULTADOS DE PRUEBAS

**Fecha:** 25 de Noviembre 2026 | **Duración:** 4 minutos | **Total Requests:** 400

---

## ✅ SCORECARD - ESTADO GENERAL

```
╔═══════════════════════════════════════════════════╗
║                                                   ║
║          SUITE DE PRUEBAS DE RENDIMIENTO          ║
║          ISO/IEC 25010:2011 (Temporal)            ║
║                                                   ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  Criterios Ejecutados: 3 de 5                     ║
║  ├─ CT-01: ❌ FAIL                                ║
║  ├─ CT-02: ✅ PASS                                ║
║  ├─ CT-03: ❌ FAIL                                ║
║  ├─ CT-04: ⏳ PENDIENTE                            ║
║  └─ CT-05: ⏳ PENDIENTE                            ║
║                                                   ║
║  Resultado: ❌ FALLOS DETECTADOS (2 de 3)        ║
║  Tasa de Éxito: 33% (1/3 criterios)               ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

---

## 📈 COMPARACIÓN VISUAL: MEDICIONES vs LÍMITES

### CT-01: Consultas (Listar Clientes)

**p50 - Mediana de Respuesta:**
```
Límite:        |████| 400 ms
Medido:        |██████████████████| 766.63 ms
                             ▲ 92% sobre límite ❌
```

**p95 - 95 Percentil:**
```
Límite:        |████████| 800 ms
Medido:        |██████████████████████| 1,197.82 ms
                                      ▲ 50% sobre límite ❌
```

**p99 - 99 Percentil:**
```
Límite:        (no especificado)
Medido:        |██████████████████████████████████| 3,520.47 ms
                                                   ▲ Muy alto ⚠️
```

**Desviación Estándar:**
```
Estabilidad:   |████████████| 369.59 ms
                              ▲ Variabilidad moderada-alta ⚠️
```

---

### CT-02: Creación (Payment Intents)

**p95 - 95 Percentil:**
```
Límite:        |██████████████████| 1,500 ms
Medido:        |███████| 353.21 ms
               ▲ 76% de margen ✅ EXCELENTE
```

**p99 - 99 Percentil:**
```
Límite:        |██████████████████████████| 2,500 ms
Medido:        |███████████| 730.56 ms
               ▲ 71% de margen ✅ EXCELENTE
```

**Promedio:**
```
Límite:        (no especificado)
Medido:        |██| 211.19 ms
               ▲ Muy rápido ✅
```

---

### CT-03: Estabilidad (Ratio p99/p50)

**CT-01 - Consultas:**
```
Límite:        |███| 3.0x
Medido:        |████████| 4.59x
                      ▲ 53% sobre límite ❌
```

**Interpretación del Ratio:**
```
Ratio = 1.0x  → Respuestas perfectamente consistentes (Ideal)
Ratio = 2.0x  → Variabilidad moderada (Aceptable)
Ratio = 3.0x  → Límite máximo tolerable
Ratio = 4.59x → ❌ Degradación severa con colas/saturación
```

---

## 🎯 DISTRIBUCIÓN DE TIEMPOS (Visualización)

### CT-01: Consultas
```
      Frecuencia
        ▁▂▃▄▅
    0 ms        3,500 ms
    ├────────────────────┤
    │                    │
    │ p50:  766 ms │
    │ p95: 1197 ms │
    │ p99: 3520 ms │ ← Largo tail de outliers
    │               │
    └────────────────────┘
    Patrón: Distribución asimétrica con cola derecha
```

### CT-02: Creación
```
      Frecuencia
       ▅▄▃▂▁
    0 ms        4,000 ms
    ├────────────────────┤
    │ ▓▓▓▓▓▓▓▓▓▓▓▓▓     │
    │ p50:  158 ms       │
    │ p95:  353 ms       │
    │ p99:  730 ms       │
    │                    │ ← Pocos outliers
    └────────────────────┘
    Patrón: Distribución más normal, concentrada a la izquierda
```

---

## 📊 TABLA COMPARATIVA: CT-01 vs CT-02

```
┌──────────────┬───────────┬───────────┬────────────────┐
│   Métrica    │  CT-01    │  CT-02    │  Diferencia    │
├──────────────┼───────────┼───────────┼────────────────┤
│ p50/Mediana  │  766 ms   │  158 ms   │  4.9x más rápido
│ p95          │ 1197 ms   │  353 ms   │  3.4x más rápido
│ p99          │ 3520 ms   │  730 ms   │  4.8x más rápido
│ Promedio     │  873 ms   │  211 ms   │  4.1x más rápido
│ Desv. Estd.  │  369 ms   │  286 ms   │  Ambas variables
│ Min          │  716 ms   │  130 ms   │  5.5x más rápido
│ Max          │ 3723 ms   │ 4013 ms   │  CT-02 tiene 1 outlier
└──────────────┴───────────┴───────────┴────────────────┘

Conclusión: CT-02 (Crear) es MUCHO más eficiente que CT-01 (Listar)
```

---

## 🔴 PROBLEMAS CRÍTICOS (Heatmap de Severidad)

```
┌─────────────────────────────────────────┐
│          MATRIZ DE PROBLEMAS            │
│                                         │
│         CRITICIDAD vs IMPACTO           │
│                                         │
│   ALTO       ┌─────────────────┐       │
│              │   P1: CT-01     │       │
│   IMPACTO    │   Lentitud      │       │
│              │   Consultas     │       │
│              └─────────────────┘       │
│                                         │
│   MEDIO      ┌─────────────────┐       │
│              │   P2: CT-03     │       │
│              │   Estabilidad   │       │
│              │   Comprometida  │       │
│              └─────────────────┘       │
│                                         │
│   BAJO              [Sin issues]       │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🚨 DIAGRAMA DE CAUSAS PROBABLES

```
                        PROBLEMA: Consultas Lentas (CT-01)
                                       │
                 ┌─────────────────────┼─────────────────────┐
                 │                     │                     │
            BD LENTA           SERVIDOR LENTO         RED LENTA
                 │                     │                     │
        ┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐
        │                 │  │                 │  │                 │
    Índices Sin    Queries SQL    CPU Alto    Memoria    Latencia    Ancho
    Optimizar      Complejas      Alto        Saturada   > 200ms     Banda
                                                                      Bajo
        
        ✓ Verificar     ✓ Revisar      ✓ Monitorear   ✓ Validar
          índices       logs servidor   recursos       ping/tracert
```

---

## ✅/❌ MATRIZ DE CUMPLIMIENTO

```
                          CRITERIO  │  ESTADO  │  MARGEN  │  ACCIÓN
                          ──────────┼──────────┼──────────┼─────────────
CT-01 p50 (≤400ms)        766 ms    │ ❌ FAIL  │  -92%    │ URGENTE
CT-01 p95 (≤800ms)       1197 ms    │ ❌ FAIL  │  -50%    │ URGENTE
CT-01 Estabilidad        4.59x/3.0x │ ❌ FAIL  │  -53%    │ URGENTE
CT-02 p95 (≤1500ms)       353 ms    │ ✅ PASS  │  +76%    │ MANTENER
CT-02 p99 (≤2500ms)       730 ms    │ ✅ PASS  │  +71%    │ MANTENER
CT-04 Concurrencia         PENDING   │ ⏳ N/A   │   N/A    │ EJECUTAR
CT-05 Repetibilidad        PENDING   │ ⏳ N/A   │   N/A    │ EJECUTAR
```

---

## 📊 ÍNDICES CLAVE DE DESEMPEÑO (KPIs)

```
╔═════════════════════════════════════════════════════════╗
║                     KPI DASHBOARD                       ║
╠═════════════════════════════════════════════════════════╣
║                                                         ║
║ Tasa de Éxito (Requests OK)       400/400  100%  ✅    ║
║ Timeouts                           0        0%    ✅    ║
║ Errores HTTP                       0        0%    ✅    ║
║ Criterios PASS                     1/3     33%    ❌    ║
║ Criterios FAIL                     2/3     67%    ❌    ║
║                                                         ║
║ Velocidad Relativa CT-02 vs CT-01: 4.1x más rápido    ║
║ Variabilidad CT-01                 Moderada-Alta (⚠️)  ║
║ Estabilidad bajo carga             Comprometida (❌)   ║
║                                                         ║
╚═════════════════════════════════════════════════════════╝
```

---

## 🎯 LÍNEA DE TIEMPO: RECOMENDACIONES DE ACCIÓN

```
HOY                 ESTA SEMANA        2 SEMANAS        PRÓXIMO MES
│                       │                  │               │
├─ Ejecutar CT-04       │                  │               │
│  (Concurrencia)       │                  │               │
│                       │                  │               │
│  Ejecutar CT-05       ├─ Investigar      │               │
│  (Repetibilidad)      │  servidor        │               │
│                       │                  │               │
│  Revisar logs         ├─ Optimizar       ├─ Validar      │
│  servidor             │  índices BD      │  cambios      │
│                       │                  │               │
│  Validar red          ├─ Implementar     ├─ Pruebas      │
│                       │  caché           │  de regresión │
│                       │                  │               │
│                       │                  ├─ Reporte      │
│                       │                  │  final        │
│                       │                  │               │
│                       │                  ├─ Producción   │
│                       │                  │  si PASS      │

Prioridad: P1 (Consultas) → P2 (Estabilidad) → P3 (Verificación)
```

---

## 📞 COMANDOS PARA PRÓXIMAS PRUEBAS

```bash
# Ejecutar solo CT-04 (Concurrencia, 5 min)
python run_performance_tests.py --ct-04

# Ejecutar solo CT-05 (Repetibilidad, 15 min)
python run_performance_tests.py --ct-05 --exec 3

# Ejecutar TODO (CT-01 a CT-05, ~25 min)
python run_performance_tests.py --all

# Ejecutar con 500 requests (baseline más exhaustiva)
python run_performance_tests.py --requests 500

# Ejecutar CT-04 con 20 usuarios (stress test)
python run_performance_tests.py --ct-04 --users 20
```

---

## 💾 ARCHIVOS GENERADOS

```
./test_results_BASELINE_20261125_115449.json    ← Datos brutos (JSON)
./REPORTE_RESULTADOS_PRUEBAS.md                 ← Reporte detallado
./RESUMEN_VISUAL_RESULTADOS.md                  ← Este archivo
```

---

**Generado:** 25-Nov-2026 11:54:49  
**Versión:** 1.0  
**Próxima ejecución:** Hoy (CT-04 y CT-05)
