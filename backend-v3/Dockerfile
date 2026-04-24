# ── Build stage ───────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

# ── Runtime stage ─────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# ffmpeg nécessaire pour la concaténation des clips Veo
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copier les dépendances
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages/

# Copier l'application
COPY . .

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
