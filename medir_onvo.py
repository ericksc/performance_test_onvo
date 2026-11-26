"""Mide la latencia de una consulta de solo lectura a ONVO Pay."""

import argparse
import getpass
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from pathlib import Path

# Intenta cargar desde .env si está disponible
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        load_dotenv(env_file, override=True)
except ImportError:
    pass


URL = "https://api.onvopay.com/v1/payment-method-domains?limit=1"
METRICAS = (
    "time_namelookup",
    "time_connect",
    "time_appconnect",
    "time_starttransfer",
    "time_total",
)


def medir(curl, configuracion):
    formato = ",".join("%{" + campo + "}" for campo in ("http_code", *METRICAS))
    proceso = subprocess.run(
        [
            curl, "-q", "--config", "-", "--silent", "--connect-timeout", "5",
            "--max-time", "15", "--output", os.devnull, "--write-out", formato, URL,
        ],
        input=configuracion,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    campos = proceso.stdout.strip().split(",")
    if len(campos) != 6:
        return proceso.returncode, 0, [float("nan")] * 5
    return proceso.returncode, int(campos[0]), [float(t) * 1000 for t in campos[1:]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("intentos", nargs="?", type=int, default=10)
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--sin-clave", action="store_true", help="espera HTTP 401")
    modo.add_argument("--pedir-clave", action="store_true",
                      help="solicita la llave de prueba con entrada oculta")
    args = parser.parse_args()
    if not 1 <= args.intentos <= 100:
        parser.error("la cantidad de intentos debe estar entre 1 y 100")

    curl = shutil.which("curl")
    if curl is None:
        parser.error("se requiere curl en PATH")

    configuracion = 'header = "Accept: application/json"\n'
    if not args.sin_clave:
        if args.pedir_clave:
            try:
                clave = getpass.getpass("Llave secreta de prueba de ONVO: ").strip()
            except (EOFError, KeyboardInterrupt):
                parser.exit(2, "\nEntrada de llave cancelada.\n")
        else:
            clave = os.getenv("ONVO_TEST_SECRET_KEY", "")
        if not re.fullmatch(r"onvo_test_secret_key_[A-Za-z0-9_-]+", clave):
            parser.error("configurá ONVO_TEST_SECRET_KEY con una llave secreta de prueba")
        configuracion += f'header = "Authorization: Bearer {clave}"\n'

    esperado = 401 if args.sin_clave else 200
    totales = []
    print("intento curl http    dns_ms    tcp_ms    tls_ms   ttfb_ms  total_ms", flush=True)
    for intento in range(1, args.intentos + 1):
        if intento > 1:
            time.sleep(0.5)
        codigo, http, tiempos = medir(curl, configuracion)
        detalle = " ".join(f"{valor:9.2f}" for valor in tiempos)
        print(f"{intento:7} {codigo:4} {http:03} {detalle}", flush=True)
        if codigo == 0 and http == esperado:
            totales.append(tiempos[-1])

    print(f"\nHTTP {esperado} con transferencia completa: {len(totales)}/{args.intentos}")
    if totales:
        p95 = statistics.quantiles(totales, n=100, method="inclusive")[94] if len(totales) > 1 else totales[0]
        print(
            f"Mínimo: {min(totales):.2f} ms | Mediana: {statistics.median(totales):.2f} ms "
            f"| p95: {p95:.2f} ms | Máximo: {max(totales):.2f} ms"
        )
    return 0 if len(totales) == args.intentos else 1


if __name__ == "__main__":
    raise SystemExit(main())
