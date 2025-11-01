# Guide de Déploiement Sécurisé sur Cloud Run

Ce guide explique comment déployer l'application avec **Workload Identity** et des **accès restreints** pour une sécurité maximale.

## 🔒 Architecture de Sécurité

```
Internet (Public)
    ↓
┌─────────────────────────────────────┐
│  Frontend (Cloud Run - PUBLIC)      │
│  Service Account: frontend-sa       │
│  - Accessible publiquement          │
│  - Proxy Nginx avec auth token      │
└─────────────────┬───────────────────┘
                  │ (Authentifié avec token)
                  ↓
┌─────────────────────────────────────┐
│  Backend (Cloud Run - PRIVÉ)        │
│  Service Account: backend-sa        │
│  - Accessible SEULEMENT par         │
│    le frontend (roles/run.invoker)  │
│  - Workload Identity activé         │
└─────────────────┬───────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│  Google Cloud Storage               │
│  - backend-sa a Storage Object Admin│
│  - backend-sa peut signer des URLs  │
└─────────────────────────────────────┘
```

## 📋 Prérequis

1. **Google Cloud SDK (gcloud)** installé et configuré
   ```bash
   gcloud auth login
   gcloud config set project pipeline-video-ia
   ```

2. **APIs activées**
   ```bash
   gcloud services enable \
       run.googleapis.com \
       artifactregistry.googleapis.com \
       storage.googleapis.com \
       iam.googleapis.com
   ```

3. **Docker** installé pour le build local

## 🚀 Déploiement en 3 étapes

### Étape 1 : Configuration IAM et Workload Identity

Créer les service accounts et configurer les permissions :

```bash
./setup-iam.sh
```

**Ce script crée :**
- ✅ Service Account `pipeline-backend-sa` avec :
  - `roles/storage.objectAdmin` (accès GCS)
  - `roles/iam.serviceAccountTokenCreator` (pour signer les URLs)
  
- ✅ Service Account `pipeline-frontend-sa` 
  - Pourra invoquer le backend (configuré à l'étape 3)

### Étape 2 : Build et Push des Images

Construire les images Docker et les pousser vers Artifact Registry :

```bash
./build-and-push.sh
```

**Ce script :**
- ✅ Crée le repository Artifact Registry si nécessaire
- ✅ Build l'image backend (Python FastAPI)
- ✅ Build l'image frontend (React + Nginx avec auth proxy)
- ✅ Push les deux images vers `us-central1-docker.pkg.dev`

**Images produites :**
- `us-central1-docker.pkg.dev/pipeline-video-ia/pipeline-tiktok/backend:latest`
- `us-central1-docker.pkg.dev/pipeline-video-ia/pipeline-tiktok/frontend:latest`

### Étape 3 : Déployer sur Cloud Run

Déployer les services avec Workload Identity et restrictions d'accès :

```bash
./deploy.sh
```

**Ce script :**

1. **Déploie le backend (PRIVÉ)** :
   - Mode `--no-allow-unauthenticated` (pas d'accès public)
   - Service Account `backend-sa` attaché (Workload Identity)
   - Variables d'environnement injectées (PROJECT_ID, BUCKET_NAME, etc.)

2. **Configure les permissions** :
   - Donne au `frontend-sa` le rôle `roles/run.invoker` sur le backend
   - Seul le frontend peut maintenant appeler le backend

3. **Déploie le frontend (PUBLIC)** :
   - Mode `--allow-unauthenticated` (accessible publiquement)
   - Service Account `frontend-sa` attaché
   - Variable `BACKEND_URL` injectée
   - Au démarrage, le conteneur frontend récupère automatiquement un **token d'identité** via metadata service
   - Nginx proxy les requêtes `/api/*` vers le backend avec le token dans le header `Authorization`

## 🔐 Comment fonctionne l'authentification ?

### En local (Docker Compose)
- Le frontend appelle directement `http://backend:8000` (réseau Docker)
- Pas d'authentification requise

### En production (Cloud Run)
1. Au démarrage du conteneur frontend, le script `start.sh` détecte l'environnement Cloud Run (`$K_SERVICE`)
2. Il récupère un **token d'identité** depuis le metadata service :
   ```bash
   curl -H "Metadata-Flavor: Google" \
     "http://metadata.google.internal/.../identity?audience=BACKEND_URL"
   ```
3. Ce token est injecté dans la config nginx
4. Nginx ajoute automatiquement `Authorization: Bearer <token>` sur toutes les requêtes vers le backend
5. Cloud Run vérifie que le token provient bien du `frontend-sa` qui a `roles/run.invoker`

## ✅ Vérification du déploiement

Après `./deploy.sh`, vous verrez :

```
✓ Backend déployé: https://pipeline-backend-xxxxx-uc.a.run.app
✓ Frontend autorisé à appeler le backend
✓ Frontend déployé: https://pipeline-frontend-xxxxx-uc.a.run.app

🔒 Sécurité:
  ✓ Backend accessible uniquement par le frontend
  ✓ Workload Identity activé (pas de credentials.json)
  ✓ Frontend proxy les requêtes /api vers le backend privé
```

**Testez :**
1. Ouvrez l'URL du frontend → ✅ Fonctionne
2. Essayez d'accéder directement au backend → ❌ 403 Forbidden
3. Les appels `/api/*` du frontend fonctionnent → ✅ Proxy authentifié

## 🛠️ Dépannage

### Le backend retourne 403
- Vérifiez que le frontend SA a bien le rôle `run.invoker` :
  ```bash
  gcloud run services get-iam-policy pipeline-backend --region=us-central1
  ```

### Les signed URLs ne fonctionnent pas
- Vérifiez les permissions du backend SA :
  ```bash
  gcloud projects get-iam-policy pipeline-video-ia \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:pipeline-backend-sa@*"
  ```
- Le SA doit avoir `roles/iam.serviceAccountTokenCreator`

### Le token expire
- Les tokens d'identité Cloud Run expirent après 1h
- Nginx conserve le token au démarrage
- Pour les longues sessions : implémenter un refresh périodique (TODO)

## 📊 Comparaison Local vs Production

| Aspect | Local (Docker Compose) | Production (Cloud Run) |
|--------|------------------------|------------------------|
| **Backend Auth** | Aucune | Token Bearer obligatoire |
| **Backend URL** | `http://backend:8000` | `https://pipeline-backend-xxx.run.app` |
| **GCS Auth** | `credentials.json` monté | Workload Identity (backend-sa) |
| **Frontend → Backend** | Réseau Docker | HTTPS + Token |
| **Accès public Backend** | Non (réseau privé) | Non (--no-allow-unauthenticated) |

## 🔄 Mises à jour

Pour redéployer après des modifications :

```bash
# 1. Rebuild et push les images
./build-and-push.sh

# 2. Redéployer (pas besoin de refaire setup-iam.sh)
./deploy.sh
```

## 🧹 Nettoyage

Pour supprimer les ressources :

```bash
# Supprimer les services Cloud Run
gcloud run services delete pipeline-backend --region=us-central1
gcloud run services delete pipeline-frontend --region=us-central1

# Supprimer les images
gcloud artifacts repositories delete pipeline-tiktok --location=us-central1

# Supprimer les service accounts
gcloud iam service-accounts delete pipeline-backend-sa@pipeline-video-ia.iam.gserviceaccount.com
gcloud iam service-accounts delete pipeline-frontend-sa@pipeline-video-ia.iam.gserviceaccount.com
```

## 📚 Ressources

- [Cloud Run Authentication](https://cloud.google.com/run/docs/authenticating/service-to-service)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [IAM Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
