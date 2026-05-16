FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema (necesarias para argon2)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear directorio para la base de datos
RUN mkdir -p /app/escuela_2026

EXPOSE 5000

# Comando CORRECTO: gunicorn app:app (no main:app)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
