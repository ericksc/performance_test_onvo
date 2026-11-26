#!/usr/bin/env python
"""
Script simple para capturar gráficos con Playwright durante ejecución de pruebas
"""

import subprocess
import time
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def capture_screenshot_async(url, filename):
    """Captura screenshot de Locust usando Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=10000)
            
            # Crear carpeta si no existe
            Path("screenshots").mkdir(exist_ok=True)
            
            filepath = f"screenshots/{filename}"
            await page.screenshot(path=filepath, full_page=True)
            print(f"[✓] Captura guardada: {filepath}")
            return filepath
        except Exception as e:
            print(f"[✗] Error capturando {filename}: {e}")
        finally:
            await browser.close()


def run_tests_with_capture():
    """Ejecuta pruebas y captura screenshots en momentos clave"""
    
    print("=" * 70)
    print("EJECUCIÓN DE PRUEBAS CON CAPTURA DE GRÁFICOS")
    print("=" * 70)
    print()
    
    # Captura 1: Formulario inicial (antes de pruebas)
    print("[1/4] Capturando estado inicial...")
    asyncio.run(capture_screenshot_async("http://localhost:8089", "01_inicio.png"))
    time.sleep(2)
    
    # Iniciar pruebas
    print("[2/4] Iniciando pruebas de rendimiento (28 min aprox)...")
    print("[!] Capturando gráficos en tiempo real mientras se ejecutan")
    print()
    
    test_process = subprocess.Popen(
        ["python", "run_performance_tests.py", "--all"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Enviar confirmaciones
    test_process.stdin.write("s\ns\n")
    test_process.stdin.flush()
    
    # Captura durante ejecución (cada 5 minutos)
    capture_times = [120, 300, 480, 720]  # 2, 5, 8, 12 minutos
    capture_names = [
        "02_durante_ct01.png",
        "03_durante_ct02_ct03.png", 
        "04_durante_ct04_carga.png",
        "05_durante_ct05_repetibilidad.png"
    ]
    
    for delay, name in zip(capture_times, capture_names):
        print(f"[*] Esperando {delay}s para captura: {name}")
        time.sleep(delay - (5 if capture_times.index(delay) > 0 else 0))
        print(f"[*] Capturando: {name}")
        asyncio.run(capture_screenshot_async("http://localhost:8089", name))
    
    # Esperar a que terminen las pruebas
    print("\n[*] Esperando finalización de pruebas...")
    stdout, stderr = test_process.communicate(timeout=1800)
    
    # Captura final
    print("[3/4] Capturando resultados finales...")
    time.sleep(5)
    asyncio.run(capture_screenshot_async("http://localhost:8089", "06_resultados_finales.png"))
    
    # Captura de Statistics tab
    print("[4/4] Capturando tabla de estadísticas...")
    asyncio.run(capture_stats_tab("07_statistics_table.png"))
    
    print()
    print("=" * 70)
    print("CAPTURAS COMPLETADAS ✓")
    print("=" * 70)
    print()
    print("Archivos guardados en carpeta 'screenshots/':")
    print("  ✓ 01_inicio.png")
    print("  ✓ 02_durante_ct01.png")
    print("  ✓ 03_durante_ct02_ct03.png")
    print("  ✓ 04_durante_ct04_carga.png")
    print("  ✓ 05_durante_ct05_repetibilidad.png")
    print("  ✓ 06_resultados_finales.png")
    print("  ✓ 07_statistics_table.png")
    print()
    
    if stdout:
        print("=" * 70)
        print("SALIDA DE PRUEBAS:")
        print("=" * 70)
        print(stdout[-2000:])  # Últimas 2000 caracteres


async def capture_stats_tab(filename):
    """Captura específicamente la tabla de Statistics"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        
        try:
            await page.goto("http://localhost:8089", wait_until="networkidle", timeout=10000)
            
            # Buscar y click en Statistics tab
            stats_tab = await page.query_selector('[role=tab]:has-text("Statistics")')
            if not stats_tab:
                # Intentar con selector alternativo
                stats_tab = await page.query_selector('a:has-text("Statistics")')
            
            if stats_tab:
                await stats_tab.click()
                await page.wait_for_load_state("networkidle")
            
            # Scroll a la tabla
            await page.evaluate("() => { document.querySelector('table')?.scrollIntoView(); }")
            await page.wait_for_timeout(1000)
            
            Path("screenshots").mkdir(exist_ok=True)
            filepath = f"screenshots/{filename}"
            await page.screenshot(path=filepath, full_page=True)
            print(f"[✓] Tabla Statistics capturada: {filepath}")
        except Exception as e:
            print(f"[✗] Error capturando Statistics: {e}")
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        run_tests_with_capture()
    except KeyboardInterrupt:
        print("\n[!] Captura cancelada por usuario")
    except Exception as e:
        print(f"\n[✗] Error: {e}")
        import traceback
        traceback.print_exc()
