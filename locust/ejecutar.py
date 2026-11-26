"""Verifica la llave de prueba y lanza el perfil seleccionado de Locust."""

import argparse
import getpass
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime

import requests

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from destino import HOST, RUTA

PERFILES = {"latencia": (1, "1m"), "concurrencia": (3, "2m")}
CARPETA = Path(__file__).resolve().parent
RAIZ = CARPETA.parent


def cargar_clave():
    """Carga la clave desde .env o la solicita interactivamente."""
    # Busca .env en la carpeta raíz (carpeta padre)
    env_file = RAIZ / ".env"
    
    if load_dotenv and env_file.exists():
        load_dotenv(env_file, override=True)
    
    clave = os.getenv("ONVO_TEST_SECRET_KEY", "").strip()
    if clave:
        return clave
    
    # Si no está en .env, la solicita
    if not sys.stdin.isatty():
        raise ValueError(
            "Abrí probar.cmd en una terminal para ingresar la llave de prueba, "
            "o creá un archivo .env con ONVO_TEST_SECRET_KEY=tu_clave"
        )
    try:
        clave = getpass.getpass("Llave secreta de prueba de ONVO: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
    
    return clave


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("perfil", nargs="?", choices=("verificar", *PERFILES),
                        default="verificar")
    args = parser.parse_args()

    try:
        clave = cargar_clave()
    except ValueError as e:
        parser.error(str(e))
        return 2
    
    if not clave:
        return 2
    
    if not re.fullmatch(r"onvo_test_secret_key_[A-Za-z0-9_-]+", clave):
        parser.error("Ingresá una llave con prefijo onvo_test_secret_key_.")

    try:
        respuesta = requests.get(
            HOST + RUTA,
            headers={"Authorization": f"Bearer {clave}", "Accept": "application/json"},
            allow_redirects=False,
            timeout=(5, 10),
        )
    except requests.RequestException as error:
        print(f"No se pudo conectar con ONVO: {type(error).__name__}.")
        return 1

    print(f"Comprobación de ONVO: HTTP {respuesta.status_code} "
          f"en {respuesta.elapsed.total_seconds() * 1000:.0f} ms.", flush=True)
    if respuesta.status_code != 200:
        return 1
    if args.perfil == "verificar":
        return 0

    usuarios, duracion = PERFILES[args.perfil]
    momento = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    carpeta_reporte = CARPETA / "reportes" / f"{momento}_{args.perfil}"
    carpeta_reporte.mkdir(parents=True)
    entorno = {k: v for k, v in os.environ.items() if not k.upper().startswith("LOCUST_")}
    entorno["ONVO_TEST_SECRET_KEY"] = clave
    resultado = subprocess.run(
        [
            sys.executable, "-m", "locust", "-f", str(CARPETA / "locustfile.py"),
            "--headless", "--host", HOST, "-u", str(usuarios), "-r", "1",
            "-t", duracion, "--stop-timeout", "15", "--exit-code-on-error", "1",
            "--html", str(carpeta_reporte / "reporte.html"),
            "--csv", str(carpeta_reporte / "metricas"), "--csv-full-history",
        ],
        cwd=CARPETA,
        env=entorno,
        check=False,
    )
    print(f"Carpeta de reportes: {carpeta_reporte}")
    return resultado.returncode


if __name__ == "__main__":
    raise SystemExit(main())
