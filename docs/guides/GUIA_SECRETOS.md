## 🔑 Gestión Centralizada de Secretos de ONVO

### ¿Qué se cambió?

Antes necesitabas:
- Usar `--pedir-clave` cada vez que ejecutabas
- O usar `$env:ONVO_TEST_SECRET_KEY` manualmente
- O tener la llave explícita en `--config` de curl

Ahora:
- **Guardas la llave una sola vez** en un archivo `.env` protegido
- **Ambos scripts la usan automáticamente**: `medir_onvo.py` y Locust
- **El archivo `.env` está en .gitignore**, así no comitís secretos

### 📋 Pasos de setup

#### 1. Configurar la llave (primera vez)
```powershell
cd c:\work\poc_onvo
python configurar_clave.py
```
- Pegas tu llave `onvo_test_secret_key_...` del Dashboard de ONVO
- Se crea automáticamente `c:\work\poc_onvo\.env` protegido
- El archivo solo lo puedes leer tú (Windows/Linux)

#### 2. Usar `medir_onvo.py` (sin parámetros)
```powershell
python .\poc_onvo\medir_onvo.py 1
python .\poc_onvo\medir_onvo.py 20
```
Obtiene la clave desde `.env` automáticamente.

#### 3. Usar Locust
```powershell
python .\poc_onvo\locust\ejecutar.py verificar
python .\poc_onvo\locust\ejecutar.py latencia
python .\poc_onvo\locust\ejecutar.py concurrencia
```
También obtiene la clave desde `.env`.

### 📁 Archivos nuevos

| Archivo | Propósito |
|---------|-----------|
| `.env` | Secretos locales (creado por `configurar_clave.py`, no versionado) |
| `.env.example` | Plantilla de referencia |
| `configurar_clave.py` | Script interactivo para guardar la llave |
| `config.py` | Funciones compartidas de configuración |
| `.gitignore` | Protege `.env` y otros archivos locales |

### 🔄 Cambios en scripts

#### `medir_onvo.py`
- Ahora intenta cargar `.env` automáticamente
- Mantiene compatibilidad con `--pedir-clave` y `--sin-clave`
- Mantiene compatibilidad con variable de entorno

#### `locust/ejecutar.py` (actualizado)
- Carga `.env` si existe en la carpeta padre
- Fallback a entrada interactiva si no está configurado
- Mejor manejo de errores

#### `locust/locustfile.py` (arreglado)
- Ahora lee correctamente la clave desde `ONVO_TEST_SECRET_KEY`
- Usa `Bearer {clave}` en el header Authorization (formato correcto)

#### `locust/requirements.txt`
- Añadida `python-dotenv` para cargar `.env`

### 🛡️ Seguridad

- La llave se guarda **local**, nunca en repositorio (`.gitignore`)
- Archivo `.env` protegido con permisos de lectura solo para tu usuario
- Puedes revisar la llave guardada con: `cat .env` (no la expondrá)
- Para cambiar la llave, ejecuta `configurar_clave.py` nuevamente

### ⏮️ Compatibilidad hacia atrás

Los siguientes métodos **siguen funcionando**:

```powershell
# Método antiguo: variable de entorno
$env:ONVO_TEST_SECRET_KEY = "tu_clave"
python .\poc_onvo\medir_onvo.py 10

# Método antiguo: pedir cada vez
python .\poc_onvo\medir_onvo.py 10 --pedir-clave
```
