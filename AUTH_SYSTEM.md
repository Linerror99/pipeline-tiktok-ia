# 🔐 Système d'Authentification - Documentation Complète

## Vue d'ensemble

Le système d'authentification protège l'application contre les abus et les coûts excessifs via :
- **Code d'accès rotatif** : Change toutes les heures via Cloud Scheduler
- **JWT tokens** : Authentification stateless avec expiration de 7 jours
- **Quotas utilisateurs** : 2 vidéos pour utilisateurs normaux, illimité pour admins
- **Backend privé** : API accessible uniquement via le frontend authentifié

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Scheduler                           │
│                  (Cron: 0 * * * *)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ Toutes les heures
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              Cloud Function: rotate-access-code             │
│         Génère un nouveau code de 8 caractères              │
└──────────────────────┬──────────────────────────────────────┘
                       │ Sauvegarde
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    Firestore                                │
│  Collection: config                                         │
│    Document: access_code                                    │
│      - code: "ABC12345"                                     │
│      - updated_at: timestamp                                │
│                                                             │
│  Collection: users                                          │
│    Document: {userId}                                       │
│      - email: string                                        │
│      - password_hash: string (bcrypt)                       │
│      - is_admin: boolean                                    │
│      - video_count: number                                  │
│      - max_videos: number (-1 = illimité)                   │
│      - created_at: timestamp                                │
│      - last_login: timestamp                                │
└─────────────────────────────────────────────────────────────┘
                       ↑                    ↑
                       │                    │
┌──────────────────────┴──────┐   ┌────────┴──────────────────┐
│      Frontend (PUBLIC)       │   │    Backend (PRIVÉ)        │
│                              │   │                           │
│  - React + Vite              │   │  - FastAPI                │
│  - Nginx reverse proxy       │   │  - JWT auth middleware    │
│  - Service Account:          │   │  - Quota enforcement      │
│    pipeline-frontend-sa      │   │  - Service Account:       │
│  - Peut invoker le backend   │   │    pipeline-backend-sa    │
│                              │   │  - Firestore access       │
└──────────────────────────────┘   └───────────────────────────┘
```

## Flux d'Authentification

### 1. Inscription (Register)

```
User → Frontend → /api/auth/verify-code (POST)
                   ↓
              Nginx rewrite: /auth/verify-code
                   ↓
              Backend vérifie le code dans Firestore
                   ↓
              ✅ Code valide
                   ↓
User → Frontend → /api/auth/register (POST)
                   {
                     email: "user@example.com",
                     password: "password123",
                     access_code: "ABC12345"
                   }
                   ↓
              Nginx rewrite: /auth/register
                   ↓
              Backend:
                1. Vérifie le code
                2. Hash le mot de passe (bcrypt)
                3. Crée l'utilisateur dans Firestore
                4. Génère un JWT token (HS256)
                   ↓
              ← JWT token + user info
                   ↓
              Frontend stocke le token (localStorage)
                   ↓
              Configure axios.defaults.headers.common['Authorization']
```

### 2. Connexion (Login)

```
User → Frontend → /api/auth/verify-code (POST)
                   ↓
              ✅ Code valide
                   ↓
User → Frontend → /api/auth/login (POST)
                   {
                     email: "user@example.com",
                     password: "password123"
                   }
                   ↓
              Backend:
                1. Vérifie l'email
                2. Vérifie le mot de passe (bcrypt.verify)
                3. Met à jour last_login
                4. Génère un JWT token
                   ↓
              ← JWT token + user info
                   ↓
              Frontend stocke le token
```

### 3. Requêtes Authentifiées

```
User → Frontend → /api/videos/create (POST)
                   Header: Authorization: Bearer <JWT>
                   ↓
              Nginx:
                1. Rewrite: /videos/create
                2. Preserve Authorization header (conditionally)
                3. Add Cloud Run auth token if needed
                   ↓
              Backend:
                1. Vérifie JWT (get_current_user middleware)
                2. Vérifie le quota (can_create_video)
                3. Traite la requête
                4. Incrémente video_count
