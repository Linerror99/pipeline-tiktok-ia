# URLs de Production Cloud Run

Ce fichier centralise les URLs stables des services déployés.

## ⚠️ Important

**Les URLs Cloud Run ne changent PAS** tant que :
- Le nom du service reste identique
- Le projet GCP reste le même

Ces URLs sont donc **STABLES** et peuvent être hardcodées.

## 🔗 URLs des Services

### Backend
```
https://tiktok-backend-vrzs3y5aoq-uc.a.run.app
```

### Frontend  
```
https://tiktok-frontend-838433433731.us-central1.run.app
```

## 📝 Où mettre à jour si URLs changent

Si jamais les URLs changent (changement de projet ou recréation de service), mettez à jour :

1. **GitHub Actions Workflow** (`.github/workflows/deploy-production.yml`) :
   - Variable `BACKEND_URL` dans "Build Frontend Image"
   - Variable `FRONTEND_URL` dans "Build Frontend Image"
   - Variable `CORS_ORIGINS` dans "Deploy Backend to Cloud Run"

2. **Terraform** (`terraform/terraform.tfvars`) :
   - Variable `cors_origins`

3. **Terraform Storage** (`terraform/storage.tf`) :
   - CORS configuration du bucket `artifacts_v2`

## 🧪 Tester les URLs

```bash
# Backend health check
curl https://tiktok-backend-vrzs3y5aoq-uc.a.run.app/

# Frontend
open https://tiktok-frontend-838433433731.us-central1.run.app
```

## 🔐 Code d'accès

Pour récupérer le code d'accès actuel :

```bash
gcloud firestore databases documents get \
  projects/reetik-project/databases/(default)/documents/config/access_code \
  --format="value(fields.code.stringValue)"
```

Ou déclencher une nouvelle génération :

```bash
curl -X POST https://rotate-access-code-vrzs3y5aoq-uc.a.run.app \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -H "Content-Type: application/json" \
  -d '{}'
```
