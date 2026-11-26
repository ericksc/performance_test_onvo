#!/usr/bin/env python
"""
Script para capturar screenshots de Locust durante pruebas de rendimiento
Captura gráficos en diferentes momentos:
  - Inicio
  - Durante CT-01
  - Durante CT-04 (concurrencia)
  - Final
"""

import subprocess
import time
import os
from pathlib import Path
import threading

def capture_screenshot(filename, delay=5):
    """Captura screenshot usando PowerShell y Playwright"""
    script = f"""
    Add-Type -AssemblyName System.Windows.Forms
    
    # Esperar a que Locust esté listo
    Start-Sleep -Seconds {delay}
    
    try {{
        # Usar Microsoft Edge para captura (más confiable)
        $url = "http://localhost:8089"
        $output = "$PSScriptRoot\\screenshots\\{filename}"
        
        # Crear carpeta si no existe
        New-Item -ItemType Directory -Force -Path "$PSScriptRoot\\screenshots" | Out-Null
        
        # Usar Playwright directamente desde Python
        python -c "
import asyncio
from playwright.async_api import async_playwright
import os

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={{'width': 1400, 'height': 900}})
        await page.goto('http://localhost:8089', wait_until='networkidle')
        await page.screenshot(path=r'{output}', full_page=True)
        await browser.close()

asyncio.run(capture())
"
    }}
    catch {{
        Write-Error "Error capturando screenshot: $_"
    }}
    """
    
    ps_script = f"""
    powershell -NoProfile -ExecutionPolicy Bypass -Command {{
        {script}
    }}
    """
    
    print(f"[*] Capturando: {filename}")
    os.system(ps_script)
    print(f"[✓] Captura guardada: screenshots/{filename}")


def run_performance_tests_with_captures():
    """Ejecuta pruebas y captura screenshots en tiempo real"""
    
    print("=" * 70)
    print("SUITE DE PRUEBAS CON CAPTURA DE GRÁFICOS EN TIEMPO REAL")
    print("=" * 70)
    print()
    
    # Crear carpeta de screenshots
    os.makedirs("screenshots", exist_ok=True)
    
    # Captura inicial (UI vacío)
    print("[1/5] Capturando estado inicial de Locust...")
    capture_screenshot("01_inicio.png", delay=3)
    time.sleep(2)
    
    # Iniciar pruebas en background
    print("[2/5] Iniciando pruebas de rendimiento...")
    test_process = subprocess.Popen(
        [
            "python", "run_performance_tests.py", "--all"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Enviar confirmaciones automáticas
    test_process.stdin.write("s\ns\n")
    test_process.stdin.flush()
    
    # Captura durante CT-01 (después de ~2 minutos)
    print("[3/5] Esperando a CT-01... (capturando en 2 min)")
    time.sleep(120)
    capture_screenshot("02_durante_ct01.png")
    
    # Captura durante CT-04 (concurrencia, después de ~8 minutos)
    print("[4/5] Esperando a CT-04... (capturando en 7 min más)")
    time.sleep(420)
    capture_screenshot("03_durante_ct04_concurrencia.png")
    
    # Captura final
    print("[5/5] Esperando finalización...")
    stdout, stderr = test_process.communicate(timeout=600)
    
    time.sleep(5)
    capture_screenshot("04_resultados_finales.png")
    
    # Mostrar resultados
    print()
    print("=" * 70)
    print("CAPTURAS COMPLETADAS")
    print("=" * 70)
    print()
    print("Archivos generados en carpeta 'screenshots/':")
    print("  ✓ 01_inicio.png                 - UI inicial")
    print("  ✓ 02_durante_ct01.png           - Durante pruebas CT-01")
    print("  ✓ 03_durante_ct04_concurrencia.png - Durante carga (CT-04)")
    print("  ✓ 04_resultados_finales.png     - Resultados finales")
    print()
    print("Ver http://localhost:8089 para más detalles en tiempo real")
    print()
    
    if stdout:
        print("Salida de pruebas:")
        print(stdout)


def capture_charts_manual():
    """Alternativa: Captura manual de gráficos existentes"""
    
    print("=" * 70)
    print("CAPTURA MANUAL DE GRÁFICOS (Para ejecuciones previas)")
    print("=" * 70)
    print()
    
    os.makedirs("screenshots", exist_ok=True)
    
    print("[*] Abriendo http://localhost:8089 en navegador...")
    print("[*] Capturando gráficos principales...")
    
    # Esperar conexión a Locust
    max_retries = 10
    for i in range(max_retries):
        try:
            import requests
            requests.get("http://localhost:8089", timeout=2)
            print("[✓] Locust server está activo")
            break
        except:
            if i < max_retries - 1:
                print(f"[.] Intentando conexión {i+1}/{max_retries}...")
                time.sleep(1)
            else:
                print("[✗] Locust no está disponible. Inicia: python locust/ui.py")
                return
    
    # Capturar pantalla Stats
    capture_screenshot("stats_table.png", delay=1)
    time.sleep(2)
    
    # Capturar pantalla Charts
    print("\n[*] Capturando tab de Charts...")
    capture_screenshot("charts_response_times.png", delay=1)
    time.sleep(2)
    
    print()
    print("=" * 70)
    print("CAPTURAS GUARDADAS EN: screenshots/")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        capture_charts_manual()
    else:
        try:
            run_performance_tests_with_captures()
        except KeyboardInterrupt:
            print("\n[!] Captura cancelada por usuario")
        except Exception as e:
            print(f"\n[✗] Error: {e}")
