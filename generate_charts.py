#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para capturar los gr??ficos existentes de Locust
Funciona con Locust ya ejecutado y con datos disponibles
"""

import subprocess
import time
import json
import os
import sys
from pathlib import Path

# Configurar encoding para Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def generate_html_report():
    """Genera un HTML con los gr??ficos de los resultados"""
    
    # Leer el ??ltimo archivo JSON de resultados
    json_files = list(Path(".").glob("test_results_*.json"))
    if not json_files:
        print("[!] No se encontraron archivos de resultados JSON")
        return
    
    latest_json = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"[*] Usando archivo: {latest_json}")
    
    with open(latest_json) as f:
        data = json.load(f)
    
    # Generar gr??ficos con matplotlib
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Crear carpeta de gr??ficos
        Path("graficos").mkdir(exist_ok=True)
        
        # Gr??fico 1: Comparativa de criterios
        fig, ax = plt.subplots(figsize=(12, 6))
        criterios = ["CT-01", "CT-02", "CT-03", "CT-04", "CT-05"]
        verdicts = [
            data.get("CT-01", {}).get("clientes", {}).get("verdict", "?"),
            data.get("CT-02", {}).get("verdict", "?"),
            data.get("CT-03", {}).get("CT-01_clientes", {}).get("verdict", "?"),
            data.get("CT-04", {}).get("verdict", "?"),
            data.get("CT-05", {}).get("clientes", {}).get("verdict", "?"),
        ]
        
        colores = ["red" if "FAIL" in v else "green" for v in verdicts]
        y_pos = np.arange(len(criterios))
        
        ax.barh(y_pos, [1]*len(criterios), color=colores, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(criterios)
        ax.set_xlabel("Resultado")
        ax.set_title("Resultados de Criterios de Aceptaci??n", fontsize=14, fontweight="bold")
        ax.set_xlim(0, 1.2)
        
        # Agregar etiquetas
        for i, (c, v) in enumerate(zip(criterios, verdicts)):
            status = "PASS" if "PASS" in v else "FAIL"
            ax.text(0.5, i, status, ha="center", va="center", fontweight="bold", color="white", fontsize=12)
        
        plt.tight_layout()
        plt.savefig("graficos/01_resultados_criterios.png", dpi=150, bbox_inches='tight')
        print("[OK] Grafico 1: Resultados de criterios")
        plt.close()
        
        # Grafico 2: Latencias CT-01 vs CT-02
        if "CT-01" in data and "CT-02" in data:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # CT-01
            ct01_stats = data["CT-01"]["clientes"]["stats"]
            labels1 = ["p50", "p95", "p99"]
            values1 = [ct01_stats["p50"], ct01_stats["p95"], ct01_stats["p99"]]
            limits1 = [400, 800, None]  # L??mites
            
            x = np.arange(len(labels1))
            ax1.bar(x, values1, color="steelblue", alpha=0.8, label="Medici??n")
            ax1.axhline(y=400, color="red", linestyle="--", linewidth=2, label="L??mite p50 (400ms)")
            ax1.axhline(y=800, color="orange", linestyle="--", linewidth=2, label="L??mite p95 (800ms)")
            ax1.set_ylabel("Latencia (ms)")
            ax1.set_title("CT-01: GET /v1/customers", fontsize=12, fontweight="bold")
            ax1.set_xticks(x)
            ax1.set_xticklabels(labels1)
            ax1.legend()
            ax1.grid(axis="y", alpha=0.3)
            
            # CT-02
            ct02_stats = data["CT-02"]["stats"]
            labels2 = ["p95", "p99"]
            values2 = [ct02_stats["p95"], ct02_stats["p99"]]
            limits2 = [1500, 2500]  # L??mites
            
            x2 = np.arange(len(labels2))
            ax2.bar(x2, values2, color="seagreen", alpha=0.8, label="Medici??n")
            ax2.axhline(y=1500, color="orange", linestyle="--", linewidth=2, label="L??mite p95 (1500ms)")
            ax2.axhline(y=2500, color="red", linestyle="--", linewidth=2, label="L??mite p99 (2500ms)")
            ax2.set_ylabel("Latencia (ms)")
            ax2.set_title("CT-02: POST /v1/payment-intents", fontsize=12, fontweight="bold")
            ax2.set_xticks(x2)
            ax2.set_xticklabels(labels2)
            ax2.legend()
            ax2.grid(axis="y", alpha=0.3)
            
            plt.tight_layout()
            plt.savefig("graficos/02_latencias_ct01_ct02.png", dpi=150, bbox_inches='tight')
            print("[???] Gr??fico 2: Latencias CT-01 vs CT-02")
            plt.close()
        
        # Gr??fico 3: Degradaci??n en CT-04
        if "CT-04" in data:
            ct04 = data["CT-04"]
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # GET Clientes
            baseline_get = ct04["baseline"]["clientes_p95"]
            concurrent_get = ct04["concurrent"]["clientes"]["p95"]
            degradation_get = ct04["p95_increase"]["clientes"] * 100
            
            ax1.bar(["Baseline", "Bajo Carga"], [baseline_get, concurrent_get], color=["green", "red"], alpha=0.7)
            ax1.axhline(y=baseline_get * 1.3, color="orange", linestyle="--", linewidth=2, label="L??mite +30%")
            ax1.set_ylabel("Latencia p95 (ms)")
            ax1.set_title(f"CT-04: GET /v1/customers\nDegradaci??n: {degradation_get:.1f}%", fontsize=12, fontweight="bold")
            ax1.legend()
            ax1.grid(axis="y", alpha=0.3)
            
            # POST Creaci??n
            baseline_post = ct04["baseline"]["creacion_p95"]
            concurrent_post = ct04["concurrent"]["creacion"]["p95"]
            degradation_post = ct04["p95_increase"]["creacion"] * 100
            
            ax2.bar(["Baseline", "Bajo Carga"], [baseline_post, concurrent_post], color=["green", "orange"], alpha=0.7)
            ax2.axhline(y=baseline_post * 1.3, color="red", linestyle="--", linewidth=2, label="L??mite +30%")
            ax2.set_ylabel("Latencia p95 (ms)")
            ax2.set_title(f"CT-04: POST /v1/payment-intents\nDegradaci??n: {degradation_post:.1f}%", fontsize=12, fontweight="bold")
            ax2.legend()
            ax2.grid(axis="y", alpha=0.3)
            
            plt.tight_layout()
            plt.savefig("graficos/03_degradacion_ct04.png", dpi=150, bbox_inches='tight')
            print("[???] Gr??fico 3: Degradaci??n en CT-04")
            plt.close()
        
        # Gr??fico 4: Varianza en CT-05
        if "CT-05" in data:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # GET Clientes
            clientes_values = data["CT-05"]["clientes"]["p95_values"]
            varianza_clientes = data["CT-05"]["clientes"]["variance"] * 100
            
            executions = ["Ejecuci??n 1", "Ejecuci??n 2", "Ejecuci??n 3"]
            ax1.plot(executions, clientes_values, marker="o", linewidth=2, markersize=8, color="steelblue")
            ax1.axhline(y=np.mean(clientes_values), color="red", linestyle="--", label="Media")
            ax1.fill_between(range(len(executions)), 
                            np.mean(clientes_values) - np.std(clientes_values),
                            np.mean(clientes_values) + np.std(clientes_values),
                            alpha=0.2, color="steelblue")
            ax1.set_ylabel("Latencia p95 (ms)")
            ax1.set_title(f"CT-05: GET /v1/customers\nVarianza: {varianza_clientes:.1f}%", fontsize=12, fontweight="bold")
            ax1.legend()
            ax1.grid(alpha=0.3)
            
            # POST Creaci??n
            creacion_values = data["CT-05"]["creacion"]["p95_values"]
            varianza_creacion = data["CT-05"]["creacion"]["variance"] * 100
            
            ax2.plot(executions, creacion_values, marker="s", linewidth=2, markersize=8, color="seagreen")
            ax2.axhline(y=np.mean(creacion_values), color="red", linestyle="--", label="Media")
            ax2.fill_between(range(len(executions)),
                            np.mean(creacion_values) - np.std(creacion_values),
                            np.mean(creacion_values) + np.std(creacion_values),
                            alpha=0.2, color="seagreen")
            ax2.set_ylabel("Latencia p95 (ms)")
            ax2.set_title(f"CT-05: POST /v1/payment-intents\nVarianza: {varianza_creacion:.1f}%", fontsize=12, fontweight="bold")
            ax2.legend()
            ax2.grid(alpha=0.3)
            
            plt.tight_layout()
            plt.savefig("graficos/04_varianza_ct05.png", dpi=150, bbox_inches='tight')
            print("[???] Gr??fico 4: Varianza en CT-05")
            plt.close()
        
        print()
        print("=" * 70)
        print("GRAFICOS GENERADOS EN CARPETA 'graficos/'")
        print("=" * 70)
        print()
        print("Archivos:")
        print("  ??? 01_resultados_criterios.png       - Resumen de verdicts")
        print("  ??? 02_latencias_ct01_ct02.png        - Comparativa de endpoints")
        print("  ??? 03_degradacion_ct04.png           - Impacto de concurrencia")
        print("  ??? 04_varianza_ct05.png              - Consistencia entre ejecuciones")
        print()
        
    except ImportError:
        print("[!] matplotlib no est?? instalado. Instalando...")
        subprocess.run(["python", "-m", "pip", "install", "matplotlib", "-q"])
        print("[???] matplotlib instalado. Ejecuta el script nuevamente.")


if __name__ == "__main__":
    try:
        generate_html_report()
    except Exception as e:
        print(f"[x] Error: {e}")
        import traceback
        traceback.print_exc()


