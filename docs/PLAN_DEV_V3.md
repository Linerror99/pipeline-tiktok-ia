# PLAN DE DÉVELOPPEMENT V3 — REETIK

> Version : 2026-04-23  
> À valider avant toute implémentation

---

## Vue d'ensemble

Trois chantiers séquentiels :

| # | Chantier | Priorité |
|---|----------|----------|
| 1 | Nettoyage Cloud + Test génération vidéo | Urgent |
| 2 | Refonte UX frontend (sidebar + multi-entités) | Haute |
| 3 | Onglet TikTok par vidéo | Basse |

---

## CHANTIER 1 — Nettoyage Cloud + Génération Vidéo

### 1.1 Services Cloud Run à supprimer (via Terraform uniquement)

**Services à GARDER** (portfolio V2) :

| Service | Raison |
|---------|--------|
| `tiktok-backend` | Portfolio V2 — déjà dans `cloud-run.tf` |
| `tiktok-frontend` | Portfolio V2 — déjà dans `cloud-run.tf` |

**Services à SUPPRIMER :**

| Service | Statut Terraform | Action |
|---------|-----------------|--------|
| `rotate-access-code` | ✅ Dans `functions.tf` + `scheduler.tf` | Supprimer les blocs → `terraform apply` |
| `check-and-retry-clips` | ❌ Hors Terraform | Import → remove → `terraform apply` |
| `agent-assembler-v2` | ❌ Hors Terraform | Import → remove → `terraform apply` |
| `agent-script-v2` | ❌ Hors Terraform | Import → remove → `terraform apply` |
| `agent-video-v2` | ❌ Hors Terraform | Import → remove → `terraform apply` |

**Stratégie Terraform pour les services hors état :**

Créer `terraform/cleanup-v2.tf` avec un `null_resource` qui déclenche la suppression via `gcloud` lors du `terraform apply` :

```hcl
# terraform/cleanup-v2.tf
resource "null_resource" "delete_v2_orphan_services" {
  provisioner "local-exec" {
    command = <<-EOT
      gcloud run services delete check-and-retry-clips --region us-central1 --quiet --project ${var.project_id} || true
      gcloud run services delete agent-assembler-v2     --region us-central1 --quiet --project ${var.project_id} || true
      gcloud run services delete agent-script-v2        --region us-central1 --quiet --project ${var.project_id} || true
      gcloud run services delete agent-video-v2         --region us-central1 --quiet --project ${var.project_id} || true
    EOT
  }
}
```

Une fois appliqué et les services supprimés, supprimer ce fichier et re-appliquer (le `null_resource` disparaît proprement).

Pour `rotate-access-code` : supprimer les blocs dans `functions.tf` et `scheduler.tf` → `terraform apply` le détruira automatiquement.

---

### 1.2 Déploiement V3 via Terraform

Créer `terraform/cloud-run-v3.tf` avec les services V3 :
- `backend-v3` (FastAPI, port 8080, image `...backend-v3:latest`)
- `reetik-frontend-v3` (nginx, port 80, image `...frontend-v3:latest`)

Ces services remplacent fonctionnellement V2 pour les nouveaux usages.

---

### 1.3 Génération vidéo — Architecture révisée

