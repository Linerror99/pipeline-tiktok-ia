# Nettoyage Infrastructure - Terraform Simplifié

## 🎯 Changements effectués

### ❌ Supprimé
1. **Bucket `functions_source`** - Code stocké sur GitHub, pas besoin de bucket
2. **Bucket V1 `artifacts_v1`** - On garde uniquement V2 (Veo 3.1)
3. **Toutes les ressources Cloud Functions dans Terraform** - Déployées manuellement
4. **Cloud Scheduler dans Terraform** - Déployé manuellement

### ✅ Conservé
1. **Bucket V2** `tiktok-pipeline-v2-artifacts-reetik-project` - Pour les vidéos/scripts
2. **Service Account** - Pour les permissions des Cloud Functions
3. **APIs activées** - Toujours nécessaires
4. **Firestore** - Base de données

---

## 📦 Infrastructure finale Terraform

```
reetik-project/
├── Bucket V2 (Storage)
│   └── tiktok-pipeline-v2-artifacts-reetik-project
│       ├── {video_id}/script_v2.json
│       ├── {video_id}/block_1.mp4
│       ├── {video_id}/block_2.mp4
│       └── {video_id}/final.mp4
│
├── Firestore (Database)
│   ├── v2_video_status
│   └── v2_veo_operations
│
└── Service Account
    └── cloud-functions-sa@reetik-project.iam.gserviceaccount.com
```

**Cloud Functions** et **Cloud Scheduler** sont déployés **manuellement** via scripts bash.

---

## 🚀 Commandes de déploiement

### 1. Infrastructure de base (Terraform)
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

**Déploie:**
- ✅ Bucket V2
- ✅ Service Account + IAM
- ✅ APIs (Storage, Functions, Firestore, Vertex AI)
- ✅ Firestore

### 2. Cloud Functions (manuel)
```bash
# Depuis la racine du projet
./deploy-functions-v2.sh
```

**Déploie:**
- `agent-script-v2` (HTTP)
- `agent-video-v2` (HTTP)
- `check-and-retry-clips` (HTTP)
- `agent-assembler-v2` (HTTP)

### 3. Cloud Scheduler (manuel)
```bash
cd cloud-functions
./deploy-scheduler.sh
```

**Déploie:**
- Job `check-and-retry-clips` (chaque minute)

---

## 🧹 Nettoyage du state Terraform

Avant d'appliquer les changements, il faut supprimer les anciennes ressources du state :

```bash
cd terraform

# Supprimer les Cloud Functions du state (ne seront plus gérées par Terraform)
terraform state rm google_cloudfunctions2_function.agent_script_v2
terraform state rm google_cloudfunctions2_function.agent_video_v2
terraform state rm google_cloudfunctions2_function.check_and_retry_clips
terraform state rm google_cloudfunctions2_function.agent_assembler_v2

# Supprimer les IAM des fonctions
terraform state rm google_cloudfunctions2_function_iam_member.agent_script_v2_invoker
terraform state rm google_cloudfunctions2_function_iam_member.agent_video_v2_invoker
terraform state rm google_cloudfunctions2_function_iam_member.check_retry_invoker
terraform state rm google_cloudfunctions2_function_iam_member.agent_assembler_v2_invoker

# Supprimer les objects dans le bucket source
terraform state rm google_storage_bucket_object.agent_script_v2_source
terraform state rm google_storage_bucket_object.agent_video_v2_source
terraform state rm google_storage_bucket_object.check_retry_source
terraform state rm google_storage_bucket_object.agent_assembler_v2_source

# Supprimer le bucket source
terraform state rm google_storage_bucket.functions_source

# Supprimer le bucket V1
terraform state rm google_storage_bucket.artifacts_v1
terraform state rm google_storage_bucket_iam_member.functions_v1_access

# Supprimer le scheduler
terraform state rm google_cloud_scheduler_job.check_and_retry

# Appliquer les changements
terraform apply
```

---

## 💰 Économies réalisées

| Ressource | Coût mensuel | Statut |
|-----------|--------------|---------|
| Bucket `functions_source` | $0.02 | ❌ Supprimé |
| Bucket V1 `artifacts_v1` | $5-10 | ❌ Supprimé |
| Gestion Terraform des Functions | Complexité | ✅ Simplifié |

**Total économisé:** ~$10/mois + Simplification de la maintenance

---

## ✅ Avantages

1. **Moins de buckets** = Moins de coûts
2. **Déploiement local** = Plus de contrôle et flexibilité
3. **Terraform simplifié** = Infrastructure de base seulement
4. **GitHub comme source** = Pas de duplication du code

---

## 📝 Prochaines étapes

1. ✅ Nettoyer le state Terraform (commandes ci-dessus)
2. ✅ Appliquer les changements: `terraform apply`
3. ✅ Déployer les Cloud Functions: `./deploy-functions-v2.sh`
4. ✅ Déployer le Scheduler: `cd cloud-functions && ./deploy-scheduler.sh`
5. ✅ Tester le workflow: `python test_flow_v2.py`

