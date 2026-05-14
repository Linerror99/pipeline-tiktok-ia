# ── Build stage ───────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Installer torch CPU en premier pour éviter le téléchargement de la version GPU (~700MB)
RUN pip install --no-cache-dir --target=/build/deps \
    torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt

# ── Runtime stage ─────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# ffmpeg + libass nécessaires pour la concaténation et le burn-in des sous-titres
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copier les dépendances
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages/

# Pré-télécharger le modèle Whisper base (~140MB) au build time
RUN python -c "import whisper; whisper.load_model('base')" 2>/dev/null || true

# Copier l'application
COPY . .

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PORT=8080

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
