"""Gestiona la configuración centralizada de ONVO Pay."""

import os
import re
from pathlib import Path
from dotenv import load_dotenv


# Carga variables de entorno desde .env si existe
ENV_FILE = Path(__file__).parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


def obtener_clave_secreta():
    """Obtiene la clave secreta de ONVO desde variables de entorno."""
    clave = os.getenv("ONVO_TEST_SECRET_KEY", "").strip()
    if not clave:
        raise ValueError(
            "ONVO_TEST_SECRET_KEY no está configurada. "
            "Copia tu llave al archivo .env o establece la variable de entorno."
        )
    if not re.fullmatch(r"onvo_test_secret_key_[A-Za-z0-9_-]+", clave):
        raise ValueError("La clave debe tener el prefijo onvo_test_secret_key_")
    return clave
