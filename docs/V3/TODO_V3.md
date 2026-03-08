# 📋 V3 - Plan d'Implémentation

> Dernière mise à jour : 8 mars 2026
> 
> **Principe** : On implémente phase par phase. À la fin de chaque phase, on debug, déploie et teste ensemble.
> 
> **Logs** : Cloud Logging uniquement (vue sauvegardée Log Explorer). Pas de page logs in-app.
> 
> **V2.1** : On ne touche pas, on ne redéploie pas. C'est le portfolio.

---

## Modèles IA V3

| Modèle | ID | Usage |
|--------|-----|-------|
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | Scripts, Chat IA, Suggestions TikTok |
| Veo 3.1 GA | `veo-3.1-generate-001` | Vidéo production |
| Veo 3.1 Fast GA | `veo-3.1-fast-generate-001` | Vidéo tests dev (moins cher) |
| Imagen 4 | `imagen-4.0-generate-001` | Personnages + Thumbnails |
| Gemini TTS | `gemini-2.5-pro-tts` | Voix Off (optionnel, Veo a audio natif) |
| Whisper | OpenAI Whisper | Sous-titres |

> ⚠️ Deadline : modèles preview supprimés le **2 avril 2026**.

---

## Phase 0 : Agent Video Veo 3.1 Extensions ⚠️ BLOQUANT

**But** : Résoudre le problème des coupures audio. Valider que Veo 3.1 extensions fonctionne.

### Implémentation

- [ ] `agent-video-veo31/main.py` — Génération vidéo initiale 8s + déclenchement
- [ ] `agent-video-veo31/monitor_extensions.py` — Polling + extensions séquentielles 7s
- [ ] `agent-video-veo31/requirements.txt`
- [ ] `tests/unit/test_veo31_extensions.py` — Tests calculs (sans API)

### Debug & Test

- [ ] Exécuter tests unitaires localement
- [ ] Déployer Cloud Function Gen2 + Cloud Scheduler (polling 30s)
- [ ] Test réel 8s → vérifier vidéo + audio
- [ ] Test réel 15s (1 extension) → vérifier audio continu
- [ ] Test réel 22s (2 extensions) → vérifier audio continu

**Critère de succès** : Vidéo 22s avec audio natif continu, zéro coupure.

---

## Phase 1 : Backend V3

**But** : Backend séparé avec Firebase Auth, projets, personnages, scénarios, vidéos.

### 1A — Setup + Auth Firebase

- [ ] Copier `backend/` → `backend-v3/`
- [ ] Nettoyer code V2 (virer references V1, adapter config)
- [ ] `backend-v3/app/config.py` — Config V3 (bucket V3, Firebase)
- [ ] `backend-v3/app/models/project.py`
- [ ] `backend-v3/app/models/character.py`
- [ ] `backend-v3/app/models/scenario.py`
- [ ] `backend-v3/app/models/video.py`
- [ ] `backend-v3/app/routers/auth.py` — Firebase Auth Google + code accès post-login + JWT V3
- [ ] `backend-v3/app/main.py` — FastAPI V3 avec tous les routers

### 1B — Projets + Personnages

- [ ] `backend-v3/app/routers/projects.py` — CRUD projets TikTok
- [ ] `backend-v3/app/services/chat_service.py` — Chat Gemini 3.1 Pro (personnages + scénarios)
- [ ] `backend-v3/app/routers/characters.py` — Chat IA + génération Imagen 4
- [ ] `backend-v3/app/services/character_service.py` — Imagen 4 (`imagen-4.0-generate-001`)

### 1C — Scénarios + Vidéos + TikTok

- [ ] `backend-v3/app/routers/scenarios.py` — Chat IA + upload fichiers + validation
- [ ] `backend-v3/app/routers/videos.py` — Lancer génération + statut + download
- [ ] `backend-v3/app/routers/tiktok.py` — Suggestions profil, hashtags, titres
- [ ] `backend-v3/app/services/notification_service.py` — Email quand vidéo terminée
- [ ] `backend-v3/app/routers/websocket.py` — Suivi temps réel génération

### Debug & Test

- [ ] `docker-compose -f docker-compose.v3.yml up` — Backend V3 local
- [ ] Tester auth flow : Google login → code → JWT → API
- [ ] Tester CRUD projets via Swagger `/docs`
- [ ] Tester chat personnage via `/api/v3/characters/chat`
- [ ] Tester génération Imagen 4 via `/api/v3/characters/generate`
- [ ] Tester chat scénario avec upload fichier
- [ ] Tester lancement génération vidéo

---

## Phase 2 : Agent Thumbnail

**But** : Générer des landing pages / thumbnails TikTok attractives.

### Implémentation

