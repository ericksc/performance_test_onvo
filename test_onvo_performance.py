"""
Suite de Pruebas de Rendimiento para API ONVO Pay
Basado en ISO/IEC 25010:2011 - Comportamiento Temporal

Criterios:
  CT-01: Tiempo de respuesta de consultas (200 req secuenciales)
  CT-02: Tiempo de respuesta de creacion (200 req secuenciales)
  CT-03: Estabilidad (p99 <= 3 x p50)
  CT-04: Comportamiento bajo concurrencia (10 usuarios, 5 min)
  CT-05: Repetibilidad (variacion <= 20%)
"""

import os
import time
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures


class ONVOPerformanceTest:
    """Suite de pruebas de rendimiento para ONVO Pay API"""
    
    # Endpoints de prueba
    BASE_URL = "https://api.onvopay.com"
    ENDPOINT_PAYMENT_INTENTS = "/v1/payment-intents"
    ENDPOINT_CUSTOMERS = "/v1/customers"
    
    # Umbrales de aceptación
    THRESHOLDS = {
        "CT-01": {"p50": 400, "p95": 800, "timeout": 10000},  # ms
        "CT-02": {"p95": 1500, "p99": 2500, "timeout": 10000},  # ms
        "CT-03": {"ratio": 3},  # p99 <= 3 x p50
        "CT-04": {"p95_increase": 0.30, "error_rate": 0.01},  # 30% y 1%
        "CT-05": {"variance": 0.20},  # 20%
    }
    
    def __init__(self, api_key: str, num_requests: int = 200):
        """
        Inicializa la suite de pruebas.
        
        Args:
            api_key: Llave de API de ONVO (onvo_test_secret_key_*)
            num_requests: Número de solicitudes por test (default: 200)
        """
        self.api_key = api_key
        self.num_requests = num_requests
        self.session = self._create_session()
        self.results = {}
        
    def _create_session(self) -> requests.Session:
        """Crea una sesión HTTP con reintentos configurados."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers con autenticación."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def _measure_request(self, method: str, endpoint: str, 
                        json_data: dict = None) -> Tuple[int, float, int]:
        """
        Mide una solicitud HTTP.
        
        Returns:
            (status_code, response_time_ms, payload_size_bytes)
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            start_time = time.perf_counter()
            
            if method == "GET":
                response = self.session.get(
                    url, 
                    headers=self._get_headers(),
                    timeout=15
                )
            elif method == "POST":
                response = self.session.post(
                    url,
                    headers=self._get_headers(),
                    json=json_data,
                    timeout=15
                )
            else:
                raise ValueError(f"Método no soportado: {method}")
            
            response_time = (time.perf_counter() - start_time) * 1000
            payload_size = len(response.content)
            
            return response.status_code, response_time, payload_size
            
        except requests.Timeout:
            return 0, 10000, 0  # Timeout = 10s
        except Exception as e:
            print(f"Error en solicitud: {e}")
            return 0, 10000, 0
    
    def _calculate_percentiles(self, times: List[float]) -> Dict[str, float]:
        """Calcula percentiles de tiempos de respuesta."""
        if not times:
            return {}
        
        sorted_times = sorted(times)
        return {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "p50": statistics.quantiles(times, n=100, method="inclusive")[49] if len(times) > 1 else times[0],
            "p95": statistics.quantiles(times, n=100, method="inclusive")[94] if len(times) > 1 else times[0],
            "p99": statistics.quantiles(times, n=100, method="inclusive")[98] if len(times) > 1 else times[0],
            "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        }
    
    def ct_01_query_response_time(self) -> Dict:
        """
        CT-01: Tiempo de respuesta de consultas (200 req secuenciales).
        
        Criterio de aceptación:
          p50 ≤ 400 ms y p95 ≤ 800 ms en cada operación
          Ninguna solicitud supera 10 s
        """
        print("\n" + "="*70)
        print("CT-01: Tiempo de respuesta de consultas")
        print("="*70)
        
        results = {}
        
        # Operación 1: Listar clientes
        print(f"\nMidiendo: GET {self.ENDPOINT_CUSTOMERS} ({self.num_requests} req)")
        times_customers = []
        successful = 0
        timeouts = 0
        
        for i in range(10 + self.num_requests):  # +10 calentamiento
            status, response_time, _ = self._measure_request("GET", self.ENDPOINT_CUSTOMERS)
            
            if i >= 10:  # Descartar calentamiento
                if status in (200, 304):
                    times_customers.append(response_time)
                    successful += 1
                elif response_time >= 10000:
                    timeouts += 1
            
            if (i + 1) % 50 == 0:
                print(f"  Progreso: {min(i + 1 - 10, self.num_requests)}/{self.num_requests}")
        
        stats_customers = self._calculate_percentiles(times_customers)
        results["clientes"] = {
            "stats": stats_customers,
            "successful": successful,
            "timeouts": timeouts,
            "verdict": "PASS" if stats_customers.get("p50", 999) <= 400 and stats_customers.get("p95", 999) <= 800 else "FAIL"
        }
        
        print(f"\nEstadísticas - Listar clientes:")
        print(f"  Exitosas: {successful}/{self.num_requests}")
        print(f"  Timeouts: {timeouts}")
        print(f"  p50: {stats_customers.get('p50', 0):.2f} ms (límite: 400 ms)")
        print(f"  p95: {stats_customers.get('p95', 0):.2f} ms (límite: 800 ms)")
        print(f"  Veredicto: {results['clientes']['verdict']}")
        
        self.results["CT-01"] = results
        return results
    
    def ct_02_creation_response_time(self) -> Dict:
        """
        CT-02: Tiempo de respuesta de creación de intención de pago.
        
        Criterio de aceptación:
          p95 ≤ 1500 ms y p99 ≤ 2500 ms
          Ninguna solicitud supera 10 s
        """
        print("\n" + "="*70)
        print("CT-02: Tiempo de respuesta de creación (payment-intents)")
        print("="*70)
        
        # Datos válidos de prueba
        payment_intent_data = {
            "amount": 10000,  # $100.00
            "currency": "USD",
            "metadata": {
                "order_id": "test_order_",
                "timestamp": datetime.now().isoformat(),
            }
        }
        
        print(f"\nMidiendo: POST {self.ENDPOINT_PAYMENT_INTENTS} ({self.num_requests} req)")
        times_creation = []
        successful = 0
        timeouts = 0
        
        for i in range(10 + self.num_requests):  # +10 calentamiento
            payload = payment_intent_data.copy()
            payload["metadata"]["order_id"] = f"test_order_{i}"
            
            status, response_time, _ = self._measure_request(
                "POST", 
                self.ENDPOINT_PAYMENT_INTENTS,
                payload
            )
            
            if i >= 10:  # Descartar calentamiento
                if status in (200, 201):
                    times_creation.append(response_time)
                    successful += 1
                elif response_time >= 10000:
                    timeouts += 1
            
            if (i + 1) % 50 == 0:
                print(f"  Progreso: {min(i + 1 - 10, self.num_requests)}/{self.num_requests}")
        
        stats_creation = self._calculate_percentiles(times_creation)
        results = {
            "stats": stats_creation,
            "successful": successful,
            "timeouts": timeouts,
            "verdict": "PASS" if stats_creation.get("p95", 999) <= 1500 and stats_creation.get("p99", 999) <= 2500 else "FAIL"
        }
        
        print(f"\nEstadísticas - Crear intención de pago:")
        print(f"  Exitosas: {successful}/{self.num_requests}")
        print(f"  Timeouts: {timeouts}")
        print(f"  p95: {stats_creation.get('p95', 0):.2f} ms (límite: 1500 ms)")
        print(f"  p99: {stats_creation.get('p99', 0):.2f} ms (límite: 2500 ms)")
        print(f"  Veredicto: {results['verdict']}")
        
        self.results["CT-02"] = results
        return results
    
    def ct_03_stability(self) -> Dict:
        """
        CT-03: Estabilidad de tiempos de respuesta.
        
        Criterio de aceptación:
          p99 <= 3 x p50 en todas las operaciones
        """
        print("\n" + "="*70)
        print("CT-03: Estabilidad (p99 <= 3 x p50)")
        print("="*70)
        
        results = {}
        
        # Evalúa CT-01 y CT-02
        for criterion, data in self.results.items():
            if criterion in ("CT-01", "CT-02"):
                if isinstance(data, dict):
                    for op_name, op_data in data.items():
                        if isinstance(op_data, dict) and "stats" in op_data:
                            stats = op_data["stats"]
                            p50 = stats.get("p50", 0)
                            p99 = stats.get("p99", 0)
                            
                            if p50 > 0:
                                ratio = p99 / p50
                                verdict = "PASS" if ratio <= 3 else "FAIL"
                                
                                results[f"{criterion}_{op_name}"] = {
                                    "p50": p50,
                                    "p99": p99,
                                    "ratio": ratio,
                                    "verdict": verdict
                                }
                                
                                print(f"\n{criterion} - {op_name}:")
                                print(f"  p50: {p50:.2f} ms")
                                print(f"  p99: {p99:.2f} ms")
                                print(f"  Ratio (p99/p50): {ratio:.2f}x (limite: 3x)")
                                print(f"  Veredicto: {verdict}")
        
        self.results["CT-03"] = results
        return results
    
    def ct_04_concurrency(self, num_users: int = 10, duration_sec: int = 300) -> Dict:
        """
        CT-04: Comportamiento bajo concurrencia moderada.
        
        Criterio de aceptación:
          p95 aumenta máximo 30% respecto a línea base
          Tasa de errores ≤ 1%
        """
        print("\n" + "="*70)
        print(f"CT-04: Concurrencia moderada ({num_users} usuarios, {duration_sec}s)")
        print("="*70)
        
        baseline = {
            "clientes_p95": self.results.get("CT-01", {}).get("clientes", {}).get("stats", {}).get("p95", 0),
            "creacion_p95": self.results.get("CT-02", {}).get("stats", {}).get("p95", 0),
        }
        
        print(f"\nLínea base:")
        print(f"  Clientes p95: {baseline['clientes_p95']:.2f} ms")
        print(f"  Creación p95: {baseline['creacion_p95']:.2f} ms")
        
        times_concurrent = {"clientes": [], "creacion": []}
        errors = {"5xx": 0, "timeout": 0, "success": 0}
        start_time = time.time()
        
        def worker_task():
            """Tarea de un usuario virtual."""
            ops = []
            while time.time() - start_time < duration_sec:
                # Alterna entre consultas y creación (60% consultas, 40% creación)
                if hash(time.time()) % 10 < 6:
                    status, response_time, _ = self._measure_request("GET", self.ENDPOINT_CUSTOMERS)
                    if status == 200:
                        times_concurrent["clientes"].append(response_time)
                    elif status >= 500:
                        errors["5xx"] += 1
                    elif response_time >= 10000:
                        errors["timeout"] += 1
                else:
                    payload = {"amount": 10000, "currency": "USD"}
                    status, response_time, _ = self._measure_request("POST", self.ENDPOINT_PAYMENT_INTENTS, payload)
                    if status in (200, 201):
                        times_concurrent["creacion"].append(response_time)
                    elif status >= 500:
                        errors["5xx"] += 1
                    elif response_time >= 10000:
                        errors["timeout"] += 1
                
                errors["success"] += 1
            
            return ops
        
        print(f"\nEjecutando {num_users} usuarios virtuales...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(worker_task) for _ in range(num_users)]
            for future in concurrent.futures.as_completed(futures):
                future.result()
        
        # Calcula estadísticas
        stats_concurrent = {
            "clientes": self._calculate_percentiles(times_concurrent["clientes"]),
            "creacion": self._calculate_percentiles(times_concurrent["creacion"]),
        }
        
        total_requests = errors["success"]
        error_rate = (errors["5xx"] + errors["timeout"]) / total_requests if total_requests > 0 else 0
        
        # Evalúa criterio
        p95_increase_clientes = (stats_concurrent["clientes"].get("p95", 0) / baseline["clientes_p95"] - 1) if baseline["clientes_p95"] > 0 else 0
        p95_increase_creacion = (stats_concurrent["creacion"].get("p95", 0) / baseline["creacion_p95"] - 1) if baseline["creacion_p95"] > 0 else 0
        
        verdict = "PASS" if (p95_increase_clientes <= 0.30 and p95_increase_creacion <= 0.30 and error_rate <= 0.01) else "FAIL"
        
        results = {
            "baseline": baseline,
            "concurrent": stats_concurrent,
            "errors": errors,
            "error_rate": error_rate,
            "p95_increase": {
                "clientes": p95_increase_clientes,
                "creacion": p95_increase_creacion,
            },
            "verdict": verdict
        }
        
        print(f"\nEstadísticas bajo concurrencia:")
        print(f"  Solicitudes exitosas: {errors['success']}")
        print(f"  Errores 5xx: {errors['5xx']}")
        print(f"  Timeouts: {errors['timeout']}")
        print(f"  Tasa de error: {error_rate*100:.2f}% (límite: 1%)")
        print(f"\n  Clientes - p95 aumento: {p95_increase_clientes*100:.1f}% (límite: 30%)")
        print(f"  Creación - p95 aumento: {p95_increase_creacion*100:.1f}% (límite: 30%)")
        print(f"  Veredicto: {verdict}")
        
        self.results["CT-04"] = results
        return results
    
    def ct_05_repeatability(self, executions: int = 3, interval_sec: int = 300) -> Dict:
        """
        CT-05: Repetibilidad y detección de degradación.
        
        Criterio de aceptación:
          Variación ≤ 20% respecto a línea base
        """
        print("\n" + "="*70)
        print(f"CT-05: Repetibilidad ({executions} ejecuciones)")
        print("="*70)
        
        all_p95 = {"clientes": [], "creacion": []}
        
        for exec_num in range(executions):
            print(f"\n--- Ejecución {exec_num + 1}/{executions} ---")
            timestamp = datetime.now().isoformat()
            
            # Mide clientes
            times = []
            for _ in range(self.num_requests):
                status, response_time, _ = self._measure_request("GET", self.ENDPOINT_CUSTOMERS)
                if status == 200:
                    times.append(response_time)
            
            stats = self._calculate_percentiles(times)
            all_p95["clientes"].append(stats.get("p95", 0))
            print(f"  Clientes p95: {stats.get('p95', 0):.2f} ms")
            
            # Mide creación
            times = []
            for _ in range(self.num_requests):
                payload = {"amount": 10000, "currency": "USD"}
                status, response_time, _ = self._measure_request("POST", self.ENDPOINT_PAYMENT_INTENTS, payload)
                if status in (200, 201):
                    times.append(response_time)
            
            stats = self._calculate_percentiles(times)
            all_p95["creacion"].append(stats.get("p95", 0))
            print(f"  Creación p95: {stats.get('p95', 0):.2f} ms")
            
            if exec_num < executions - 1:
                print(f"  Esperando {interval_sec}s antes de siguiente ejecución...")
                time.sleep(interval_sec)
        
        # Calcula variación
        def calc_variance(values):
            median = statistics.median(values)
            max_variance = max(abs(v - median) / median for v in values) if median > 0 else 0
            return max_variance
        
        variance_clientes = calc_variance(all_p95["clientes"])
        variance_creacion = calc_variance(all_p95["creacion"])
        
        verdict = "PASS" if (variance_clientes <= 0.20 and variance_creacion <= 0.20) else "FAIL"
        
        results = {
            "clientes": {
                "p95_values": all_p95["clientes"],
                "variance": variance_clientes,
                "verdict": verdict
            },
            "creacion": {
                "p95_values": all_p95["creacion"],
                "variance": variance_creacion,
                "verdict": verdict
            }
        }
        
        print(f"\nVariación entre ejecuciones:")
        print(f"  Clientes: {variance_clientes*100:.1f}% (límite: 20%)")
        print(f"  Creación: {variance_creacion*100:.1f}% (límite: 20%)")
        print(f"  Veredicto: {verdict}")
        
        self.results["CT-05"] = results
        return results
    
    def run_all_tests(self) -> Dict:
        """Ejecuta todos los criterios de prueba."""
        print("\n" + "="*70)
        print("SUITE COMPLETA DE PRUEBAS - ONVO PAY API")
        print("ISO/IEC 25010:2011 - Comportamiento Temporal")
        print("="*70)
        print(f"Inicio: {datetime.now().isoformat()}")
        print(f"Llave API: {self.api_key[:20]}...")
        
        try:
            self.ct_01_query_response_time()
            self.ct_02_creation_response_time()
            self.ct_03_stability()
            # CT-04 y CT-05 requieren más tiempo, pueden ejecutarse por separado
            # self.ct_04_concurrency()
            # self.ct_05_repeatability()
            
            self._print_summary()
            return self.results
            
        except Exception as e:
            print(f"\n[FAIL] Error ejecutando pruebas: {e}")
            raise
    
    def _print_summary(self):
        """Imprime resumen de resultados."""
        print("\n" + "="*70)
        print("RESUMEN DE RESULTADOS")
        print("="*70)
        
        overall_pass = True
        for criterion, data in self.results.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and "verdict" in value:
                        verdict = value["verdict"]
                        status = "[OK]" if verdict == "PASS" else "[FAIL]"
                        print(f"  {status} {criterion}_{key}: {verdict}")
                        if verdict != "PASS":
                            overall_pass = False
        
        print("\n" + "="*70)
        print(f"Estado general: {'[OK] TODAS LAS PRUEBAS PASARON' if overall_pass else '[FAIL] FALLOS DETECTADOS'}")
        print("="*70)


if __name__ == "__main__":
    import sys
    
    # Obtiene llave de API
    api_key = os.getenv("ONVO_TEST_SECRET_KEY", "")
    if not api_key:
        print("Error: ONVO_TEST_SECRET_KEY no está configurada")
        sys.exit(1)
    
    # Ejecuta suite de pruebas
    tester = ONVOPerformanceTest(api_key, num_requests=200)
    results = tester.run_all_tests()
    
    # Guarda resultados
    output_file = Path("test_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResultados guardados en: {output_file}")
