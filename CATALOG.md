# Catálogo — performance_test_onvo

Índice de código, reportes, guías, resúmenes y resultados de las pruebas de rendimiento de ONVO Pay.

## Código
| Archivo | Descripción |
|---|---|
| `test_onvo_performance.py` | Suite principal de pruebas de rendimiento |
| `run_performance_tests.py` | Ejecutor de las pruebas |
| `medir_onvo.py` | Medición rápida de latencia |
| `generate_charts.py` | Generación de gráficos (`graficos/`) |
| `capture_screenshots.py`, `capture_live_screenshots.py` | Capturas de pantalla |
| `config.py`, `configurar_clave.py` | Configuración y clave (vía variable de entorno, nunca en el repo) |
| `DEMO.ps1` | Demo en PowerShell |
| `locust/` | Pruebas de carga con Locust (ver `locust/README.md`) |

## Reportes (`docs/reports/`)
- `REPORTE_FINAL_COMPLETO.md` — reporte final completo
- `REPORTE_EJECUCION_COMPLETA_20261125.md` — ejecución del 2026-11-25
- `REPORTE_RESULTADOS_PRUEBAS.md` — resultados de las pruebas
- `ENTREGA_FINAL_COMPLETA.md` — entrega final
- `GRAFICOS_RESULTADOS.md` — gráficos y resultados
- `RESULTADO_FINAL.txt` — resultado final

## Resúmenes e índices (`docs/summaries/`)
- `RESUMEN_EJECUTIVO_UI.md`, `RESUMEN_RAPIDO.md`, `RESUMEN_VISUAL_RESULTADOS.md`, `EXECUTION_SUMMARY.txt`
- `INDEX_REPORTES.md`, `INDICE_COMPLETO_REPORTES.md`

## Guías (`docs/guides/`)
- `SETUP.md`, `PRUEBAS_QUICKSTART.md`, `PERFORMANCE_TESTS_README.md`, `TEST_DOCUMENTATION.md`
- `CI_CD_INTEGRATION.md`, `LOCUST_UI.md`, `GUIA_SECRETOS.md`
- `LEER_PRIMERO.txt`, `LEER_PRIMERO_NUEVA_EJECUCION.txt`

## Resultados y gráficos
- `results/` — JSON de las ejecuciones BASELINE (20261125)
- `graficos/` — gráficos PNG (criterios, latencias, degradación, varianza)

## Secretos
`.env` está en `.gitignore`. Use `.env.example` como plantilla y defina `ONVO_TEST_SECRET_KEY` localmente.
