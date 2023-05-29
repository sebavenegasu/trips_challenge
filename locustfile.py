from locust import HttpUser, task, between, constant_pacing

class MyUser(HttpUser):
    wait_time = between(1, 3)  # Tiempo de espera entre solicitudes

    @task
    def load_csv(self):
        self.client.post("/load_csv")  # Llamada al endpoint de carga de datos CSV

    @task
    def load_grouped(self):
        self.client.post("/load_grouped")  # Llamada al endpoint de carga de datos agrupados

    @task
    def get_weekly_average(self):
        self.client.post("/weekly_average", json={
            "min_longitude": 0.0,
            "max_longitude": 10.0,
            "min_latitude": 0.0,
            "max_latitude": 10.0,
            "region": "Region A"
        })  # Llamada al endpoint de promedio semanal

    def on_start(self):
        self.client.post("/load_csv")  # Realiza la carga inicial de datos CSV

