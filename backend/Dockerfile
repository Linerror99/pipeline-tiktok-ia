# Stage 1: Builder - installer les dépendances
FROM python:3.12-slim AS builder

WORKDIR /app

# Installer les dépendances système nécessaires pour la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer dans un virtualenv
COPY requirements.txt .

# Installer les dépendances en mode optimisé
RUN pip install --no-cache-dir --user --compile -r requirements.txt && \
    # Supprimer les fichiers de test et de documentation des packages
    find /root/.local -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type d -name "test" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -type d -name "docs" -exec rm -rf {} + 2>/dev/null || true && \
    find /root/.local -name "*.pyc" -delete && \
    find /root/.local -name "*.pyo" -delete && \
    find /root/.local -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Stage 2: Runtime - image finale légère
FROM python:3.12-slim

WORKDIR /app

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copier seulement les packages Python installés depuis le builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copier uniquement le code de l'application (pas de tests, docs, etc.)
COPY --chown=appuser:appuser app/ ./app/

# Mettre à jour le PATH pour utiliser les packages de l'utilisateur
ENV PATH=/home/appuser/.local/bin:$PATH

# Basculer vers l'utilisateur non-root
USER appuser

# Exposer le port
EXPOSE 8000

# Healthcheck pour Cloud Run
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Commande de démarrage
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
