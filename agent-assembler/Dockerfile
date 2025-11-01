# Image de base Python avec Debian (pour avoir apt-get)
FROM python:3.12-slim

# Installation de FFmpeg et des dépendances système
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY main.py .

# Configuration pour Functions Framework
ENV PORT=8080
ENV FUNCTION_TARGET=assemble_video

# Point d'entrée
CMD exec functions-framework --target=assemble_video --signature-type=cloudevent