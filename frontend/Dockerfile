# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le reste du code
COPY . .

# Argument pour choisir le fichier d'environnement
ARG ENV_FILE=.env.production

# Copier le fichier d'environnement approprié
RUN if [ -f "${ENV_FILE}" ]; then cp "${ENV_FILE}" .env; else echo "Warning: ${ENV_FILE} not found, using defaults"; fi

# Build de l'application
RUN npm run build

# Stage 2: Production avec Nginx
FROM nginx:alpine

# Copier le build depuis le stage builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Installer les outils nécessaires: envsubst et curl
RUN apk add --no-cache gettext curl

# Copier le template nginx et le script de démarrage
COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY start.sh /start.sh

# S'assurer que le script a les fins de ligne Linux (LF) et est exécutable
RUN apk add --no-cache dos2unix && \
    dos2unix /start.sh && \
    chmod +x /start.sh && \
    apk del dos2unix

EXPOSE 80

# Le script start.sh générera /etc/nginx/conf.d/default.conf depuis le template
ENTRYPOINT ["/start.sh"]
