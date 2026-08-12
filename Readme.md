"""# 🎫 **EVENTLIVE** - Sistema de Venta de Entradas

¡Bienvenido a **EVENTLIVE**! Esta es una aplicación web desarrollada en **Django** y **PostgreSQL** diseñada para la gestión y venta de entradas (tickets) para diferentes shows musicales, conciertos y obras de teatro.

---

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:
- Python (versión 3.10 o superior)
- PostgreSQL (versión 14 o superior) o Docker
- Git

---

## 🛠️ Guía de Instalación y Configuración

Sigue estos pasos detallados para configurar el entorno de desarrollo local.

### 1. Clonar el Repositorio
Primero, clona este proyecto en tu máquina local y accede al directorio:
```bash
git clone https://github.com/gonzalocabrera1990/ticket-booking-platform.git
cd ticket-booking-platform

### 2. Crear y Activar el Entorno Virtual

Es altamente recomendable aislar las dependencias del proyecto utilizando un entorno virtual.

* **En Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate

```


* **En Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate

```



### 3. Instalar Dependencias de Django y PostgreSQL

Con el entorno virtual activo, instala Django junto con el adaptador para conectarse a PostgreSQL (`psycopg2` o `psycopg2-binary`) y demás librerías:

```bash
# Si el proyecto cuenta con un archivo requirements.txt, usa:
# pip install -r requirements.txt
# Sino....
pip install --upgrade pip
pip install django psycopg2-binary

```

### 4. Configurar la Base de Datos PostgreSQL

Abre tu terminal de PostgreSQL (`psql`) o tu herramienta de administración gráfica (como pgAdmin) y ejecuta los siguientes comandos para crear la base de datos y el usuario:

*(Nota: Asegura que estas corriendo en tu computadora el servicio de PostgreSQL para guardar y usar la informacion`)*

---

```sql
CREATE DATABASE eventlive_db;
CREATE USER eventlive_user WITH PASSWORD 'tu_contraseña_segura';
ALTER ROLE eventlive_user SET client_encoding TO 'utf8';
ALTER ROLE eventlive_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE eventlive_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE eventlive_db TO eventlive_user;

```

### 5. Configurar el Archivo `settings.py` de Django

Modifica el bloque `DATABASES` en el archivo `settings.py` de tu proyecto Django para conectarlo con la base de datos que acabas de crear:

```python
# config/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'eventlive_db',
        'USER': 'eventlive_user',
        'PASSWORD': 'tu_contraseña_segura',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

```

### 6. Ejecutar Migraciones de la Base de Datos

Crea la estructura de tablas necesaria en PostgreSQL ejecutando las migraciones nativas de Django:

```bash
python manage.py makemigrations
python manage.py migrate

```
El proyecto utiliza la libreria **django-cities-light** para cargar en la base de datos informacion util para elgir y guardar las direcciones de los usuarios.
En settings.py, en la propiedad CITIES_LIGHT_INCLUDE_COUNTRIES, debemos fijar los paises que se van a usar en la aplicacion. Dependiendo de los elegidos en esta lista, son los que guardara en la base de datos.

```python
# config/settings.py

CITIES_LIGHT_INCLUDE_COUNTRIES = ['AR']

```

Ya habiendo corrido python manage.py migrate, ejecuta:

```bash
python manage.py cities_light

```
Este comando tardara un tiempo ya que dependiendo de los paises usados en CITIES_LIGHT_INCLUDE_COUNTRIES, guardara en la base de datos los paises, sus provincias/estados/regiones, y sus ciudades.

### 7. Cargar Datos de Prueba (Seeds / Fixtures)

Para usar la aplicacion y probar la UI con informacion de la base de datos necesitamos poblarla con lugares y sectores, shows musicales, teatros y categorías iniciales. Corre el comando de carga de datos:

Comando para Linux
```bash
python manage.py shell < seeds/seed_completo.py

```

Comando para Windows
```bash
python manage.py shell -c "import seeds.seed_completo"

```

La aplicacion Admin de Django tambien esta en funcionamiento para agregar informacion, en base a los modelos que usa la base de datos.
Necesitamos crear un usuario con permisos para poder usarla. Debemos correr el siguiente comando y llenar los datos que te pide la consola:

```bash
python manage.py createsuperuser

```

## 💻 Uso de la Aplicación

### Iniciar el Servidor de Desarrollo

Una vez completada la configuración, levanta el servidor local de Django:

*(Nota: Asegura que estas corriendo en tu computadora el servicio de PostgreSQL para guardar y usar la informacion`)*

```bash
python manage.py runserver

```

Abre tu navegador web e ingresa a: `http://127.0.0.1:8000/`

### Simulacion de reserva de entradas
Para comprobar el funcionamiento del flujo de compra se implemento un archivo para simular reservas.
Genera ordenes de compras vencidas. Se configura obteniendo informacion de la base de datos.

Comando para Linux
```bash
python manage.py shell < seeds/seed_purchase_due.py

```
Comando para Windows
```bash
python manage.py shell -c "import seeds.seed_purchase_due"

```
Luego verificamos el conteo de entradas del sector para ver si disminuyo.
Al iniciar un proceso de compra el sistema reserva entradas hasta concretarla.
Si la compra falla necesitamos liberar esas entradas nuevamente para la venta.
Para ello ejecutamos:

```bash
python manage.py liberar_reservas

```
Limpia las compras fallidas verificando el tiempo transcurrido desde la reserva.


### Iniciar la aplicacion en Docker

# 🚀 Despliegue del Proyecto con Docker

Este documento contiene las instrucciones necesarias para levantar el entorno de desarrollo local utilizando Docker y configurar la base de datos de Django.

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:
* [Docker Desktop](https://docker.com)
* Docker Compose (incluido en las versiones modernas de Docker)

---

## 📦 1. Iniciar la Aplicación

Elige una de las siguientes opciones para levantar los contenedores según tus necesidades:

### Opción A: Construir e iniciar en segundo plano (Recomendado)
Usa este comando la primera vez o cuando realices cambios en el `Dockerfile` o en las dependencias:
```bash
docker compose up --build -d
```

### Opción B: Construir e iniciar viendo los logs en tiempo real
```bash
docker compose up --build
```

### Opción C: Iniciar contenedores ya construidos en segundo plano
```bash
docker compose up -d
```

---

## ⚙️ 2. Configuración Inicial (Base de Datos y Datos)

Una vez que los contenedores estén corriendo en segundo plano, ejecuta los siguientes comandos en tu terminal para preparar la aplicación:

### Paso 1: Crear las tablas físicas en Postgres
Ejecuta las migraciones de Django para crear la estructura de la base de datos:
```bash
docker compose exec web python manage.py migrate
```

### Paso 2: Cargar las ciudades
Popula la base de datos con la información geográfica necesaria:
```bash
docker compose exec web python manage.py cities_light
```

### Paso 3: Crear tu usuario administrador local
Crea una cuenta de superusuario para acceder al panel de administración de Django:
```bash
docker compose exec web python manage.py createsuperuser
```

### Paso 4: Correr el seed completo de datos
Llena la base de datos con información de prueba inicial ejecutando el script de preparación:
```bash
docker compose exec -T web python manage.py shell < seeds/seed_completo.py
```

---

## 🛑 Detener la Aplicación

Para apagar los contenedores y detener los servicios, ejecuta:
```bash
docker compose down
```
