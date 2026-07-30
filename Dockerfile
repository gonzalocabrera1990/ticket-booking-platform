# Usa una imagen oficial de Python
FROM python:3.13-slim

# Evita que Python escriba archivos .pyc y asegura que los logs salgan directo a la terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Setea el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para psycopg2 (PostgreSQL)
# 🔴 ESTO ES CRUCIAL PARA POSTGRESQL:
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala los requerimientos
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del proyecto
COPY . /app/