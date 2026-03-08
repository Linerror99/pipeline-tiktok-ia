# 📋 TODO V3 - Plan d'Exécution

> Dernière mise à jour : 8 mars 2026

---

## Phase 0 : Fix Veo 3.1 Extensions (Semaines 1-2) ⚠️ CRITIQUE

**Objectif** : Valider que les extensions Veo 3.1 fonctionnent avant de construire la V3.

### Semaine 1 : Tests Extensions

- [ ] Créer `agent-video-veo31/main.py` (logique initiale 8s)
- [ ] Créer `agent-video-veo31/monitor_extensions.py` (polling + extensions séquentielles)
- [ ] Créer `agent-video-veo31/requirements.txt`
- [ ] Créer `tests/unit/test_veo31_extensions.py` (tests logique pure, pas d'API)
- [ ] Exécuter tests unitaires → valider calculs durées/extensions
- [ ] Créer `tests/integration/test_veo31_real.py` (test avec vraie API)
- [ ] **TEST RÉEL** : Générer 1 vidéo 8s avec `veo-3.1-generate-001`
- [ ] **TEST RÉEL** : Générer 1 vidéo 15s (8s + 1 extension 7s)
- [ ] **TEST RÉEL** : Générer 1 vidéo 22s (8s + 2 extensions 7s)
- [ ] Vérifier audio continu sur toutes les vidéos test

### Semaine 2 : Intégration

- [ ] Déployer `agent-video-veo31` comme Cloud Function Gen2
- [ ] Tester déclenchement par upload `script_v3.json` dans bucket
- [ ] Configurer Cloud Scheduler pour polling extensions (toutes les 30s)
- [ ] Tester flow complet : script → vidéo initiale → extensions → vidéo finale
- [ ] Valider upload vidéo finale dans Cloud Storage
- [ ] Documenter les résultats (durée, coût, qualité audio)

**Critère de succès** : Une vidéo de 22s avec audio natif continu, sans coupures.

---

## Phase 1 : Backend V3 Foundation (Semaines 3-5)

### Semaine 3 : Setup + Auth Firebase

- [ ] Copier `backend/` → `backend-v3/`
- [ ] Nettoyer le code V2 non nécessaire dans backend-v3
- [ ] Installer `firebase-admin` dans requirements.txt
- [ ] Implémenter Firebase Auth Google dans `backend-v3/app/routers/auth.py`
  - [ ] Endpoint `POST /api/v3/auth/login` (vérifier Firebase ID token)
  - [ ] Endpoint `GET /api/v3/auth/me` (user info)
  - [ ] Endpoint `POST /api/v3/auth/verify-code` (code d'accès post-login)
  - [ ] Middleware JWT V3 interne
- [ ] Créer `backend-v3/app/models/project.py` (Pydantic models)
- [ ] Créer `backend-v3/app/models/character.py`
- [ ] Créer `backend-v3/app/models/scenario.py`
- [ ] Créer `backend-v3/app/models/video.py` (V3)
- [ ] Tester auth flow : Google login → Code → JWT → API access

### Semaine 4 : Projets + Personnages

- [ ] Créer `backend-v3/app/routers/projects.py`
  - [ ] `POST /api/v3/projects/` (créer projet TikTok)
  - [ ] `GET /api/v3/projects/` (lister mes projets)
  - [ ] `GET /api/v3/projects/{id}` (détail)
  - [ ] `PATCH /api/v3/projects/{id}` (modifier)
  - [ ] `DELETE /api/v3/projects/{id}` (supprimer)
- [ ] Créer `backend-v3/app/services/chat_service.py`
  - [ ] Initialiser Gemini 3.1 Pro (`gemini-3.1-pro-preview`)
  - [ ] Chat contextuel pour caractéristiques personnages
  - [ ] Chat contextuel pour scénarios avec fichiers uploadés
- [ ] Créer `backend-v3/app/routers/characters.py`
  - [ ] `POST /api/v3/characters/chat` (discussion IA)
  - [ ] `POST /api/v3/characters/generate` (Imagen 4)
  - [ ] `GET /api/v3/characters/?project_id=...` (lister)
  - [ ] `PATCH /api/v3/characters/{id}` (modifier)
  - [ ] `POST /api/v3/characters/{id}/regenerate` (re-générer image)
- [ ] Créer `backend-v3/app/services/character_service.py`
  - [ ] Intégration Imagen 4 (`imagen-4.0-generate-001`)
  - [ ] Génération image 9:16 depuis description
  - [ ] Sauvegarde reference_images dans Storage

### Semaine 5 : Scénarios + Vidéos + TikTok

- [ ] Créer `backend-v3/app/routers/scenarios.py`
  - [ ] `POST /api/v3/scenarios/chat` (discussion IA avec contexte)
  - [ ] `POST /api/v3/scenarios/upload` (fichiers/images)
  - [ ] `POST /api/v3/scenarios/validate` (valider → prêt génération)
  - [ ] `GET /api/v3/scenarios/?project_id=...` (lister)
- [ ] Implémenter analyse fichiers uploadés dans chat_service.py
  - [ ] Support images : Gemini 3.1 Pro vision
  - [ ] Support documents : PDF, TXT analyse
- [ ] Créer `backend-v3/app/routers/videos.py` (V3)
  - [ ] `POST /api/v3/videos/generate` (lancer depuis scénario validé)
  - [ ] `GET /api/v3/videos/?project_id=...` (lister)
  - [ ] `GET /api/v3/videos/{id}/status` (polling statut)
  - [ ] `GET /api/v3/videos/{id}/download` (URL signée)
- [ ] Créer `backend-v3/app/routers/tiktok.py`
  - [ ] `POST /api/v3/tiktok/suggest-profile` (suggestions profil)
  - [ ] `POST /api/v3/tiktok/suggest-hashtags` (hashtags par thème)
  - [ ] `POST /api/v3/tiktok/suggest-title` (titres accrocheurs)
- [ ] Créer `backend-v3/app/services/notification_service.py`
  - [ ] Notification email quand vidéo terminée (SendGrid ou SMTP)
- [ ] Créer `backend-v3/app/routers/websocket.py` (temps réel)

---

## Phase 2 : Frontend V3 (Semaines 6-8)

### Semaine 6 : Setup + Auth + Navigation

- [ ] Créer `frontend-v3/` (Vite + React + TypeScript + TailwindCSS)
- [ ] Installer Firebase JS SDK
- [ ] Configurer `firebase.js` (Google Auth provider)
- [ ] Page Login : Google Sign-In + Code d'accès
- [ ] Layout principal : Sidebar navigation
  - [ ] Projets
  - [ ] Personnages
  - [ ] Vidéos
  - [ ] Admin (Logs)
- [ ] Composant `ChatInterface.jsx` réutilisable (chat IA)
- [ ] Composant `FileUploader.jsx` (drag & drop)

### Semaine 7 : Projets + Personnages

- [ ] Page `Dashboard.jsx` : Liste projets avec stats
- [ ] Page `ProjectCreate.jsx` : Formulaire création projet
  - [ ] Nom, thème (dropdown : foot/manga/food/tech/tout/custom)
  - [ ] Suggestions profil TikTok par IA
- [ ] Page `ProjectDetail.jsx` : Vue projet avec onglets
  - [ ] Onglet personnages
  - [ ] Onglet vidéos
  - [ ] Onglet stats
- [ ] Page `CharacterChat.jsx` : Interface chat IA
  - [ ] Discussion itérative pour définir personnage
  - [ ] Bouton "Générer" quand caractéristiques validées
  - [ ] Affichage image générée (Imagen 4)
  - [ ] Option "Re-générer"
- [ ] Page `CharacterGallery.jsx` : Galerie des personnages du projet

### Semaine 8 : Scénarios + Vidéos + Admin

- [ ] Page `ScenarioChat.jsx` : Chat IA pour scénarios
  - [ ] Upload fichiers/images pendant la discussion
  - [ ] IA analyse les fichiers et les intègre au contexte
  - [ ] Prévisualisation script (blocs VISUEL + DIALOGUE)
  - [ ] Sélection durée : 8s / 15s / 22s / 29s / 36s / 43s / 50s / 57s
  - [ ] Bouton "Valider scénario"
  - [ ] Affichage hashtags + titre TikTok suggérés
- [ ] Page `VideoGeneration.jsx` : Suivi temps réel
  - [ ] WebSocket : progression génération
  - [ ] Barre de progression par étape (initial → ext 1 → ext 2 → ...)
  - [ ] Notification quand terminé
- [ ] Page `VideoLibrary.jsx` : Toutes les vidéos du projet
  - [ ] Lecteur vidéo inline
  - [ ] Thumbnail affichée
  - [ ] Bouton download vidéo + thumbnail
  - [ ] Copier hashtags + titre en 1 clic
- [ ] Page `AdminLogs.jsx` : Logs centralisés
  - [ ] Connexion SSE pour logs temps réel
  - [ ] Filtres : service, sévérité, période
  - [ ] Auto-scroll + pause

---

## Phase 3 : Logs Centralisés (Semaine 5, en parallèle)

### Backend

- [ ] Créer `backend-v3/app/services/log_service.py`
  - [ ] Wrapper Cloud Logging API v2 (`entries.list()`)
  - [ ] Filtre multi-services (backend-v3 + tous les agents)
  - [ ] Stream SSE (Server-Sent Events)
- [ ] Créer `backend-v3/app/routers/admin.py`
  - [ ] `GET /api/v3/admin/logs` (SSE stream)
  - [ ] Paramètres : `service`, `severity`, `since`, `limit`
  - [ ] `GET /api/v3/admin/stats` (stats globales)
- [ ] Standardiser format logs JSON dans tous les agents V3
  - [ ] Champs obligatoires : `service`, `trace_id`, `video_id`, `event`, `severity`
  - [ ] Créer librairie partagée `shared/logging_config.py`

### Cloud Logging (immédiat)

- [ ] Créer vue sauvegardée Log Explorer (filtre multi-services)
- [ ] Configurer log sink dans `terraform-v3/logging.tf`
- [ ] Bookmark URL pour accès rapide

---

## Phase 4 : Terraform V3 + Deploy (Semaines 9-10)

### Semaine 9 : Infrastructure

- [ ] Créer `terraform-v3/main.tf` (provider, project V3)
- [ ] Créer `terraform-v3/variables.tf`
- [ ] Créer `terraform-v3/cloud-run.tf`
  - [ ] Service backend-v3 (Cloud Run)
  - [ ] Service frontend-v3 (Cloud Run)
- [ ] Créer `terraform-v3/cloud-functions.tf`
  - [ ] agent-video-veo31 (Cloud Function Gen2)
  - [ ] agent-chat (si Cloud Function, sinon dans backend-v3)
  - [ ] agent-thumbnail (Cloud Function Gen2)
  - [ ] monitor-extensions-v3 (Cloud Scheduler + Function)
- [ ] Créer `terraform-v3/firestore.tf` (collections V3)
- [ ] Créer `terraform-v3/storage.tf`
  - [ ] Bucket: v3-videos
  - [ ] Bucket: v3-uploads
  - [ ] Bucket: v3-thumbnails
  - [ ] CORS config
- [ ] Créer `terraform-v3/monitoring.tf` (dashboard V3)
- [ ] Créer `terraform-v3/logging.tf` (log sinks centralisés)
- [ ] Créer `terraform-v3/terraform.tfvars`

### Semaine 10 : Deploy + CI/CD

- [ ] `terraform init && terraform plan` (vérifier)
- [ ] `terraform apply` (déployer infrastructure V3)
- [ ] Créer `.github/workflows/deploy-v3.yml`
  - [ ] Build + push backend-v3 image
  - [ ] Build + push frontend-v3 image
  - [ ] Deploy Cloud Run services
  - [ ] Deploy Cloud Functions agents
- [ ] Configurer domaine v3 (ou subdomain)
- [ ] Configurer Firebase Auth (Authorized domains)
- [ ] Test end-to-end en production V3

---

## Phase 5 : Tests Complets (Semaine 10, en parallèle)

- [ ] Tests backend-v3 : `pytest backend-v3/tests/`
  - [ ] `test_auth.py` (Firebase + JWT + code accès)
  - [ ] `test_projects.py` (CRUD projets)
  - [ ] `test_characters.py` (chat + génération)
  - [ ] `test_scenarios.py` (chat + upload + validation)
  - [ ] `test_videos.py` (génération + statut + download)
- [ ] Tests frontend-v3 : Playwright E2E
  - [ ] Login Google → Code → Dashboard
  - [ ] Créer projet → Personnage → Scénario → Vidéo
  - [ ] Download vidéo
  - [ ] Logs admin
- [ ] Coverage > 70% backend
- [ ] CI/CD : tests automatiques sur PR

---

## Phase 6 : Thumbnails TikTok (Semaine 8, en parallèle)

- [ ] Créer `agent-thumbnail/main.py`
  - [ ] Imagen 4 (`imagen-4.0-generate-001`)
  - [ ] Format 9:16 (768×1408)
  - [ ] Prompt : thème + personnage + style accrocheur
- [ ] Créer `agent-thumbnail/requirements.txt`
- [ ] Tests : `tests/unit/test_agent_thumbnail.py`
- [ ] Intégrer dans le flow de génération vidéo
  - [ ] Après vidéo terminée → générer thumbnail
  - [ ] Sauvegarder dans Storage + Firestore

---

## Récap Timeline

```
Semaine 1-2  : Phase 0 - Fix Veo 3.1 Extensions ⚠️
Semaine 3-5  : Phase 1 - Backend V3
Semaine 5    : Phase 3 - Logs Centralisés (en parallèle)
Semaine 6-8  : Phase 2 - Frontend V3
Semaine 8    : Phase 6 - Thumbnails (en parallèle)
Semaine 9-10 : Phase 4 - Terraform V3 + Deploy
Semaine 10   : Phase 5 - Tests Complets
```

**Total : ~10 semaines (2.5 mois)**

**Premier test TikTok réel : fin Semaine 10** 🚀

---

## Modèles IA Utilisés

| Modèle | ID | Usage |
|--------|-----|-------|
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | Scripts, Chat IA, Suggestions TikTok |
| Veo 3.1 GA | `veo-3.1-generate-001` | Vidéo production |
| Veo 3.1 Fast GA | `veo-3.1-fast-generate-001` | Vidéo tests dev |
| Imagen 4 | `imagen-4.0-generate-001` | Personnages + Thumbnails |
| Gemini TTS | `gemini-2.5-pro-tts` | Voix Off (optionnel V3, Veo audio natif) |
| Whisper | OpenAI Whisper | Sous-titres |

> ⚠️ **Deadline migration** : 2 avril 2026 - tous les modèles preview supprimés.
> `gemini-3-pro-preview` supprimé le 26 mars 2026.
