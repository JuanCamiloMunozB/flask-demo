# Usa la misma versión de Python que usaste localmente
FROM python:3.9-slim

# Crea y entra al directorio de la app
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expone el puerto usado por Flask
EXPOSE 10000

# Variable de entorno para Flask
ENV FLASK_APP=keepalive.py
ENV FLASK_ENV=production
ENV PORT=10000

# Comando para ejecutar ambos servicios (Flask y el bot)
CMD ["python", "telegram_bot.py"]
