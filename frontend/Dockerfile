# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le reste du code
COPY . .

# Build de l'application
RUN npm run build

# Stage 2: Production avec Nginx
FROM nginx:alpine

# Copier le build depuis le stage builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copier la configuration Nginx personnalisée
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
