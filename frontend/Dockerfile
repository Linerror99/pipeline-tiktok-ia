# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le reste du code
COPY . .

# Copier le fichier d'environnement Docker (utilise backend:8000)
COPY .env.docker .env

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
RUN chmod +x /start.sh

EXPOSE 80

# Le script start.sh générera /etc/nginx/conf.d/default.conf depuis le template
ENTRYPOINT ["/start.sh"]
