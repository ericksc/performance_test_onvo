# Kit de velocidad de ONVO con Locust

## Interfaz web interactiva (UI)

La forma más fácil es usar el comando directo desde la carpeta raíz:

```powershell
# Abre http://localhost:8089 automáticamente
python .\locust\ui.py
```

O desde la carpeta locust:

```powershell
python ui.py
```

También puedes hacer doble clic en `ui.cmd` desde el Explorador de archivos.

**Pasos en la UI:**
1. Se abre automáticamente en http://localhost:8089
2. Ingresá los parámetros:
   - **Number of users**: cuántos usuarios simultáneos (ej: 5)
   - **Spawn rate**: usuarios/segundo a agregar (ej: 1)
3. Hacé clic en **"Start swarming"**
4. Observá las métricas en tiempo real
5. Para detener: **"Stop"** o Ctrl+C en la terminal

## Configuración inicial

1. Desde la carpeta raíz `poc_onvo`, ejecutá el configurador de llave:
   ```powershell
   python configurar_clave.py
   ```
   Pegá tu llave secreta de prueba del Dashboard de ONVO. El archivo `.env` se guarda protegido.

2. Verifica la conexión:
   ```powershell
   python ejecutar.py verificar
   ```

## Ejecutar perfiles de carga

Una vez configurada la llave, ejecutá desde esta carpeta:

```powershell
python ejecutar.py latencia
python ejecutar.py concurrencia
```

O el comando interactivo desde la carpeta raíz:

```powershell
python .\locust\ejecutar.py latencia
```

## Perfiles disponibles

| Perfil | Usuarios | Duración | Ritmo aproximado máximo |
| --- | ---: | ---: | ---: |
| Verificar | 1 | Una consulta | Una consulta en total |
| Latencia | 1 | 1 minuto | 0,5 solicitudes/s |
| Concurrencia | 3 | 2 minutos | 1,5 solicitudes/s |

Los perfiles comienzan tras una comprobación HTTP 200. Ambos consultan el mismo endpoint de solo lectura, `GET /v1/payment-method-domains?limit=1`. Se registra como fallo toda respuesta distinta de 200 y se detiene la ejecución ante HTTP 401, 403 o 429. [Referencia del endpoint](https://docs.onvopay.com/en/api/listar-dominios-de-metodos-de-pago)

## Reportes

Los reportes se guardan en la carpeta `reportes/` con marca de tiempo:

```
reportes/
├── 20240115_143022_123456_latencia/
│   ├── reporte.html          (reporte visual)
│   ├── metricas_stats.csv    (resumen)
│   ├── metricas_stats_history.csv  (evolución en el tiempo)
│   └── metricas_failures.csv       (errores)
└── ...
```

Abrí `reporte.html` en el navegador. En el reporte, revisá:
- **Mediana** para el tiempo habitual
- **p95** para las respuestas más lentas
- **Solicitudes por segundo**
- **Tasa de fallos**

El reporte mide las solicitudes HTTP con reutilización de conexiones. Para medir DNS, TCP y TLS en conexiones nuevas, usá el PoC con curl desde la carpeta raíz:

```powershell
python medir_onvo.py 20
```

