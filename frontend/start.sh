#!/bin/sh
set -e

# Default BACKEND_URL to http://backend:8000 for local/docker-compose
: ${BACKEND_URL:=http://backend:8000}

# Si on est sur Cloud Run (backend authentifié), récupérer un token d'identité
if [ -n "$K_SERVICE" ]; then
    echo "🔐 Cloud Run détecté - Configuration authentification backend..."
    
    # Installer curl si nécessaire
    apk add --no-cache curl 2>/dev/null || true
    
    # Récupérer le token d'identité pour le backend
    METADATA_URL="http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity"
    export AUTH_TOKEN=$(curl -s -H "Metadata-Flavor: Google" "${METADATA_URL}?audience=${BACKEND_URL}&format=full")
    
    # Créer un fichier de config nginx avec le token
    cat > /etc/nginx/conf.d/auth.conf << EOF
# Configuration d'authentification Cloud Run
map \$request_uri \$auth_token {
    default "Bearer ${AUTH_TOKEN}";
}
EOF
    
    echo "✓ Token d'authentification configuré"
else
    echo "💻 Environnement local - Pas d'authentification requise"
    # Créer un fichier de config avec une variable vide pour l'auth
    cat > /etc/nginx/conf.d/auth.conf << 'EOF'
# Pas d'authentification en local
map $request_uri $auth_token {
    default "";
}
EOF
fi

# Exporter BACKEND_URL pour envsubst
export BACKEND_URL

# Use envsubst to replace ${BACKEND_URL} in the template
envsubst '${BACKEND_URL}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf

# Start nginx in foreground
nginx -g 'daemon off;'
