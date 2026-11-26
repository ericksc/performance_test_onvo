"""Lanza Locust con interfaz web interactiva."""

import os
from pathlib import Path
import re
import subprocess
import sys

CARPETA = Path(__file__).resolve().parent
RAIZ = CARPETA.parent

# Carga .env manualmente para asegurar que funciona
env_file = RAIZ / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea and not linea.startswith("#"):
                if "=" in linea:
                    clave, valor = linea.split("=", 1)
                    os.environ[clave.strip()] = valor.strip()

# También intenta cargar con dotenv si está disponible
try:
    from dotenv import load_dotenv
    if load_dotenv and env_file.exists():
        load_dotenv(env_file, override=True)
except ImportError:
    pass

from destino import HOST, RUTA


def cargar_clave():
    """Obtiene la clave desde variables de entorno."""
    clave = os.getenv("ONVO_TEST_SECRET_KEY", "").strip()
    return clave


def main():
    clave = cargar_clave()
    
    if not clave:
        print("Error: ONVO_TEST_SECRET_KEY no está configurada.")
        print("Ejecutá primero: python configurar_clave.py")
        return 1
    
    if not re.fullmatch(r"onvo_test_secret_key_[A-Za-z0-9_-]+", clave):
        print("Error: Llave inválida. Debe empezar con 'onvo_test_secret_key_'")
        return 1
    
    entorno = os.environ.copy()
    entorno["ONVO_TEST_SECRET_KEY"] = clave
    
    print("=" * 60)
    print("Locust UI - Interfaz web interactiva")
    print("=" * 60)
    print()
    print("Locust se abrirá en http://localhost:8089")
    print()
    print("Pasos:")
    print("  1. Se abrirá automáticamente en tu navegador")
    print("  2. Ingresá los parámetros de carga:")
    print("     • Number of users: 1-10 usuarios")
    print("     • Spawn rate: 1-5 usuarios/segundo")
    print("  3. Hacé clic en 'Start swarming'")
    print()
    print("Para detener: Ctrl+C en esta terminal")
    print("=" * 60)
    print()
    
    resultado = subprocess.run(
        [
            sys.executable, "-m", "locust", 
            "-f", str(CARPETA / "locustfile.py"),
            "--host", HOST,
            "--web-host", "localhost",
            "--web-port", "8089",
        ],
        cwd=CARPETA,
        env=entorno,
        check=False,
    )
    return resultado.returncode


if __name__ == "__main__":
    raise SystemExit(main())
