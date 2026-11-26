# 🌐 Interfaz Web de Locust - Guía Rápida

## Abrir la UI

### Desde PowerShell (cualquier carpeta)
```powershell
python .\locust\ui.py
```

### Desde Windows (Explorer)
Haz doble clic en: `locust\ui.cmd`

## Qué es Locust

Locust es una herramienta de pruebas de carga que simula múltiples usuarios haciendo solicitudes simultáneamente. La interfaz web te permite:
- Configurar cuántos usuarios querés simular
- Controlar la velocidad de agregación de usuarios
- Ver métricas en tiempo real
- Monitorear éxitos y fallos

## Parámetros principales

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| **Number of users** | Total de usuarios simultáneos a simular | 5, 10, 50 |
| **Spawn rate** | Cuántos usuarios agregar por segundo | 1, 2, 5 |
| **Run time** | Duración de la prueba (opcional) | 60s, 5m, 1h |

## Flujo típico de uso

1. **Ejecuta:** `python .\locust\ui.py`
   
2. **Se abre:** `http://localhost:8089` en tu navegador

3. **Configura:**
   - Number of users: **5**
   - Spawn rate: **1**
   - Dejar Run time vacío para duración manual

4. **Inicia:** Click en botón azul **"Start swarming"**

5. **Monitorea:**
   - **Charts** tab: Gráficos de respuesta y throughput
   - **Statistics** tab: Tabla con estadísticas detalladas
   - **Failures** tab: Errores ocurridos
   - **Exceptions** tab: Excepciones de Python

6. **Detén:** Click en **"Stop"** o Ctrl+C en terminal

## Métricas que ves

### Statistics
- **Type**: GET/POST/etc
- **Name**: Nombre de la solicitud
- **# requests**: Cantidad total
- **# failures**: Cantidad de fallos
- **Median**: Tiempo medio de respuesta
- **Average**: Promedio
- **Min**: Mínimo
- **Max**: Máximo
- **Average size**: Tamaño promedio de respuesta

### Charts
- **Response Times**: Evolución en el tiempo
- **Number of Requests per Second**: Throughput
- **Response Time (ms) Chart**: Distribución de tiempos
- **Cumulative Failure Ratio**: Tasa de fallos

## Tipos de fallos

| Código | Significado |
|--------|-------------|
| 200 | OK (esperado) |
| 401 | No autorizado (llave expirada/inválida) |
| 403 | Prohibido |
| 429 | Rate limit (demasiadas solicitudes) |
| 500 | Error del servidor |

## Troubleshooting

### "Port 8089 already in use"
Ya hay otra instancia de Locust corriendo
```powershell
# Detén la instancia anterior
# O usa otro puerto:
python -m locust -f locust/locustfile.py --host https://api.onvopay.com --web -p 8090
```

### "Cannot connect to ONVO"
Verifica que tu llave `.env` sea correcta
```powershell
# Reconfigura la llave
python configurar_clave.py
```

### "ONVO_TEST_SECRET_KEY not found"
El archivo `.env` no existe o no tiene la variable
```powershell
python configurar_clave.py
```

## Tips

✅ **Comienza con pocos usuarios** (1-3) para verificar que todo funciona

✅ **Aumenta gradualmente** la carga si quieres medir límites

✅ **Observa el Spawn rate** - muy alto puede causar spikes artificiales

✅ **Lee la pestaña Failures** si ves errores

✅ **Los reportes** se guardan en `locust/reportes/` al detener

## Comparación con modo headless

| Aspecto | UI (web) | Headless (comando) |
|--------|----------|-------------------|
| Interfaz | Web interactiva | Línea de comandos |
| Configuración | En tiempo real | Predefinida en scripts |
| Métricas | Gráficos y tablas | Archivo HTML/CSV |
| Control | Iniciar/Detener botones | Duración fija |
| Mejor para | Experimentar/Explorar | Tests automatizados |

## Más información

- [Documentación oficial de Locust](https://locust.io/)
- [README.md](./README.md) - Documentación de tu proyecto
- [SETUP.md](../SETUP.md) - Guía de setup
