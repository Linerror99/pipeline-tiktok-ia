# 🎬 Pipeline Vidéo IA TikTok - Génération Automatisée

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Pro-orange)](https://deepmind.google/technologies/gemini/)
[![Veo](https://img.shields.io/badge/Veo-3.0-red)](https://deepmind.google/technologies/veo/)

Pipeline complète de génération automatique de vidéos TikTok/Shorts virales à partir d'un simple thème. Utilise Gemini 2.5 Pro, Veo 3.0, Google TTS Premium, et Whisper.

---

## 🚀 Fonctionnalités

- ✅ **Génération de script IA** avec Gemini 2.5 Pro
- ✅ **Voix off premium** (voix Gemini naturelle)
- ✅ **Clips vidéo créatifs** générés par Veo 3.0 (meilleur modèle vidéo IA)
- ✅ **Sous-titres style TikTok** synchronisés (Whisper + ASS)
- ✅ **Format optimisé** : 9:16, 64-80 secondes
- ✅ **Pipeline entièrement automatisée** : 1 requête → vidéo complète

---

## 📊 Architecture

```
Thème → Agent Script (Gemini) → Agent Audio (TTS) → Agent Vidéo (Veo) → Agent Assembleur (FFmpeg+Whisper) → Vidéo Finale
```

**4 Cloud Functions** déclenchées en cascade via Cloud Storage Events.

---

## 🛠️ Technologies

| Composant | Technologie |
|-----------|-------------|
| **Script Generation** | Gemini 2.5 Pro |
| **Voix Off** | Google TTS Premium (Gemini voice) |
| **Génération Vidéo** | Veo 3.0 (format 9:16) |
| **Sous-titres** | OpenAI Whisper + ASS format |
| **Assemblage** | FFmpeg |
| **Infrastructure** | Google Cloud Functions Gen2 |
| **Stockage** | Google Cloud Storage |

---

## 📋 Prérequis

- **Compte Google Cloud** avec facturation activée
- **APIs activées** :
  - Cloud Functions API
  - Cloud Storage API
  - Vertex AI API
  - Text-to-Speech API
  - Cloud Build API
  - Eventarc API
- **gcloud CLI** installé et configuré

---

## 🔧 Installation

### 1. Cloner le Repository

```bash
git clone https://github.com/votre-username/pipeline-video-tiktok.git
cd pipeline-video-tiktok
```

### 2. Configuration GCP

```bash
# Se connecter à GCP
gcloud auth login

# Définir le projet
export PROJECT_ID="pipeline-video-ia"
gcloud config set project $PROJECT_ID

# Activer les APIs nécessaires
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  texttospeech.googleapis.com \
  eventarc.googleapis.com
```

### 3. Créer le Bucket Cloud Storage

```bash
gsutil mb -p $PROJECT_ID -c STANDARD -l us-central1 \
  gs://tiktok-pipeline-artifacts-$PROJECT_ID
```

### 4. Déployer les Agents

#### Agent Script (HTTP Trigger)
```bash
cd agent-script

gcloud functions deploy generate-script-agent \
  --gen2 \
  --runtime=python312 \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --source=. \
  --entry-point=generate_script \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars="GCP_PROJECT=$PROJECT_ID,BUCKET_NAME=tiktok-pipeline-artifacts-$PROJECT_ID" \
  --memory=512Mi \
  --timeout=300s
```

#### Agent Audio (Storage Trigger)
```bash
cd ../agent-audio

gcloud functions deploy generate-audio-agent \
  --gen2 \
  --runtime=python312 \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --source=. \
  --entry-point=generate_audio \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=tiktok-pipeline-artifacts-$PROJECT_ID" \
  --memory=512Mi \
  --timeout=540s
```

#### Agent Vidéo (Storage Trigger)
```bash
cd ../agent-video

gcloud functions deploy generate-video-agent \
  --gen2 \
  --runtime=python312 \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --source=. \
  --entry-point=generate_video \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=tiktok-pipeline-artifacts-$PROJECT_ID" \
  --memory=512Mi \
  --timeout=3600s \
  --max-instances=10
```

#### Agent Assembleur (Storage Trigger)
```bash
cd ../agent-assembler

gcloud functions deploy generate-assembler-agent \
  --gen2 \
  --runtime=python312 \
  --project=$PROJECT_ID \
  --region=us-central1 \
  --source=. \
  --entry-point=assemble_video \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=tiktok-pipeline-artifacts-$PROJECT_ID" \
  --memory=4Gi \
  --timeout=540s \
  --max-instances=5
```

---

## 🎬 Utilisation

### Générer une Vidéo

```bash
# Récupérer l'URL de l'agent script
SCRIPT_URL=$(gcloud functions describe generate-script-agent \
  --gen2 \
  --region=us-central1 \
  --format="value(serviceConfig.uri)")

# Lancer la génération
curl -X POST $SCRIPT_URL \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "Les secrets cachés de la Grande Muraille de Chine"
  }'
```

### Exemples de Thèmes Viraux

```bash
# Mystères historiques
curl -X POST $SCRIPT_URL -H "Content-Type: application/json" \
  -d '{"theme": "Les pyramides de Bosnie - mythe ou réalité"}'

# Technologies anciennes
curl -X POST $SCRIPT_URL -H "Content-Type: application/json" \
  -d '{"theme": "Les technologies impossibles des anciens Égyptiens"}'

# Phénomènes inexpliqués
curl -X POST $SCRIPT_URL -H "Content-Type: application/json" \
  -d '{"theme": "Le triangle des Bermudes - nouvelle découverte 2024"}'
```

---

## 📊 Suivre l'Exécution

### Logs en Temps Réel

```bash
# Tous les agents
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=200 \
  --format="table(timestamp,resource.labels.service_name,textPayload)" \
  --project=$PROJECT_ID

# Agent spécifique
gcloud functions logs read generate-assembler-agent \
  --gen2 \
  --region=us-central1 \
  --limit=50
```

### Cloud Storage

```bash
# Lister les fichiers générés
gsutil ls gs://tiktok-pipeline-artifacts-$PROJECT_ID/

# Télécharger la vidéo finale
gsutil cp gs://tiktok-pipeline-artifacts-$PROJECT_ID/final_*.mp4 ./ma_video.mp4
```

### Interface Web (Cloud Console)

- **Storage** : https://console.cloud.google.com/storage/browser
- **Logs** : https://console.cloud.google.com/logs/query
- **Functions** : https://console.cloud.google.com/functions

---

## ⏱️ Durées de Traitement

| Étape | Durée |
|-------|-------|
| Script | 5-10 secondes |
| Audio | 20-30 secondes |
| Vidéo (8 clips en parallèle) | 3-5 minutes |
| Assemblage + Sous-titres | 2-3 minutes |
| **TOTAL** | **~6-10 minutes** |

---

## 💰 Coûts Estimés

| Service | Coût par Vidéo |
|---------|----------------|
| Gemini 2.5 Pro | ~$0.02 |
| Google TTS Premium | ~$0.05 |
| Veo 3.0 (8 clips) | ~$5.00 |
| Cloud Functions | ~$0.10 |
| Cloud Storage | ~$0.01 |
| **TOTAL** | **~$5.18** |

---

## 🐛 Troubleshooting

### Problème : Script avec < 8 scènes
```bash
# Le système régénère automatiquement
# Vérifiez les logs :
gcloud functions logs read generate-script-agent --gen2 --region=us-central1
```

### Problème : Audio désynchronisé
```bash
# Vérifiez le ratio de vitesse dans les logs :
gcloud functions logs read generate-audio-agent --gen2 --region=us-central1 | grep "Ratio vitesse"
```

### Problème : Clips dans le mauvais ordre
```bash
# Vérifiez l'ordre dans les logs de l'assembleur :
gcloud functions logs read generate-assembler-agent --gen2 --region=us-central1 | grep "Clip"
```

### Problème : Sous-titres décalés
```bash
# Whisper devrait donner une synchro parfaite
# Vérifiez que Whisper s'est bien chargé :
gcloud functions logs read generate-assembler-agent --gen2 --region=us-central1 | grep "Whisper"
```

---

## 📁 Structure du Projet

```
pipeline-video-tiktok/
├── agent-script/
│   ├── main.py              # Génération script avec Gemini
│   └── requirements.txt
├── agent-audio/
│   ├── main.py              # Génération audio avec TTS
│   └── requirements.txt
├── agent-video/
│   ├── main.py              # Génération vidéo avec Veo
│   └── requirements.txt
├── agent-assembler/
│   ├── main.py              # Assemblage avec FFmpeg + Whisper
│   ├── requirements.txt
│   └── Dockerfile           # Container avec FFmpeg
└── README.md
```

---

## 🔒 Sécurité

- Les Cloud Functions sont **privées** (sauf agent-script pour HTTP)
- Authentification via **Service Accounts**
- Permissions minimales (Principle of Least Privilege)
- Données stockées dans **région us-central1**

---

## � Système d'Authentification

L'application dispose d'un système d'authentification complet pour protéger vos ressources :

### Fonctionnalités
- ✅ **Code d'accès rotatif** : Code de 8 caractères qui change toutes les heures
- ✅ **Authentification JWT** : Tokens sécurisés avec expiration de 7 jours
- ✅ **Système de quotas** : 2 vidéos max pour utilisateurs normaux, illimité pour admins
- ✅ **Backend privé** : API accessible uniquement via le frontend (Cloud Run authentifié)
- ✅ **Workload Identity** : Pas de credentials.json en production

### Architecture Sécurisée

```
Frontend (PUBLIC) → Nginx Proxy → Backend (PRIVÉ)
     ↓                              ↓
Service Account            Service Account
Frontend SA               Backend SA
  └─ Invoke Backend         └─ Storage Admin
                            └─ Firestore User
```

### Obtenir le Code d'Accès

Le code change automatiquement toutes les heures. Pour l'obtenir :

```bash
# Appeler la Cloud Function de rotation
curl https://rotate-access-code-5ranhgrf2q-uc.a.run.app/
```

Ou consulter directement Firestore :
```bash
# Via Firebase Console
https://console.firebase.google.com/project/pipeline-video-ia/firestore

# Collection: config
# Document: access_code
```

### Utilisation

1. **Obtenir le code actuel** (change toutes les heures)
2. **S'inscrire** avec email + mot de passe + code
3. **Se connecter** avec email + mot de passe + code
4. **Créer des vidéos** (quota vérifié automatiquement)

## �🚀 Améliorations Futures

- [x] Interface web pour générer des vidéos
- [x] Système d'authentification avec quotas
- [ ] Publication automatique sur TikTok/YouTube
- [ ] Support multi-langues
- [ ] Templates de styles visuels personnalisés
- [ ] Musique de fond automatique
- [ ] Analytics et A/B testing

---

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE)

---

## 👤 Auteur

**Linerror99Su**
- GitHub: [@Linerror99Su](https://github.com/Linerror99Su)
- Projet: Pipeline Vidéo IA TikTok

---

## 🙏 Remerciements

- Google Cloud pour l'infrastructure
- DeepMind pour Gemini et Veo
- OpenAI pour Whisper
- FFmpeg pour le traitement vidéo

---

## 📞 Support

Pour toute question ou problème :
1. Consultez les logs : `gcloud functions logs read`
2. Vérifiez Cloud Storage : https://console.cloud.google.com/storage
3. Ouvrez une issue sur GitHub

---

**Générez votre première vidéo virale maintenant ! 🎬🔥**

```bash
curl -X POST $SCRIPT_URL -H "Content-Type: application/json" \
  -d '{"theme": "Votre idée de vidéo virale ici"}'
```