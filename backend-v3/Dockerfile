# ── Build stage ───────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

# ── Runtime stage ─────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copier les dépendances
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages/

# Copier l'application
COPY . .

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
