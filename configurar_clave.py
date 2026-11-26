"""Script interactivo para guardar la llave secreta de ONVO en .env"""

import getpass
import os
import re
from pathlib import Path


def main():
    env_file = Path(__file__).parent / ".env"
    
    print("=" * 60)
    print("Configurador de llave secreta de ONVO Pay")
    print("=" * 60)
    print()
    
    # Si ya existe .env, pregunta si desea sobrescribir
    if env_file.exists():
        try:
            clave_actual = os.getenv("ONVO_TEST_SECRET_KEY", "")
            if clave_actual:
                print(f"✓ Ya hay una llave configurada: {clave_actual[:20]}...")
        except Exception:
            pass
        
        while True:
            respuesta = input("\n¿Deseas reemplazarla? (s/n): ").strip().lower()
            if respuesta in ("s", "si", "sí"):
                break
            elif respuesta in ("n", "no"):
                print("Cancelado.")
                return 0
    
    print("\nCopia tu llave desde el Dashboard de ONVO Pay:")
    print("1. Inicia sesión en https://dashboard.onvopay.com")
    print("2. Ve a Configuración > Llaves API")
    print("3. Copia la llave que comienza con 'onvo_test_secret_key_'")
    print()
    
    while True:
        clave = getpass.getpass("Pega la llave secreta de prueba: ").strip()
        
        if not clave:
            print("✗ La llave no puede estar vacía.")
            continue
        
        if not re.fullmatch(r"onvo_test_secret_key_[A-Za-z0-9_-]+", clave):
            print("✗ La llave debe empezar con 'onvo_test_secret_key_' y contener solo caracteres alfanuméricos, guiones y guiones bajos.")
            continue
        
        # Confirma la llave
        confirmar = getpass.getpass("Confirma la llave pegándola nuevamente: ").strip()
        if clave != confirmar:
            print("✗ Las llaves no coinciden. Intenta de nuevo.")
            continue
        
        break
    
    # Guarda en .env
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(f"# Llave secreta de prueba de ONVO Pay\n")
            f.write(f"ONVO_TEST_SECRET_KEY={clave}\n")
        
        # Protege el archivo en Windows
        if os.name == "nt":
            os.system(f'icacls "{env_file}" /grant:r "%USERNAME%:F" /inheritance:r >nul 2>&1')
        # En Linux/macOS
        else:
            os.chmod(env_file, 0o600)
        
        print(f"\n✓ Llave guardada en: {env_file}")
        print("✓ El archivo está protegido y solo tú puedes leerlo.")
        print("\nAhora puedes usar:")
        print("  python medir_onvo.py 10")
        print("  python locust/ejecutar.py latencia")
        return 0
        
    except Exception as e:
        print(f"✗ Error al guardar: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