- [ ] `agent-thumbnail/main.py` — Imagen 4, format 9:16 (768×1408)
- [ ] `agent-thumbnail/requirements.txt`
- [ ] Intégrer dans le flow : vidéo terminée → générer thumbnail

### Debug & Test

- [ ] Test réel : générer 1 thumbnail depuis un thème + personnage
- [ ] Vérifier qualité image et format 9:16

---

## Phase 3 : Frontend V3

**But** : Interface complète pour gérer projets, personnages, scénarios, vidéos.

### 3A — Setup + Auth + Navigation

- [ ] `frontend-v3/` — Vite + React + TypeScript + TailwindCSS
- [ ] Firebase JS SDK + Google Auth provider
- [ ] Page `Login.jsx` — Google Sign-In + Code d'accès
- [ ] Layout Sidebar : Projets / Personnages / Vidéos
- [ ] Composant `ChatInterface.jsx` — Réutilisable (chat IA)
- [ ] Composant `FileUploader.jsx` — Drag & drop fichiers/images
- [ ] Composant `VideoPlayer.jsx` — Lecteur vidéo + thumbnail

### 3B — Projets + Personnages

- [ ] Page `Dashboard.jsx` — Liste projets + stats
- [ ] Page `ProjectCreate.jsx` — Formulaire (nom, thème, description)
- [ ] Page `ProjectDetail.jsx` — Vue projet avec onglets
- [ ] Page `CharacterChat.jsx` — Chat IA pour personnages + bouton "Générer"
- [ ] Page `CharacterGallery.jsx` — Galerie personnages du projet

### 3C — Scénarios + Vidéos

- [ ] Page `ScenarioChat.jsx` — Chat IA + upload fichiers + sélection durée + validation
- [ ] Page `VideoGeneration.jsx` — WebSocket suivi temps réel + barre progression
- [ ] Page `VideoLibrary.jsx` — Lecteur inline + download + copier hashtags/titre

### Debug & Test

- [ ] `npm run dev` — Frontend V3 local
- [ ] Tester login Google + code accès
- [ ] Tester flow complet : Projet → Personnage → Scénario → Vidéo → Download
- [ ] Vérifier responsive mobile (TikTok = mobile first)

---

## Phase 4 : Terraform V3 + Deploy + CI/CD

**But** : Infrastructure séparée, déploiement automatique.

### Implémentation

- [ ] `terraform-v3/main.tf` — Provider, projet
- [ ] `terraform-v3/variables.tf`
- [ ] `terraform-v3/cloud-run.tf` — backend-v3 + frontend-v3
- [ ] `terraform-v3/cloud-functions.tf` — agent-video-veo31, agent-thumbnail
- [ ] `terraform-v3/firestore.tf` — Collections V3
- [ ] `terraform-v3/storage.tf` — Buckets V3 (videos, uploads, thumbnails) + CORS
- [ ] `terraform-v3/monitoring.tf` — Dashboard Cloud Monitoring
- [ ] `terraform-v3/terraform.tfvars`
- [ ] `.github/workflows/deploy-v3.yml` — CI/CD séparé du V2
- [ ] Configurer Firebase Auth (authorized domains)
- [ ] Vue sauvegardée Cloud Logging (filtre multi-services V3)

### Debug & Test

- [ ] `terraform init && terraform plan` — Vérifier
- [ ] `terraform apply` — Déployer
- [ ] Test end-to-end en production V3
- [ ] Vérifier que V2.1 (reetik.ldjossou.com) n'est pas impacté

---

## Phase 5 : Tests + Polish

**But** : Stabiliser avant de commencer à produire du contenu TikTok.

- [ ] Tests backend-v3 : `pytest`
  - [ ] Auth (Firebase + JWT + code)
  - [ ] CRUD projets
  - [ ] Chat personnages / scénarios
  - [ ] Génération vidéo
- [ ] Tests frontend-v3 : Playwright E2E
  - [ ] Login → Projet → Personnage → Scénario → Vidéo → Download
- [ ] Fix bugs trouvés pendant les tests
- [ ] Optimisations UX : loading states, messages d'erreur clairs
- [ ] Premier vrai projet TikTok créé 🚀

---

## Résumé

```
Phase 0  →  agent-video-veo31 (fix coupures audio)
Phase 1  →  backend-v3 (FastAPI, auth, projets, chat, vidéos)
Phase 2  →  agent-thumbnail (Imagen 4, landing pages TikTok)
Phase 3  →  frontend-v3 (React, interface complète)
Phase 4  →  terraform-v3 + deploy + CI/CD
Phase 5  →  tests + polish + premier projet TikTok
```

Chaque phase se termine par : **debug ensemble → deploy → test → valider → passer à la suivante.**
