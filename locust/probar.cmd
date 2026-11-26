@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
    if errorlevel 1 goto fallo
)
".venv\Scripts\python.exe" -m pip show locust >nul 2>&1
if errorlevel 1 (
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto fallo
)
if not "%~1"=="" (
    ".venv\Scripts\python.exe" ejecutar.py %*
    exit /b
)
echo 1. Verificar HTTP 200 con una consulta
echo 2. Medir latencia con 1 usuario durante 1 minuto
echo 3. Medir concurrencia con 3 usuarios durante 2 minutos
choice /c 123 /m "Selecciona una opcion"
if errorlevel 4 exit /b 2
if errorlevel 3 (
    set "perfil=concurrencia"
) else if errorlevel 2 (
    set "perfil=latencia"
) else if errorlevel 1 (
    set "perfil=verificar"
) else (
    exit /b 2
)
".venv\Scripts\python.exe" ejecutar.py %perfil%
set "resultado=%ERRORLEVEL%"
pause
exit /b %resultado%

:fallo
echo No se pudo preparar Locust. Verifica que Python este instalado y que tengas acceso a PyPI.
pause
exit /b 1
