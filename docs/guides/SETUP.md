# 🚀 SETUP RÁPIDO - Gestión Centralizada de Secretos de ONVO

## El problema que se resolvió

Antes tenías que:
- ❌ Pedir la llave cada vez: `python medir_onvo.py 1 --pedir-clave`
- ❌ Configurar variables de entorno manualmente: `$env:ONVO_TEST_SECRET_KEY = "..."`
- ❌ Mantener la llave en memoria o en scripts inseguros

**Ahora**: Guardas la llave **una sola vez** de forma segura, y todos los scripts la usan automáticamente.

---

## 📋 Pasos de configuración

### Paso 1: Guardar tu llave secreta (primera vez)

```powershell
cd c:\work\poc_onvo
python configurar_clave.py
```

**Qué hace:**
1. Te pide que pegues tu llave secreta (`onvo_test_secret_key_...`) del Dashboard de ONVO
2. Te pide que la confirmes (pegando nuevamente)
3. Crea un archivo `.env` protegido
4. Solo tú puedes leer ese archivo

**Resultado:**
```
✓ Llave guardada en: c:\work\poc_onvo\.env
✓ El archivo está protegido y solo tú puedes leerlo.
```

---

### Paso 2: Usar `medir_onvo.py` (sin parámetros)

Ahora es mucho más simple:

```powershell
# Medir 1 solicitud
python .\poc_onvo\medir_onvo.py 1

# Medir 20 solicitudes
python .\poc_onvo\medir_onvo.py 20

# Diagnóstico sin credenciales (espera HTTP 401)
python .\poc_onvo\medir_onvo.py 10 --sin-clave
```

---

### Paso 3: Usar Locust

**Opción A: Interfaz web interactiva (recomendado)**

```powershell
python .\poc_onvo\locust\ui.py
```

O desde Windows: Haz doble clic en `locust\ui.cmd`

Esto abre `http://localhost:8089` donde puedes:
1. Ingresar "Number of users" (ej: 5)
2. Ingresar "Spawn rate" (ej: 1 usuario/segundo)
3. Hacé clic en "Start swarming"
4. Ver métricas en tiempo real

**Opción B: Tests automatizados (modo headless)**

```powershell
# Solo verificar la conexión
python .\poc_onvo\locust\ejecutar.py verificar

# Medir latencia (1 usuario, 1 minuto)
python .\poc_onvo\locust\ejecutar.py latencia

# Medir concurrencia (3 usuarios, 2 minutos)
python .\poc_onvo\locust\ejecutar.py concurrencia
```

Los reportes se guardan en `locust/reportes/<timestamp>_<perfil>/`

---

## 📁 Estructura de archivos

```
c:\work\poc_onvo\
├── .env                      ← Tu llave (NO versionada)
├── .env.example              ← Plantilla de referencia
├── .gitignore                ← Protege .env del versionado
├── configurar_clave.py       ← Script de setup (ejecuta 1 vez)
├── config.py                 ← Funciones compartidas
├── medir_onvo.py             ← Test con curl
├── README.md                 ← Documentación
├── GUIA_SECRETOS.md          ← Esta guía
└── locust/
    ├── ejecutar.py           ← Lanza Locust
    ├── locustfile.py         ← Tests de Locust
    ├── destino.py            ← Configuración de endpoints
    ├── requirements.txt       ← Dependencias
    └── README.md             ← Documentación
```

---

## 🔒 Seguridad

✅ **Lo que se protege:**
- El `.env` está en `.gitignore` (nunca se sube a Git)
- El archivo tiene permisos de lectura solo para tu usuario
- La llave nunca se escribe en scripts o logs

✅ **Cambiar la llave después:**
```powershell
python configurar_clave.py    # Ejecuta nuevamente, reemplaza el .env
```

---

## ⏮️ Compatibilidad con métodos antiguos

Los siguientes métodos **siguen funcionando** si prefieres no usar `.env`:

```powershell
# Método 1: Variable de entorno temporal
$env:ONVO_TEST_SECRET_KEY = "tu_llave_aqui"
python .\poc_onvo\medir_onvo.py 10
Remove-Item Env:ONVO_TEST_SECRET_KEY

# Método 2: Pedir cada vez
python .\poc_onvo\medir_onvo.py 10 --pedir-clave
```

---

## ✅ Validación

Para verificar que todo funciona:

```powershell
# Verifica que medir_onvo.py pueda cargar la configuración
python .\poc_onvo\locust\ejecutar.py verificar
```

Deberías ver: `Comprobación de ONVO: HTTP 200 en XXX ms.`

---

## 🆘 Troubleshooting

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'dotenv'` | Ejecuta `pip install python-dotenv` |
| `Error al guardar: ...` | Verifica que tengas permisos de escritura en `c:\work\poc_onvo` |
| `Ingresá una llave con prefijo onvo_test_secret_key_` | Copia la llave exacta del Dashboard de ONVO |
| `.env no existe` | Ejecuta `python configurar_clave.py` primero |

---

## 📚 Más información

- [GUIA_SECRETOS.md](./GUIA_SECRETOS.md) — Detalles técnicos
- [README.md](./README.md) — Documentación general
- [locust/README.md](./locust/README.md) — Documentación de Locust
- [Autenticación de ONVO](https://docs.onvopay.com/authentication)
