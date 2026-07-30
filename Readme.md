"""# 🎫 **EVENTLIVE** - Sistema de Venta de Entradas

¡Bienvenido a **EVENTLIVE**! Esta es una aplicación web desarrollada en **Django** y **PostgreSQL** diseñada para la gestión y venta de entradas (tickets) para diferentes shows musicales, conciertos y obras de teatro.

---

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:
- Python (versión 3.10 o superior)
- PostgreSQL (versión 14 o superior)
- Git

---

## 🛠️ Guía de Instalación y Configuración

Sigue estos pasos detallados para configurar el entorno de desarrollo local.

### 1. Clonar el Repositorio
Primero, clona este proyecto en tu máquina local y accede al directorio:
```bash
git clone https://github.com/gonzalocabrera90/django-ticket.git
cd django-ticket

### 2. Crear y Activar el Entorno Virtual

Es altamente recomendable aislar las dependencias del proyecto utilizando un entorno virtual.

* **En Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate

```


* **En Windows:**
```bash
python -m venv venv
.\\venv\\Scripts\\activate

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
# django-ticket/settings.py

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


## 💻 Uso de la Aplicación

### Iniciar el Servidor de Desarrollo

Una vez completada la configuración, levanta el servidor local de Django:

*(Nota: Asegura que estas corriendo en tu computadora el servicio de PostgreSQL para guardar y usar la informacion`)*

```bash
python manage.py runserver

```

Abre tu navegador web e ingresa a: `http://127.0.0.1:8000/`


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

### Paso 2: Crear tu usuario administrador local
Crea una cuenta de superusuario para acceder al panel de administración de Django:
```bash
docker compose exec web python manage.py createsuperuser
```

## 🛑 Detener la Aplicación

Para apagar los contenedores y detener los servicios, ejecuta:
```bash
docker compose down
```