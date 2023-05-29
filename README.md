# Proyecto de NeuralWorks

Este proyecto es una solución al problema planteado por NeuralWorks en el que se exploran los patrones de movimiento de las personas para optimizar el transporte público. El proyecto está construido con FastAPI y utiliza PostGIS como base de datos. La aplicación está dockerizada y también se incluye una interfaz básica en HTML para interactuar con ella. Y al final de este README una explicacion del diagrama de GCP.

## Cómo Ejecutar el Proyecto

0. Es necesario tener instalado Docker y Locust. Y un .env como .env_example con la variable de entorno.
1. Construir el proyecto con Docker: `docker-compose build`
2. Iniciar el proyecto: `docker-compose up`
3. Abrir la interfaz en el navegador: http://localhost:8080/static/index.html
4. Para usar Locust, con el proyecto en ejecución, abre otra terminal y ejecuta: `locust -f locustfile.py --host=http://localhost:8080` e ingresa a http://localhost:8089

5. Puede que al correr el docker-compose up haya un error porque la aplicacion no espera que la base de datos empiece a correr. En ese caso, correr el docker-compose up de nuevo. (creo que esto se puede solucionar con un script wait-for-it.sh pero no me quise complicar mucho)
6. Con `docker-compose down -v` se detiene el proyecto y se eliminan los volumenes de la base de datos.
## Tecnologías Utilizadas

- **FastAPI**: Elegí utilizar FastAPI debido a su rápido desarrollo y su eficiencia para construir APIs.
- **PostGIS**: Esta es una extensión de PostgreSQL que está especializada en cálculos geográficos, lo que es esencial para este proyecto.

## Solución Propuesta

1. Para cargar los datos del CSV en la base de datos, creé un endpoint. Aunque en una aplicación real esto podría no ser práctico, es una solución fácil de modificar si es necesario.
2. Para agrupar los viajes, utilicé las funciones de PostGIS, agrupando los viajes que estuvieran dentro de un rango de 1 grado de latitud y longitud. Esto lo hice creando una "grid" con ST_SnapToGrid de GeoAlchemy y asignando los puntos a cada celda. Además, los viajes son considerados similares si están dentro de 1 hora de diferencia.
3. Para calcular el promedio semanal de viajes, creé un endpoint que toma un promedio semanal y una bounding box definida por dos puntos. Para ello, utilicé las funciones ST_MakeEnvelope para crear la bounding box y ST_Within para verificar si los puntos están dentro de la bounding box.
4. Para observar la ingesta de datos en tiempo real, implementé un WebSocket y una función personalizada en la base de datos que notifica cada vez que se agrega una fila.
5. Para probar la escalabilidad de la aplicación, utilicé Locust para simular muchas solicitudes a la aplicación. Esto se puede ver en la interfaz gráfica de Locust.


## Posibles Mejoras

- Implementar una base de datos de prueba para facilitar el desarrollo y las pruebas y que el testing no sea tan demandante en el sistema.
- Desarrollar pruebas más robustas para asegurar la escalabilidad de la solución.
- Cargar los datos de manera más ordenada, en lugar de a través de un endpoint, podría hacerse a través de una interfaz.
- Crear una interfaz de usuario más amigable y con un diseño más atractivo.


## Arquitectura en Google Cloud Platform (GCP)

La arquitectura del diagrama esta pensada para ser escalable y simple.

A continuación se detalla cada componente:

1. **Cloud Storage**: Almacena los archivos CSV que contienen los datos de los viajes. Estos archivos son cargados en la base de datos PostGIS a través de la aplicación FastAPI. De esta forma se pueden cargar archivos mucho más grandes.

2. **Cloud Run**: Contiene la aplicación FastAPI desplegada en un contenedor Docker.

3. **Cloud SQL**: Servicio administrado que facilita la gestión de bases de datos relacionales en la nube. Se conecta con la base de datos PostGIS con la aplicación FastAPI en Cloud Run.

4. **Cloud Scheduler / Cloud Functions**: Automatiza el proceso de ingestión de datos. Cloud Scheduler desencadena una Cloud Function a intervalos programados que llama al endpoint de ingestión de datos en la aplicación FastAPI. Para asi periodicamente cargar los datos en la base de datos.

5. **Cloud Pub/Sub**: Genera eventos de estado para informar sobre el estado de la ingesta de datos en tiempo real. Estos eventos son enviados y recibidos por la aplicación FastAPI y enviados a los clientes a través de WebSocket.

6. **Stackdriver**: Permite registrar y monitorizar las operaciones de la aplicación, lo cual es esencial para identificar problemas rápidamente y garantizar un buen rendimiento. Stackdriver se integra con Cloud Run y Cloud SQL.

7. **Cloud Load Balancing**: Distribuye las solicitudes a la aplicación FastAPI de manera equilibrada. Este servicio interactúa directamente con el usuario final y la aplicación en Cloud Run.
