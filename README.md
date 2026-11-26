# Medición de latencia de ONVO Pay

Para medir latencia y concurrencia con reportes HTML y CSV, abrí el [kit de Locust](locust/README.md).

El script en Python hace solicitudes GET a `/v1/payment-method-domains?limit=1` y descarta el cuerpo de cada respuesta. Requiere Python 3.8 o posterior y curl en PATH. [Referencia del endpoint](https://docs.onvopay.com/en/api/listar-dominios-de-metodos-de-pago)

## Configurar la llave secreta

ONVO usa `https://api.onvopay.com/v1` también para pruebas. ONVO genera las llaves de prueba al registrar una cuenta. Copiá del Dashboard la llave que empieza con `onvo_test_secret_key_`. [Autenticación de ONVO](https://docs.onvopay.com/authentication)

Ejecutá el configurador interactivo para guardar la llave de forma segura en un archivo `.env`:

```powershell
python .\poc_onvo\configurar_clave.py
```

Esto crea un archivo `.env` protegido que tanto `medir_onvo.py` como el kit de Locust pueden usar automáticamente.

## Confirmar HTTP 200 en modo de prueba

Una vez configurada la llave, ejecutá desde la carpeta `materiales`:

```powershell
python .\poc_onvo\medir_onvo.py 1
```

La confirmación esperada es `HTTP 200 con transferencia completa: 1/1`. Cambiá `1` por `20` para medir la latencia en varias solicitudes.

## Diagnóstico sin credenciales

Esta consulta espera HTTP 401.

```powershell
python .\poc_onvo\medir_onvo.py 10 --sin-clave
```

## Interfaz web interactiva de Locust

Para usar la UI de Locust con métricas en tiempo real:

```powershell
python .\locust\ui.py
```

Esto:
1. Abre automáticamente `http://localhost:8089` en tu navegador
2. Verifica la conexión con ONVO
3. Te permite ingresar parámetros de carga interactivamente
4. Muestra métricas en tiempo real mientras se ejecuta

**Desde Windows:** Puedes hacer doble clic en `locust/ui.cmd`

## Tests de carga sin interfaz (modo headless)

Una vez configurada la llave en `.env`, ejecutá desde `locust/`:

```powershell
python .\locust\ejecutar.py latencia
```

O para solo verificar la conexión:

```powershell
python .\locust\ejecutar.py verificar
```

## Variable de entorno alternativa

Si prefieres no guardar la llave en archivo, puedes usar `ONVO_TEST_SECRET_KEY`:

```powershell
$env:ONVO_TEST_SECRET_KEY = "tu_llave_aqui"
python .\poc_onvo\medir_onvo.py 20
Remove-Item Env:ONVO_TEST_SECRET_KEY
```

Cada intento abre una conexión nueva. DNS, TCP, TLS y TTFB son tiempos acumulados desde el inicio de la consulta. TTFB indica cuándo llegó el primer byte y el tiempo total incluye la descarga de la respuesta. El resumen muestra mínimo, mediana, p95 y máximo solo para transferencias completas con el estado HTTP esperado. Con pocas consultas, el p95 es orientativo.
