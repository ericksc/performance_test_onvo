import os

from locust import HttpUser, constant_pacing, task

from destino import HOST, RUTA


class ConsultaONVO(HttpUser):
    host = HOST
    wait_time = constant_pacing(2)

    @task
    def listar_dominios(self):
        clave = os.getenv("ONVO_TEST_SECRET_KEY", "")
        with self.client.get(
            HOST + RUTA,
            headers={
                "Authorization": f"Bearer {clave}",
                "Accept": "application/json",
            },
            name="GET /v1/payment-method-domains",
            catch_response=True,
            allow_redirects=False,
            timeout=(5, 10),
        ) as respuesta:
            if respuesta.status_code != 200:
                estado = respuesta.status_code or "sin respuesta"
                respuesta.failure(f"Se esperaba HTTP 200. Resultado: {estado}")
        if respuesta.status_code in (401, 403, 429):
            self.environment.runner.quit()
