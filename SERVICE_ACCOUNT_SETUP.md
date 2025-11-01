# 🔐 Configuration Compte de Service Google Cloud

## 📋 Problème

L'erreur suivante apparaît lors de la génération d'URLs signées :

```
you need a private key to sign credentials.
the credentials you are currently using <class 'google.oauth2.credentials.Credentials'> just contains a token.
```

**Cause :** Vous utilisez `gcloud auth application-default login` qui donne des credentials utilisateur (OAuth2) sans clé privée. Les URLs signées nécessitent un **compte de service** avec clé privée.

---

## ✅ Solution Temporaire (Développement)

Le code a été modifié pour utiliser un **fallback** :
1. Essaie de générer une URL signée
2. Si échec → rend le blob **public** temporairement et retourne l'URL publique

⚠️ **Attention :** Les vidéos deviennent publiques (accessible sans authentification)

---

## 🚀 Solution Recommandée (Production)

### Étape 1 : Créer un Compte de Service

```bash
# Définir les variables
export PROJECT_ID=pipeline-video-ia
export SERVICE_ACCOUNT_NAME=pipeline-video-sa

# Créer le compte de service
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --display-name="Pipeline Video IA Service Account" \
  --project=$PROJECT_ID

# Donner les permissions Storage
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

### Étape 2 : Créer et Télécharger la Clé

```bash
# Créer la clé JSON
gcloud iam service-accounts keys create credentials.json \
  --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

# La clé est téléchargée dans credentials.json
```

### Étape 3 : Configurer l'Application

#### Option A : Variable d'environnement (recommandé)

**Backend (.env) :**
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

**Dans le code (config.py) :**
```python
import os
from google.cloud import storage

# Le client utilisera automatiquement les credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/credentials.json'
client = storage.Client(project=PROJECT_ID)
```

#### Option B : Passer explicitement les credentials

**storage.py :**
```python
from google.cloud import storage
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    '/path/to/credentials.json'
)

client = storage.Client(
    project=settings.PROJECT_ID,
    credentials=credentials
)
```

### Étape 4 : Docker Configuration

**docker-compose.yml :**
```yaml
services:
  backend:
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
    volumes:
      - ./credentials.json:/app/credentials.json:ro
```

**Dockerfile :**
```dockerfile
# Copier la clé (ATTENTION: ne pas commit dans Git!)
COPY credentials.json /app/credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
```

---

## 🔒 Sécurité

### ⚠️ NE JAMAIS :
- ❌ Commit `credentials.json` dans Git
- ❌ Partager la clé publiquement
- ❌ Mettre la clé dans le code source

### ✅ TOUJOURS :
- ✅ Ajouter `credentials.json` au `.gitignore`
- ✅ Utiliser des variables d'environnement
- ✅ Révoquer les anciennes clés
- ✅ Utiliser des secrets managers (Cloud Secret Manager, Vault)

### Ajout au .gitignore :
```
# Google Cloud credentials
credentials.json
service-account.json
*-credentials.json
```

---

## 🐳 Déploiement Cloud Run

Pour Cloud Run, utilisez **Workload Identity** au lieu de clés JSON :

```bash
# Créer le service account
gcloud iam service-accounts create pipeline-video-sa

# Lier au Cloud Run
gcloud run services add-iam-policy-binding pipeline-backend \
  --member="serviceAccount:pipeline-video-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Donner accès Storage
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:pipeline-video-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Déployer avec le service account
gcloud run deploy pipeline-backend \
  --service-account=pipeline-video-sa@PROJECT_ID.iam.gserviceaccount.com
```

Pas besoin de clé JSON sur Cloud Run ! 🎉

---

## 📊 Permissions Nécessaires

Minimum requis pour le compte de service :

```yaml
roles/storage.objectAdmin      # Lire/écrire/supprimer objets Storage
roles/storage.buckets.get      # Lister les buckets
```

Ou créer un rôle personnalisé :

```bash
gcloud iam roles create pipelineVideoRole \
  --project=$PROJECT_ID \
  --title="Pipeline Video Role" \
  --permissions=storage.objects.create,storage.objects.delete,storage.objects.get,storage.objects.list
```

---

## 🧪 Test

Après configuration, tester :

```bash
# Vérifier les credentials
python -c "from google.cloud import storage; print(storage.Client().project)"

# Tester génération URL signée
python -c "
from google.cloud import storage
from datetime import timedelta

client = storage.Client()
bucket = client.bucket('YOUR_BUCKET')
blob = bucket.blob('final_20231101_120000.mp4')
url = blob.generate_signed_url(version='v4', expiration=timedelta(hours=1), method='GET')
print(f'URL signée générée : {url[:50]}...')
"
```

---

## 💡 Résumé

| Environnement | Solution |
|---------------|----------|
| **Dev Local** | Credentials JSON + variable env |
| **Docker Local** | Volume mount credentials.json |
| **Cloud Run** | Workload Identity (pas de clé!) |
| **Production** | Service Account + Secret Manager |

---

**Pour l'instant, le fallback vers URL publique permet de tester. Mais configurez un compte de service pour la production !** 🔐
