@echo off
REM Abre la interfaz web de Locust en http://localhost:8089

echo ============================================================
echo   Locust UI - Interfaz web interactiva
echo ============================================================
echo.

cd /d "%~dp0"
python ui.py

pause