```

## Configuration Cloud Run

### Variables d'Environnement Backend

```bash
PROJECT_ID=pipeline-video-ia
BUCKET_NAME=tiktok-pipeline-artifacts-pipeline-video-ia
REGION=us-central1
JWT_SECRET_KEY=<généré automatiquement ou défini manuellement>
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7
```

### Variables d'Environnement Frontend

```bash
BACKEND_URL=https://pipeline-backend-354616212471.us-central1.run.app
VITE_API_URL=/api  # En production (Nginx proxy)
# VITE_API_URL=http://localhost:8000  # En développement local
```

## Service Accounts et Permissions

### Backend Service Account

```bash
pipeline-backend-sa@pipeline-video-ia.iam.gserviceaccount.com
```

Permissions :
- `roles/storage.objectAdmin` - Accès au bucket GCS
- `roles/datastore.user` - Accès à Firestore
- `roles/iam.serviceAccountTokenCreator` - Génération de tokens

### Frontend Service Account

```bash
pipeline-frontend-sa@pipeline-video-ia.iam.gserviceaccount.com
```

Permissions :
- `roles/run.invoker` sur `pipeline-backend` - Peut appeler le backend privé

## Configuration Nginx (Frontend)

Le fichier `nginx.conf.template` gère :
1. Le rewrite des URLs `/api/*` vers `/*` pour le backend
2. La préservation du header `Authorization` JWT du client
3. L'ajout conditionnel du token Cloud Run pour l'auth backend

```nginx
location /api/ {
    # Retirer /api/ du path
    rewrite ^/api/(.*)$ /$1 break;
    
    proxy_pass ${BACKEND_URL};
    
    # Préserver le JWT du client ou utiliser le token Cloud Run
    proxy_set_header Authorization $http_authorization$auth_token;
    
    # Headers standards
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

## Gestion des Quotas

### Utilisateur Normal
- `max_videos = 2`
- `video_count` incrémenté après chaque création réussie
- Vérifié avant chaque création (`can_create_video`)

### Administrateur
- `max_videos = -1` (illimité)
- `is_admin = true`
- Pas de vérification de quota

### Endpoint de Vérification

```bash
GET /auth/me
Authorization: Bearer <JWT>

Response:
{
  "id": "user123",
  "email": "user@example.com",
  "is_admin": false,
  "video_count": 1,
  "max_videos": 2,
  "created_at": "2025-11-01T...",
  "last_login": "2025-11-02T..."
}
```

## Déploiement

### 1. Déployer la Cloud Function

```bash
cd cloud-functions
./deploy-scheduler.sh
```

Cela crée :
- La Cloud Function `rotate-access-code`
- Le Cloud Scheduler job (cron horaire)
- Génère le premier code d'accès

### 2. Initialiser Firestore

```bash
cd cloud-functions
python init-firestore.py
```

Crée :
- Le compte admin par défaut
- Le premier code d'accès

### 3. Build et Push les Images

```bash
./build-and-push.sh
```

### 4. Déployer sur Cloud Run

```bash
./deploy.sh
```

Ou avec JWT_SECRET_KEY manuel :
```bash
JWT_SECRET_KEY="votre-clé-secrète-ici" ./deploy.sh
```

## Commandes Utiles

### Obtenir le Code Actuel

```bash
# Via Cloud Function
curl https://rotate-access-code-5ranhgrf2q-uc.a.run.app/ | jq

# Via Firestore (nécessite credentials)
python << EOF
from google.cloud import firestore
db = firestore.Client(project='pipeline-video-ia')
doc = db.collection('config').document('access_code').get()
print(f"Code: {doc.to_dict()['code']}")
EOF
```

### Créer un Compte Admin Manuellement

```bash
python << EOF
from google.cloud import firestore
import bcrypt

db = firestore.Client(project='pipeline-video-ia')
password_hash = bcrypt.hashpw("votre_mot_de_passe".encode(), bcrypt.gensalt()).decode()

db.collection('users').add({
    'email': 'admin@example.com',
    'password_hash': password_hash,
    'is_admin': True,
    'video_count': 0,
    'max_videos': -1,
    'created_at': firestore.SERVER_TIMESTAMP,
    'last_login': None
})
print("Admin créé !")
EOF
```

### Tester l'Authentification

```bash
# Vérifier un code
curl -X POST https://pipeline-frontend-354616212471.us-central1.run.app/api/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"code":"ABC12345"}'

# S'inscrire
curl -X POST https://pipeline-frontend-354616212471.us-central1.run.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "access_code": "ABC12345"
  }'

# Se connecter
curl -X POST https://pipeline-frontend-354616212471.us-central1.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Récupérer les infos utilisateur
curl -X GET https://pipeline-frontend-354616212471.us-central1.run.app/api/auth/me \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

## Sécurité

### Best Practices Implémentées

✅ Mots de passe hashés avec bcrypt (salt automatique)  
✅ JWT tokens avec expiration (7 jours)  
✅ Code d'accès rotatif (1 heure)  
✅ Backend privé (accessible uniquement via frontend)  
✅ Workload Identity (pas de fichier credentials.json)  
✅ HTTPS obligatoire (Cloud Run)  
✅ CORS configuré correctement  
✅ Headers de sécurité (X-Real-IP, X-Forwarded-For)  
✅ Quotas par utilisateur  

### Recommandations Additionnelles

- [ ] Rate limiting sur les endpoints d'authentification
- [ ] Logging des tentatives de connexion échouées
- [ ] Blocage temporaire après X échecs
- [ ] Vérification de la force du mot de passe côté frontend
- [ ] Email de confirmation à l'inscription
- [ ] Reset de mot de passe par email
- [ ] Refresh tokens pour renouveler JWT sans re-login

## Troubleshooting

### Erreur 401 sur /auth/me

**Cause** : Token JWT invalide ou expiré

**Solution** :
1. Vérifier que le token est bien stocké dans localStorage
2. Vérifier que axios.defaults.headers.common['Authorization'] est défini
3. Se reconnecter pour obtenir un nouveau token

### Erreur 405 Method Not Allowed

**Cause** : Le rewrite Nginx ne fonctionne pas correctement

**Solution** :
1. Vérifier `nginx.conf.template` : `rewrite ^/api/(.*)$ /$1 break;`
2. Vérifier que les routers backend n'ont pas de préfixe `/api`
3. Rebuild et redéployer le frontend

### Erreur 404 sur /api/videos

**Cause** : Route backend mal configurée

**Solution** :
1. Vérifier que `videos.router` a le préfixe `/videos` (pas `/api/videos`)
2. Vérifier que le frontend appelle `/api/videos` (avec `/api`)
3. Vérifier que Nginx rewrite vers `/videos`

### Code d'accès invalide

**Cause** : Le code a expiré (change toutes les heures)

**Solution** :
1. Appeler la Cloud Function pour obtenir le nouveau code
2. Vérifier que le Cloud Scheduler fonctionne
3. Consulter Firestore pour voir le code actuel

## Support

Pour toute question :
1. Consulter les logs Cloud Run
2. Vérifier Firestore (collection users et config)
3. Tester les endpoints avec curl
4. Ouvrir une issue sur GitHub

---

**Dernière mise à jour** : 2 novembre 2025
