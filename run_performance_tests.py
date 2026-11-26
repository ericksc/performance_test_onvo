"""
Script de ejecución automática de pruebas de rendimiento para ONVO Pay

Uso:
  python run_performance_tests.py                    # Ejecuta CT-01, CT-02, CT-03
  python run_performance_tests.py --all              # Ejecuta todos (incluye CT-04, CT-05)
  python run_performance_tests.py --ct-04            # Solo CT-04 (concurrencia)
  python run_performance_tests.py --ct-05 --exec 3   # CT-05 con 3 ejecuciones
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Load .env file
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

from test_onvo_performance import ONVOPerformanceTest


def save_report(results: dict, test_name: str = "BASELINE"):
    """Guarda resultados en archivo dated."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{test_name}_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n[OK] Resultados guardados: {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(
        description="Suite de pruebas de rendimiento para ONVO Pay API"
    )
    parser.add_argument("--all", action="store_true", help="Ejecutar todos los criterios")
    parser.add_argument("--ct-01", action="store_true", help="Solo CT-01")
    parser.add_argument("--ct-02", action="store_true", help="Solo CT-02")
    parser.add_argument("--ct-03", action="store_true", help="Solo CT-03")
    parser.add_argument("--ct-04", action="store_true", help="Solo CT-04 (concurrencia)")
    parser.add_argument("--ct-05", action="store_true", help="Solo CT-05 (repetibilidad)")
    parser.add_argument("--requests", type=int, default=200, help="Número de solicitudes (default: 200)")
    parser.add_argument("--users", type=int, default=10, help="Número de usuarios para CT-04 (default: 10)")
    parser.add_argument("--duration", type=int, default=300, help="Duración CT-04 en segundos (default: 300)")
    parser.add_argument("--exec", type=int, default=3, help="Número de ejecuciones CT-05 (default: 3)")
    parser.add_argument("--interval", type=int, default=300, help="Intervalo entre ejecuciones CT-05 (default: 300s)")
    
    args = parser.parse_args()
    
    # Obtiene llave API
    api_key = os.getenv("ONVO_TEST_SECRET_KEY", "")
    if not api_key:
        print("[FAIL] Error: ONVO_TEST_SECRET_KEY no esta configurada")
        print("Ejecuta: python configurar_clave.py")
        sys.exit(1)
    
    # Inicializa tester
    tester = ONVOPerformanceTest(api_key, num_requests=args.requests)
    
    # Determina qué ejecutar
    run_all = args.all
    run_ct01 = args.ct_01 or run_all or not any([args.ct_02, args.ct_03, args.ct_04, args.ct_05])
    run_ct02 = args.ct_02 or run_all or not any([args.ct_01, args.ct_03, args.ct_04, args.ct_05])
    run_ct03 = args.ct_03 or run_all or not any([args.ct_01, args.ct_02, args.ct_04, args.ct_05])
    run_ct04 = args.ct_04 or run_all
    run_ct05 = args.ct_05 or run_all
    
    print("\n" + "="*70)
    print("SUITE DE PRUEBAS DE RENDIMIENTO - ONVO PAY API")
    print("="*70)
    print(f"Inicio: {datetime.now().isoformat()}")
    print(f"API Key: {api_key[:25]}...")
    print(f"Solicitudes por test: {args.requests}")
    print()
    
    try:
        if run_ct01 or run_ct02:
            if run_ct01:
                tester.ct_01_query_response_time()
            if run_ct02:
                tester.ct_02_creation_response_time()
        
        if run_ct03 and (tester.results.get("CT-01") or tester.results.get("CT-02")):
            tester.ct_03_stability()
        
        if run_ct04:
            print("\n[WARN] CT-04 requiere 10+ usuarios y ~5 minutos")
            response = input("Continuar? (s/n): ").strip().lower()
            if response in ("s", "si"):
                tester.ct_04_concurrency(num_users=args.users, duration_sec=args.duration)
        
        if run_ct05:
            print(f"\n[WARN] CT-05 requiere {args.exec} ejecuciones con intervalos de {args.interval}s")
            total_time = args.exec * args.interval
            print(f"   Tiempo total aproximado: {total_time/60:.0f} minutos")
            response = input("Continuar? (s/n): ").strip().lower()
            if response in ("s", "si"):
                tester.ct_05_repeatability(executions=args.exec, interval_sec=args.interval)
        
        # Imprime resumen
        tester._print_summary()
        
        # Guarda resultados
        filename = save_report(tester.results)
        
        print(f"\n[OK] Pruebas completadas en {datetime.now().isoformat()}")
        return 0
        
    except KeyboardInterrupt:
        print("\n\n[WARN] Pruebas interrumpidas por usuario")
        return 1
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
