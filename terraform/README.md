# Terraform Infrastructure - TikTok Pipeline

Infrastructure as Code pour déployer le pipeline de génération de vidéos TikTok sur GCP.

## 📋 Prérequis

1. **Terraform** installé (`>= 1.0`)
   ```bash
   terraform --version
   ```

2. **gcloud CLI** configuré
   ```bash
   gcloud auth application-default login
   gcloud config set project VOTRE_PROJECT_ID
   ```

3. **Projet GCP** créé
   ```bash
   # Projet: reetik-project
   gcloud config set project reetik-project
   
   # Activer la facturation (si pas déjà fait)
   gcloud billing accounts list
   gcloud billing projects link reetik-project --billing-account=BILLING_ACCOUNT_ID
   ```

## 🚀 Déploiement

### 1. Configuration

Copier le fichier d'exemple et le remplir :
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

Remplir les valeurs :
```hcl
project_id = "reetik-project"
region     = "us-central1"

bucket_name_v1 = "tiktok-pipeline-artifacts-reetik"
bucket_name_v2 = "tiktok-pipeline-v2-artifacts-reetik"
```

### 2. Initialiser Terraform

```bash
terraform init
```

### 3. Vérifier le plan

```bash
terraform plan
```

### 4. Créer Firestore Database (prérequis)

Terraform ne peut pas créer la base Firestore initiale, il faut le faire manuellement :

```bash
gcloud firestore databases create --location=us-central1
```

### 5. Déployer l'infrastructure

```bash
terraform apply
```

Taper `yes` pour confirmer.

## 📊 Ressources déployées

- ✅ **APIs GCP** (Cloud Functions, Firestore, Storage, Scheduler, etc.)
- ✅ **Service Account** avec permissions appropriées
- ✅ **Cloud Storage Buckets** (V1 + V2 avec versioning)
- ✅ **Firestore Indexes** pour requêtes optimisées
- ✅ **4 Cloud Functions Gen2** :
  - `agent-script-v2` (trigger: Storage)
  - `agent-video-v2` (HTTP)
  - `agent-assembler-v2` (HTTP)
  - `check-and-retry-clips` (HTTP + Scheduler)
- ✅ **Cloud Scheduler** (1 minute)

## 🔄 Mise à jour

Modifier les fichiers `.tf` puis :

```bash
terraform plan
terraform apply
```

## 🗑️ Destruction

**ATTENTION** : Supprime toute l'infrastructure !

```bash
terraform destroy
```

## 📤 Récupérer les outputs

```bash
terraform output
terraform output -json > outputs.json
```

## 🔐 Sécurité

- `terraform.tfvars` est dans `.gitignore` (contient config projet)
- Service Account avec permissions minimales (principe du moindre privilège)
- Buckets avec versioning activé

## 📝 Structure

```
terraform/
├── main.tf              # Provider + APIs
├── variables.tf         # Variables d'entrée
├── outputs.tf           # Outputs
├── storage.tf           # Cloud Storage
├── firestore.tf         # Firestore indexes
├── functions.tf         # Cloud Functions
├── scheduler.tf         # Cloud Scheduler
├── terraform.tfvars     # Configuration (ignoré par Git)
└── README.md
```

## 🛠️ Commandes utiles

```bash
# Formater le code
terraform fmt

# Valider la syntaxe
terraform validate

# Voir l'état actuel
terraform show

# Lister les ressources
terraform state list

# Voir une ressource spécifique
terraform state show google_cloudfunctions2_function.agent_video_v2
```

## 🐛 Troubleshooting

### Erreur "API not enabled"
```bash
# Activer manuellement
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
```

### Erreur "Firestore not initialized"
```bash
gcloud firestore databases create --location=us-central1
```

### Conflit de ressources
```bash
# Importer une ressource existante
terraform import google_storage_bucket.artifacts_v2 tiktok-pipeline-v2-artifacts
```

## 📚 Documentation

- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Functions Terraform](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/cloudfunctions2_function)
- [GCP Best Practices](https://cloud.google.com/docs/terraform/best-practices-for-terraform)
