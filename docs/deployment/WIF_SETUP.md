# Configuration Workload Identity Federation

## ✅ Ressources créées

- **Workload Identity Pool:** `github-actions-pool`
- **OIDC Provider:** `github-provider`
- **Project Number:** `838433433731`

## 🔧 Configuration IAM

Pour finaliser la configuration, exécutez cette commande en remplaçant `VOTRE_USERNAME_GITHUB` par votre nom d'utilisateur GitHub :

```bash
# Remplacez VOTRE_USERNAME_GITHUB (exemple: "ldjossou" ou nom de votre organisation)
GITHUB_USERNAME="Linerror99"
REPO_NAME="pipeline-tiktok-ia"

gcloud iam service-accounts add-iam-policy-binding \
  pipeline-tiktok-functions@reetik-project.iam.gserviceaccount.com \
  --project=reetik-project \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/838433433731/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/${GITHUB_USERNAME}/${REPO_NAME}"
```

## 📝 Secrets GitHub à configurer

Ajoutez ces secrets dans votre repository GitHub :  
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### 1. WIF_PROVIDER
```
projects/838433433731/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider
```

### 2. WIF_SERVICE_ACCOUNT
```
pipeline-tiktok-functions@reetik-project.iam.gserviceaccount.com
```

## ✅ Vérification

Après avoir configuré les secrets, déclenchez le workflow manuellement :

```bash
# Sur GitHub: Actions → Deploy to Production → Run workflow
```

Ou poussez sur la branche `main` :

```bash
git add .
git commit -m "Setup Workload Identity Federation"
git push origin main
```

## 🔍 Debug

Si le déploiement échoue, vérifiez :

```bash
# Vérifier le provider
gcloud iam workload-identity-pools providers describe github-provider \
  --project=reetik-project \
  --location=global \
  --workload-identity-pool=github-actions-pool

# Vérifier les bindings IAM
gcloud iam service-accounts get-iam-policy \
  pipeline-tiktok-functions@reetik-project.iam.gserviceaccount.com \
  --project=reetik-project
```

## 📚 Documentation

- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub Actions + Google Cloud](https://github.com/google-github-actions/auth)