**Modèle :** `veo-3.1-generate-001`  
**Location :** `global`  
**SDK :** `google-genai` (`pip install google-genai`)  
**Modèle extension :** `veo-3.1-generate-preview` (ajoute 7s à partir d'un clip existant)

**Stratégie de génération par durée cible :**

```
target = 8s  → 1 génération  (8s)
target = 15s → 1 génération  (8s) + 1 extension  (7s) → trim 15s
target = 22s → 1 génération  (8s) + 2 extensions (14s) → trim 22s
target = 29s → 1 génération  (8s) + 3 extensions (21s) → trim 29s
...
```

**Flux détaillé :**

```
POST /api/v3/videos/generate
  ① Créer VideoRecord Firestore (status: pending)
  ② Lancer BackgroundTask (non bloquant)
  ③ Retourner { id: video_id } immédiatement

BackgroundTask generate_video_background(video_id):
  ① Construire le prompt depuis les blocs du script + descriptions personnages
  ② Appeler Veo 3.1: operation = client.models.generate_videos(model, prompt, config)
     - Boucle while not operation.done: sleep(15) + operation = client.operations.get(op)
     - Mettre à jour Firestore { status: "generating", progress: X% } à chaque itération
  ③ Si target > 8s: boucler sur extensions avec veo-3.1-generate-preview
     - Input: clip précédent (URI GCS)
     - Output: clip de 7s supplémentaires
     - Mettre à jour progress
  ④ Concaténer les clips avec ffmpeg (moviepy ou subprocess)
  ⑤ Upload final.mp4 → GCS reetik-v3-artifacts/{video_id}/final.mp4
  ⑥ Mettre à jour Firestore { status: "completed", video_url: "gs://..." }
  En cas d'erreur: Firestore { status: "failed", error: "..." }
```

**Résolution des blocs du scénario en prompts Veo :**

Le scénario contient des blocs `VISUEL` / `DIALOGUE`. Pour le prompt Veo :
- Concaténer tous les blocs dans un seul prompt (meilleure cohérence)
- Inclure la description complète du personnage (nom, look, traits) dans chaque prompt
- Format : `"[CONTEXT personnage]. [VISUEL bloc1]. [DIALOGUE bloc2]. ..."`

**Code de base du service :**

```python
import os
from google import genai
from google.genai.types import GenerateVideosConfig, Video

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "reetik-project"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

client = genai.Client()

# Génération initiale
operation = client.models.generate_videos(
    model="veo-3.1-generate-001",
    prompt=prompt,
    config=GenerateVideosConfig(
        aspect_ratio="9:16",
        output_gcs_uri=f"gs://reetik-v3-artifacts/{video_id}/clip_0.mp4",
    ),
)
while not operation.done:
    await asyncio.sleep(15)
    operation = client.operations.get(operation)
    # MAJ Firestore progress

# Extension (si target > 8s)
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=continuation_prompt,
    video=Video(uri=f"gs://reetik-v3-artifacts/{video_id}/clip_0.mp4", mime_type="video/mp4"),
    config=GenerateVideosConfig(
        output_gcs_uri=f"gs://reetik-v3-artifacts/{video_id}/clip_1.mp4",
    ),
)
```

---

### 1.4 WebSocket — Temps réel avec reconnexion

**Choix retenu :** WebSocket dynamique avec gestion d'échecs (pas de simple polling HTTP)

**Fonctionnement :**
- La BackgroundTask écrit dans Firestore à chaque étape
- L'endpoint WS (`/api/v3/videos/{video_id}/ws`) lit Firestore en boucle et pousse les mises à jour
- Si la connexion WS est coupée : le client se reconnecte et reprend l'état courant depuis Firestore
- La génération continue côté serveur indépendamment des connexions WS

**Messages WebSocket types :**
```json
{ "status": "generating", "progress": 35, "step": "Génération clip initial...", "detail": "Veo processing..." }
{ "status": "extending", "progress": 65, "step": "Extension clip 1/2..." }
{ "status": "completed", "progress": 100, "video_url": "https://storage.googleapis.com/..." }
{ "status": "failed", "error": "Veo API error: ..." }
```

**Gestion reconnexion côté frontend :**
```js
function connectWs(videoId, onMessage, onClose) {
  const ws = new WebSocket(...)
  ws.onmessage = onMessage
  ws.onerror = () => ws.close()
  ws.onclose = () => {
    // Si toujours en cours: reconnect après 3s
    setTimeout(() => connectWs(videoId, onMessage, onClose), 3000)
  }
  return ws
}
```

**Fichiers à créer/modifier :**
- `backend-v3/app/services/video_service.py` — **Créer**
- `backend-v3/app/routers/videos.py` — Modifier `generate` + ajouter endpoint WS
- `backend-v3/requirements.txt` — Ajouter `google-genai`, `ffmpeg-python`
- `terraform/cleanup-v2.tf` — **Créer** (suppression services orphelins)
- `terraform/functions.tf` — Supprimer bloc `rotate_access_code`
- `terraform/scheduler.tf` — Supprimer bloc `rotate_access_code_hourly`
- `terraform/cloud-run-v3.tf` — **Créer** (déploiement V3)

---

## CHANTIER 2 — Refonte UX Frontend

### 2.1 Layout global : sidebar gauche

**Actuel :** onglets horizontaux en haut → scroll obligatoire pour y accéder.

**Nouveau :**
```
┌─────────────────────────────────────────────┐
│  Header (logo + user)                       │
├──────────┬──────────────────────────────────┤
│          │                                  │
│ SIDEBAR  │   CONTENU PRINCIPAL              │
│ (fixe)   │   (scrollable)                   │
│          │                                  │
│ 👤 Perso │                                  │
│ 📝 Scéna │                                  │
│ 🎬 Vidéo │                                  │
│ # TikTok │                                  │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

La sidebar est `sticky top-0 h-screen` — toujours visible même en scrollant.

**Fichiers à modifier :**
- `frontend-v3/src/pages/ProjectPage.jsx` — layout flex row + sidebar
- Tous les onglets — pas de changement de logique, juste le container parent

---

### 2.2 Onglet Personnages — Multi-personnages

**Actuel :** un seul fil de chat, restaure le dernier personnage au chargement.

**Nouveau :**

```
┌─── Personnages ─────────────────────────────┐
│  [+ Nouveau personnage]                     │
│                                             │
│  ┌── Héros ─────────────────────────────┐   │
│  │  🖼 [image]  Héros • Prêt           │   │
│  │  Traits : courageux, jeune...        │   │
│  │  [Voir chat] [Régénérer image]       │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌── Méchant ───────────────────────────┐   │
│  │  🖼 [image]  Méchant • En cours     │   │
│  │  [Voir chat]                         │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  [clic sur un personnage → ouvre son chat]  │
└─────────────────────────────────────────────┘
```

**UX flow :**
1. Page d'accueil de l'onglet = liste des personnages existants
2. Clic "+ Nouveau personnage" → ouvre le chat IA (crée un nouveau personnage via l'API)
3. Clic sur une carte personnage → ouvre son chat IA historique
4. Depuis le chat : bouton "Générer l'image" → appel `/characters/{id}/generate`
5. L'IA a accès à TOUS les personnages du projet (contexte côté backend, pas de changement)

**États d'un personnage :**
- `draft` — chat en cours, pas encore d'image
- `ready` — image générée, prêt pour un scénario

**Fichiers à modifier :**
- `frontend-v3/src/components/project/CharactersTab.jsx` — refonte complète
- Pas de changement backend

---

### 2.3 Onglet Scénarios — Multi-scénarios + prérequis personnage

**Actuel :** un seul scénario, restaure le dernier au chargement. Pas de vérification personnage.

**Nouveau :**

```
┌─── Scénarios ───────────────────────────────┐
│                                             │
│  ⚠️ [Si aucun personnage prêt]              │
│  "Créez au moins un personnage avant..."    │
│                                             │
│  [+ Nouveau scénario]  (désactivé si pas   │
│                         de personnage prêt) │
│                                             │
│  ┌── Scénario 1 ────────────────────────┐   │
│  │  "La quête du héros" • ✅ Validé    │   │
│  │  22s • 3 blocs                       │   │
│  │  [Voir scénario]                     │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌── Scénario 2 ────────────────────────┐   │
│  │  "Introduction" • 🕐 En cours       │   │
│  │  [Continuer le chat]                 │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**UX flow :**
1. Chargement = liste scénarios + liste personnages (pour vérifier prérequis)
2. Si aucun personnage avec `status=ready` → message + bouton désactivé
3. Clic "+ Nouveau scénario" → chat IA (nouveau scénario)
4. Clic sur un scénario → ouvre son chat IA (continuer ou voir)
5. Depuis le chat : sélecteur de durée + bouton "Valider le scénario"
6. Après validation : carte scénario passe à "Validé"

**Prérequis à implémenter côté frontend uniquement** (backend n'a pas à valider ça).

**Fichiers à modifier :**
- `frontend-v3/src/components/project/ScenarioTab.jsx` — refonte complète

---

### 2.4 Onglet Vidéos — Lié aux scénarios validés

**Actuel :** liste toutes les vidéos + bouton "Générer la vidéo" global.

**Nouveau :**

```
┌─── Vidéos ──────────────────────────────────┐
│                                             │
│  SCÉNARIOS VALIDÉS                          │
│  ┌── Scénario 1 ────────────────────────┐   │
│  │  "La quête du héros" • 22s           │   │
│  │                                      │   │
│  │  [Vidéo générée]  ▶ 00:22  ⬇        │   │
│  │  ou                                  │   │
│  │  [⚡ Générer la vidéo]               │   │
│  │  ou                                  │   │
│  │  [⏳ Génération en cours... 34%]     │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌── Scénario 2 ────────────────────────┐   │
│  │  "Introduction" • 8s                 │   │
│  │  [⚡ Générer la vidéo]               │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**UX flow :**
1. Chargement = liste scénarios validés + liste vidéos associées
2. Chaque carte scénario affiche l'état de sa vidéo (si elle existe)
3. Clic "Générer" → `POST /api/v3/videos/generate` avec `scenario_id`
4. Polling toutes les 10s sur `GET /api/v3/videos/{id}/status`
5. **La génération continue côté serveur** si l'utilisateur quitte la page
   - Au retour : le polling reprend depuis Firestore
6. Quand terminée : aperçu vidéo + bouton télécharger

**Fichiers à modifier :**
- `frontend-v3/src/components/project/VideosTab.jsx` — refonte complète

---

### 2.5 Onglet TikTok — Par vidéo (pas par projet)

**Actuel :** Bio + Hashtags + Titre générés pour le projet entier.

**Nouveau :**
- **Bio de profil** → reste globale au projet (1 seule bio par compte TikTok)
- **Titre de vidéo** → par vidéo : bouton "Suggérer un titre" depuis la carte vidéo
- **Hashtags** → par vidéo : bouton "Suggérer des hashtags" depuis la carte vidéo

```
┌─── TikTok ──────────────────────────────────┐
│                                             │
│  BIO DE PROFIL (par compte)                 │
│  ┌─────────────────────────────────────┐    │
│  │ [Générer une bio]                   │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  CONTENU PAR VIDÉO                          │
│  ┌── Vidéo : "La quête du héros" ──────┐   │
│  │  Titre : [Suggérer un titre]        │   │
│  │  Hashtags : [Suggérer des hashtags] │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Changements nécessaires :**
- Backend : ajouter endpoints `POST /tiktok/suggest-title-for-video/{video_id}` et `POST /tiktok/suggest-hashtags-for-video/{video_id}` (ou passer `video_id` aux endpoints existants)
- Frontend : `TikTokTab.jsx` — refonte pour séparer bio/per-video

---

## Résumé des fichiers à créer/modifier

### Infrastructure (terraform/)
| Fichier | Action | Chantier |
|---------|--------|----------|
| `cleanup-v2.tf` | **Créer** — supprimer services V2 orphelins | 1 |
| `functions.tf` | Supprimer bloc `rotate_access_code` | 1 |
| `scheduler.tf` | Supprimer bloc `rotate_access_code_hourly` | 1 |
| `cloud-run-v3.tf` | **Créer** — déploiement backend-v3 + frontend-v3 | 1 |

### Backend (backend-v3/)
| Fichier | Action | Chantier |
|---------|--------|----------|
| `app/services/video_service.py` | **Créer** — logique Veo + extensions + ffmpeg | 1 |
| `app/routers/videos.py` | Modifier — BackgroundTask + endpoint WS | 1 |
| `requirements.txt` | Ajouter `google-genai`, `ffmpeg-python` | 1 |
| `app/routers/tiktok.py` | Modifier — ajouter endpoints per-video | 3 |

### Frontend (frontend-v3/src/)
| Fichier | Action | Chantier |
|---------|--------|----------|
| `pages/ProjectPage.jsx` | Modifier — layout sidebar gauche fixe | 2 |
| `components/project/CharactersTab.jsx` | Refonte — liste cartes + chat par personnage | 2 |
| `components/project/ScenarioTab.jsx` | Refonte — liste cartes + prérequis + chat par scénario | 2 |
| `components/project/VideosTab.jsx` | Refonte — par scénario validé + WS reconnect | 2 |
| `components/project/TikTokTab.jsx` | Modifier — bio globale + titre/hashtags per-video | 3 |

---

## Séquence d'exécution

```
[1]  Terraform: créer cleanup-v2.tf → terraform apply (supprime services orphelins)
[2]  Terraform: supprimer blocs rotate_access_code → terraform apply
[3]  Implémenter video_service.py (Veo + extensions + ffmpeg)
[4]  Modifier videos.py (BackgroundTask + WebSocket)
[5]  Ajouter google-genai + ffmpeg-python à requirements.txt
[6]  Rebuild backend-v3 local → tester POST /api/v3/videos/generate
[7]  Valider : vidéo générée dans GCS, statut completed, WS fonctionne
[8]  Terraform: créer cloud-run-v3.tf → déployer V3 en prod
[9]  Refonte frontend — layout sidebar gauche
[10] Refonte CharactersTab — multi-personnages
[11] Refonte ScenarioTab — multi-scénarios
[12] Refonte VideosTab — par scénario + WS reconnect
[13] Refonte TikTokTab — per-video
[14] Test pipeline complète end-to-end
```

---

## Questions résolues

| Question | Réponse |
|----------|---------|
| Modèle Veo | `veo-3.1-generate-001`, location `global` |
| SDK | `google-genai` (pas `vertexai`) |
| Extensions | `veo-3.1-generate-preview` + `video=Video(uri=...)` |
| Durée | Génération 8s + extensions 7s jusqu'à cible |
| Polling vs WS | WebSocket avec reconnexion automatique |
| Terraform scope | Toutes les modifications prod passent par Terraform |
| Services à garder | `tiktok-backend` + `tiktok-frontend` (portfolio V2) |
