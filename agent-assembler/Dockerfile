FROM python:3.12-slim

# Installation de FFmpeg + dépendances système
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENV PORT=8080
ENV FUNCTION_TARGET=assemble_video

CMD exec functions-framework --target=assemble_video --signature-type=cloudevent