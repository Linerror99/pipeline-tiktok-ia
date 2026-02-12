# 📋 PLAN DE DÉVELOPPEMENT COMPLET - PIPELINE TIKTOK IA V2. 0

**Objectif** : Transformer le pipeline actuel en système production-ready avec Veo 3.1, personnages récurrents, et 17 améliorations majeures.

---

## 🎯 VISION GLOBALE

### Fonctionnalités finales
- ✅ Génération vidéos 60-90s fluides avec audio natif (Veo 3.1)
- ✅ Personnages récurrents (Nano Banana)
- ✅ Suivi temps réel (WebSocket)
- ✅ Templates de style (7 styles visuels)
- ✅ Multi-langues (FR, EN, ES)
- ✅ Musique de fond
- ✅ Système de favoris et historique
- ✅ Optimisations performance et coûts

---

## 📅 PLANIFICATION PAR PHASES

### **PHASE 1 : MIGRATION VEO 3.1 (FONDATIONS)** 
**Durée estimée :  2-3 semaines**  
**Priorité :  CRITIQUE**

#### Objectif
Remplacer le système actuel (8 clips assemblés) par Veo 3.1 (1 vidéo fluide avec audio natif)

#### Tâches

**1.1 - Agent Script (Veo 3.1)**
- [ ] Modifier prompt Gemini pour format "BLOCS" avec dialogues/effets sonores
- [ ] Ajouter validation :  minimum 4 blocs (60-90s)
- [ ] Tester génération scripts avec différents thèmes
- [ ] Créer document Firestore `video_status` avec champs : `video_id`, `status`, `block_count`, `script_file`

**1.2 - Agent Vidéo Veo 3.1 (NOUVEAU)**
- [ ] Créer dossier `agent-video-veo31/`
- [ ] Implémenter extraction des blocs depuis le script
- [ ] Implémenter génération vidéo initiale (8s) avec Veo 3.1 API
- [ ] Implémenter extensions successives (7s × N blocs)
- [ ] Gérer polling des opérations asynchrones Veo
- [ ] Télécharger et uploader vidéo finale vers GCS (`veo31_videos/`)
- [ ] Mettre à jour Firestore :  `status = 'video_generated'`, `veo31_video_uri`
- [ ] Créer Dockerfile + requirements.txt
- [ ] Tester avec script de 4-6 blocs

**1.3 - Agent Assembleur (Modification)**
- [ ] Modifier pour télécharger 1 vidéo Veo 3.1 (au lieu de 8 clips)
- [ ] Implémenter extraction audio de la vidéo Veo avec FFmpeg
- [ ] Garder génération sous-titres Whisper (inchangée)
- [ ] Incruster sous-titres dans vidéo Veo
- [ ] Tester assemblage complet
- [ ] Mettre à jour Firestore : `status = 'completed'`, `final_video_url`

**1.4 - Monitoring (Modification)**
- [ ] Modifier pour surveiller `status = 'video_generated'` au lieu de clips individuels
- [ ] Appeler assembleur quand vidéo Veo 3.1 prête
- [ ] Tester déclenchement automatique

**1.5 - Déploiement Infrastructure**
- [ ] Créer script `deploy-veo31.sh`
- [ ] Configurer variables d'environnement (GEMINI_API_KEY)
- [ ] Déployer 4 Cloud Functions (script, video-veo31, assembler, monitor)
- [ ] Configurer Cloud Scheduler (2 min)
- [ ] Tester pipeline end-to-end

**1.6 - Tests et Validation**
- [ ] Tester avec 5 thèmes différents
- [ ] Vérifier durées vidéos (60-90s)
- [ ] Vérifier synchronisation audio/vidéo
- [ ] Vérifier qualité sous-titres
- [ ] Mesurer temps de génération (baseline)
- [ ] Mesurer coûts par vidéo (baseline)

**Livrables Phase 1**
- ✅ Pipeline Veo 3.1 fonctionnel (thème → vidéo 60-90s)
- ✅ Documentation technique
- ✅ Métriques de performance (temps, coûts)

---

### **PHASE 2 :  SYSTÈME DE PERSONNAGES**
**Durée estimée :  2-3 semaines**  
**Priorité : HAUTE**

#### Objectif
Permettre création et réutilisation de personnages récurrents (Nano Banana)

#### Tâches

**2.1 - Backend - API Characters**
- [ ] Créer modèle Pydantic `CharacterCreateRequest` :  name, description, style
- [ ] Créer router `backend/app/routers/characters.py`
- [ ] Endpoint `POST /characters/create` : génère image avec Nano Banana (Gemini 2.5 Flash Image)
- [ ] Sauvegarder image dans GCS (`characters/{character_id}. png`)
- [ ] Créer document Firestore `characters/{character_id}` : name, description, reference_image_uri, created_by
- [ ] Endpoint `GET /characters/list` : liste personnages de l'utilisateur
- [ ] Endpoint `GET /characters/{id}` : détails d'un personnage
- [ ] Endpoint `DELETE /characters/{id}` : supprimer personnage
- [ ] Protéger endpoints avec JWT
- [ ] Tests unitaires

**2.2 - Agent Script (Modification)**
- [ ] Ajouter paramètre optionnel `character_id` dans requête HTTP
- [ ] Si `character_id` fourni, récupérer depuis Firestore
- [ ] Inclure description personnage dans prompt Gemini
- [ ] Format : "PERSONNAGE PRINCIPAL : {name} - {description}"
- [ ] Tester génération scripts avec/sans personnage

**2.3 - Agent Vidéo Veo 3.1 (Modification)**
- [ ] Extraire `character_id` depuis nom fichier script ou Firestore
- [ ] Récupérer `reference_image_uri` depuis Firestore
- [ ] Télécharger image de référence depuis GCS
- [ ] Convertir en objet `Image` compatible Veo API
- [ ] Créer `VideoGenerationReferenceImage` avec `reference_type="asset"`
- [ ] Passer `reference_images` dans config Veo (bloc initial + extensions)
- [ ] Tester cohérence personnage sur 60-90s

**2.4 - Frontend - Interface Characters**
- [ ] Créer page `src/pages/Characters.jsx`
- [ ] Formulaire création personnage :  nom, description, style
- [ ] Galerie personnages (cards avec image, nom, description)
- [ ] Bouton "Créer vidéo" pour chaque personnage
- [ ] Intégration avec page CreateVideo :  sélecteur personnage (optionnel)
- [ ] Gestion états :  loading, erreurs, succès
- [ ] Tests UI

**2.5 - Frontend - Modification CreateVideo**
- [ ] Ajouter dropdown "Personnage" (optionnel) :  "Aucun" + liste personnages
- [ ] Si personnage sélectionné, envoyer `character_id` à l'API
- [ ] Afficher preview image du personnage
- [ ] Tests intégration

**2.6 - Tests End-to-End**
- [ ] Créer personnage "Nano Banana"
- [ ] Générer 3 vidéos différentes avec Nano Banana
- [ ] Vérifier cohérence visuelle
- [ ] Générer 1 vidéo sans personnage
- [ ] Comparer qualité

**Livrables Phase 2**
- ✅ Système personnages opérationnel
- ✅ Interface utilisateur complète
- ✅ 5+ personnages de test créés

---

### **PHASE 3 : TEMPS RÉEL & UX** 
**Durée estimée : 1-2 semaines**  
**Priorité : HAUTE**

#### Objectif
Améliorer l'expérience utilisateur avec WebSocket, thumbnails, durées

#### Tâches

**3.1 - WebSocket Temps Réel**
- [ ] Backend :  ajouter `python-socketio` et `websockets` aux requirements
- [ ] Créer `backend/app/routers/websocket.py`
- [ ] Implémenter `ConnectionManager` : gestion connexions actives
- [ ] Endpoint `WS /ws/video/{video_id}? token={jwt}` : authentification JWT
- [ ] Créer Firestore watcher (`onSnapshot`) sur `video_status/{video_id}`
- [ ] Broadcaster changements à tous clients connectés
- [ ] Gérer déconnexions et erreurs
- [ ] Frontend : créer hook `useVideoWebSocket(videoId, token)`
- [ ] Modifier `CreateVideo. jsx` : barre progression temps réel
- [ ] Afficher :  status, completed_blocks, total_blocks, progression %
- [ ] Tests :  simuler génération avec mises à jour live

**3.2 - Génération Thumbnails**
- [ ] Agent Assembleur : après upload final, extraire frame à 2s avec FFmpeg
- [ ] Redimensionner en 540×960 (9:16)
- [ ] Uploader vers GCS (`thumbnails/{video_id}.jpg`)
- [ ] Mettre à jour Firestore : `thumbnail_url`
- [ ] Backend Storage Service : méthode `_get_thumbnail_url(video_id)`
- [ ] Inclure `thumbnail_url` dans réponse `list_videos()`
- [ ] Frontend : afficher thumbnails dans galerie vidéos
- [ ] Tests : vérifier génération pour 5 vidéos

**3.3 - Extraction Durée Vidéo**
- [ ] Agent Assembleur : après upload final, exécuter `ffprobe` pour durée
- [ ] Parser JSON output pour extraire `format. duration`
- [ ] Mettre à jour Firestore : `duration` (en secondes)
- [ ] Backend Storage Service : récupérer durée depuis Firestore
- [ ] Frontend : formatter et afficher durée (ex: "1m 24s")
- [ ] Tests : vérifier durées correctes

**3.4 - Cache Whisper Model**
- [ ] Modifier `agent-assembler/Dockerfile`
- [ ] Pré-télécharger modèle Whisper "base" dans `/tmp/. cache/whisper`
- [ ] Configurer `ENV XDG_CACHE_HOME=/tmp/.cache`
- [ ] Modifier `main.py` pour pointer vers cache
- [ ] Mesurer temps cold start avant/après
- [ ] Objectif : réduire de 30s à <5s

**Livrables Phase 3**
- ✅ WebSocket fonctionnel (progression live)
- ✅ Thumbnails générés automatiquement
- ✅ Durées vidéos affichées
- ✅ Cold start Whisper optimisé

---

### **PHASE 4 : PERSONNALISATION & STYLES**
**Durée estimée : 2 semaines**  
**Priorité : MOYENNE**

#### Objectif
Offrir choix de styles visuels, voix, et langues

#### Tâches

**4.1 - Templates de Style Visuel**
- [ ] Agent Script : définir dictionnaire `VISUAL_STYLES` (7 styles)
- [ ] Styles :  cinematic, anime, realistic, sketch, cyberpunk, vintage, fantasy
- [ ] Ajouter paramètre `style` dans requête HTTP
- [ ] Inclure style dans prompt Gemini pour chaque bloc
- [ ] Nom fichier : `script_{theme}_{style}.txt`
- [ ] Backend : ajouter `style` dans `VideoCreateRequest`
- [ ] Validation : style doit être dans liste autorisée
- [ ] Frontend : créer sélecteur de style (grid avec previews)
- [ ] Tests : générer 1 vidéo par style (7 vidéos)

**4.2 - Choix de Voix (Optionnel - si TTS utilisé)**
- [ ] Définir dictionnaire `FRENCH_VOICES` (Rasalgethi, Sabik, Wavenet A-D)
- [ ] Frontend : dropdown choix de voix
- [ ] Backend : passer `voice` à agent audio (si implémenté)
- [ ] Tests : comparer qualité des voix

**4.3 - Multi-langues**
- [ ] Agent Script : ajouter paramètre `language` (fr, en, es)
- [ ] Adapter prompt Gemini selon langue
- [ ] Modifier instructions :  "Generate in English", "Genera en español"
- [ ] Backend : ajouter `language` dans `VideoCreateRequest`
- [ ] Frontend : sélecteur de langue (drapeaux)
- [ ] Tests : générer vidéo en EN et ES

**Livrables Phase 4**
- ✅ 7 styles visuels disponibles
- ✅ 3 langues supportées (FR, EN, ES)
- ✅ Interface choix style/langue fluide

---

### **PHASE 5 : MUSIQUE & AUDIO**
**Durée estimée : 1 semaine**  
**Priorité : MOYENNE**

#### Objectif
Ajouter musique de fond optionnelle

#### Tâches

**5.1 - Bibliothèque Musiques**
- [ ] Télécharger 5-10 musiques libres de droits (YouTube Audio Library, Pixabay)
- [ ] Catégories : lofi, upbeat, ambient, epic, calm
- [ ] Uploader vers GCS (`music/*. mp3`)
- [ ] Créer collection Firestore `music_tracks` :  name, category, gcs_uri, duration
- [ ] Backend : endpoint `GET /music/list` : liste musiques disponibles

**5.2 - Agent Assembleur (Modification)**
- [ ] Ajouter paramètre `music` dans requête HTTP
- [ ] Si `music != 'none'`, télécharger piste depuis GCS
- [ ] FFmpeg : mixer audio Veo + musique (musique à 20% volume)
- [ ] Utiliser `aloop` pour boucler musique si trop courte
- [ ] Filter : `[music]volume=0.2[m];[audio][m]amix=inputs=2`
- [ ] Tests : comparer avec/sans musique

**5.3 - Frontend**
- [ ] Ajouter dropdown "Musique de fond" dans CreateVideo
- [ ] Options : "Aucune", "Lofi Chill", "Upbeat Energy", "Ambient Calm"
- [ ] Envoyer `music` à l'API
- [ ] Tests UI

**Livrables Phase 5**
- ✅ 5+ musiques disponibles
- ✅ Mixage audio fonctionnel
- ✅ Choix musique dans interface

---

### **PHASE 6 : HISTORIQUE & FAVORIS**
**Durée estimée : 1 semaine**  
**Priorité :  MOYENNE**

#### Objectif
Permettre aux utilisateurs d'organiser leurs vidéos

#### Tâches

**6.1 - Backend - Système Favoris**
- [ ] Créer collection `users/{user_id}/videos` dans Firestore
- [ ] Champs : video_id, theme, created_at, is_favorite, views, character_id
- [ ] Endpoint `POST /videos/{id}/favorite` : marquer favori
- [ ] Endpoint `DELETE /videos/{id}/favorite` : retirer favori
- [ ] Endpoint `GET /videos/my-videos` : vidéos de l'utilisateur (filtre par created_by)
- [ ] Endpoint `GET /videos/favorites` : seulement favoris
- [ ] Tests API

**6.2 - Frontend - Interface Historique**
- [ ] Modifier `MyVideos.jsx` : onglets "Toutes" / "Favoris"
- [ ] Ajouter bouton ⭐ sur chaque card vidéo
- [ ] État : is_favorite (toggle)
- [ ] Tri : par date, par vues, par durée
- [ ] Filtres : par personnage, par style, par langue
- [ ] Tests UI

**6.3 - Analytics Basiques**
- [ ] Incrémenter compteur `views` lors du visionnage
- [ ] Endpoint `POST /videos/{id}/view` : incrémenter
- [ ] Afficher nombre de vues sur card
- [ ] Tests

**Livrables Phase 6**
- ✅ Système favoris opérationnel
- ✅ Historique personnel par utilisateur
- ✅ Tri et filtres avancés

---

### **PHASE 7 : OPTIMISATIONS PERFORMANCE**
**Durée estimée : 1-2 semaines**  
**Priorité : HAUTE**

#### Objectif
Réduire temps génération, coûts, et améliorer fiabilité

#### Tâches

**7.1 - Retry Intelligent avec Backoff**
- [ ] Modifier Monitor : implémenter fonction `should_retry_clip()`
- [ ] Backoff exponentiel : 1min, 3min, 10min
- [ ] Stocker `last_retry_at` dans Firestore
- [ ] Max 3 tentatives avant abandon
- [ ] Tests : simuler échecs Veo

**7.2 - Compression Vidéo Adaptative**
- [ ] Agent Assembleur : après incrustation sous-titres, compresser avec FFmpeg
- [ ] Paramètres : `-c:v libx264 -preset fast -crf 23`
- [ ] Audio : `-c:a aac -b:a 128k`
- [ ] Ajouter `-movflags +faststart` pour streaming optimisé
- [ ] Mesurer tailles avant/après (objectif :  200MB → 40MB)
- [ ] Tests : vérifier qualité visuelle acceptable

**7.3 - Cloud CDN pour Streaming**
- [ ] Créer backend bucket :  `gcloud compute backend-buckets create`
- [ ] Activer Cloud CDN sur le bucket GCS
- [ ] Configurer cache TTL (1 jour)
- [ ] Modifier Storage Service : utiliser URLs CDN au lieu de GCS direct
- [ ] Tests : mesurer latence streaming (sans/avec CDN)

**7.4 - Logs Structurés**
- [ ] Ajouter `structlog` aux requirements (tous agents)
- [ ] Remplacer `print()` par `logger.info()`, `logger.error()`
- [ ] Format JSON : `{"event": "clip_generated", "video_id": ".. .", "duration": 8}`
- [ ] Intégrer avec Cloud Logging
- [ ] Créer dashboards dans Cloud Monitoring
- [ ] Métriques : temps génération, taux succès, coûts

**7.5 - Cache Gemini Responses**
- [ ] Créer collection Firestore `script_cache`
- [ ] Hash du thème :  `hashlib.md5(theme.encode()).hexdigest()`
- [ ] Avant génération, vérifier si script existe en cache
- [ ] Stocker :  theme_hash, script_content, created_at
- [ ] TTL : 7 jours
- [ ] Tests : mesurer réduction coûts API

**Livrables Phase 7**
- ✅ Retry intelligent déployé
- ✅ Vidéos compressées (5x plus légères)
- ✅ CDN activé (streaming rapide)
- ✅ Logs structurés avec dashboards
- ✅ Cache Gemini opérationnel

---

### **PHASE 8 : TESTS & QUALITÉ**
**Durée estimée : 1 semaine**  
**Priorité : HAUTE**

#### Objectif
Garantir fiabilité et qualité du système

#### Tâches

**8.1 - Tests Automatisés Backend**
- [ ] Créer `backend/tests/`
- [ ] Tests unitaires : `test_auth.py`, `test_characters.py`, `test_videos.py`
- [ ] Tests intégration : pipeline complet (mock Veo API)
- [ ] Coverage : objectif >80%
- [ ] Configurer pytest + pytest-cov

**8.2 - Tests Automatisés Agents**
- [ ] Tests `agent-script` : vérifier format BLOCS
- [ ] Tests `agent-video-veo31` : extraction blocs, gestion erreurs
- [ ] Tests `agent-assembler` : FFmpeg, Whisper
- [ ] Mocks pour APIs externes (Gemini, Veo)

**8.3 - CI/CD GitHub Actions**
- [ ] Créer `.github/workflows/test.yml`
- [ ] Workflow : install deps → run tests → coverage report
- [ ] Déclencher sur push/PR
- [ ] Badge coverage dans README

**8.4 - Tests End-to-End**
- [ ] Scénario 1 : Vidéo simple (thème uniquement)
- [ ] Scénario 2 : Vidéo avec personnage
- [ ] Scénario 3 : Vidéo avec style + musique + langue
- [ ] Scénario 4 : Gestion erreurs (quota dépassé, Veo timeout)
- [ ] Scénario 5 : Retry automatique après échec

**8.5 - Documentation**
- [ ] README principal : architecture, installation, usage
- [ ] Guides utilisateur : créer personnage, générer vidéo
- [ ] Documentation API :  Swagger/OpenAPI
- [ ] Guides admin : déploiement, monitoring, troubleshooting
- [ ] Diagrammes architecture (Mermaid)

**Livrables Phase 8**
- ✅ Suite tests complète (>80% coverage)
- ✅ CI/CD fonctionnel
- ✅ Documentation exhaustive

---

### **PHASE 9 : ALERTES & MONITORING**
**Durée estimée : 3-4 jours**  
**Priorité : MOYENNE**

#### Objectif
Surveiller coûts, performances, et erreurs

#### Tâches

**9.1 - Alertes Budget GCP**
- [ ] Créer budget GCP : $100/mois
- [ ] Seuils d'alerte : 50%, 75%, 90%, 100%
- [ ] Notifications : email admin + Slack (optionnel)
- [ ] Tests : vérifier réception alertes

**9.2 - Dashboards Cloud Monitoring**
- [ ] Dashboard "Génération Vidéos" : 
  - Nombre vidéos générées / jour
  - Temps moyen génération
  - Taux succès/échec
  - Coût par vidéo
- [ ] Dashboard "Performances" :
  - Latence API backend
  - Cold starts Cloud Functions
  - Taille vidéos finales
- [ ] Alertes : échec >10% sur 1h, latence >30s

**9.3 - Error Tracking (Optionnel)**
- [ ] Intégrer Sentry ou Google Error Reporting
- [ ] Capturer exceptions non gérées
- [ ] Alertes erreurs critiques
- [ ] Tests : déclencher erreur volontaire

**Livrables Phase 9**
- ✅ Alertes budget configurées
- ✅ 2 dashboards Cloud Monitoring
- ✅ Error tracking opérationnel

---

### **PHASE 10 : POLISH & DÉPLOIEMENT PRODUCTION**
**Durée estimée : 1 semaine**  
**Priorité : CRITIQUE**

#### Objectif
Finaliser et déployer en production

#### Tâches

**10.1 - Sécurité**
- [ ] Changer `JWT_SECRET_KEY` en production (variable d'env)
- [ ] Activer HTTPS uniquement
- [ ] Configurer CORS restrictif (domaines autorisés)
- [ ] Rate limiting sur endpoints critiques (créer vidéo, créer personnage)
- [ ] Audit sécurité : scanner vulnérabilités (Snyk, Dependabot)

**10.2 - Performance Frontend**
- [ ] Lazy loading des composants (React. lazy)
- [ ] Optimisation images (WebP, compression)
- [ ] Bundle size analysis (Vite build analyzer)
- [ ] Service Worker pour cache (PWA optionnel)
- [ ] Lighthouse score : objectif >90

**10.3 - Environnements**
- [ ] Séparer dev / staging / production
- [ ] Variables d'env par environnement
- [ ] GCS buckets séparés
- [ ] Firestore databases séparés (ou namespaces)

**10.4 - Déploiement Production**
- [ ] Déployer backend sur Cloud Run (scaling auto)
- [ ] Déployer frontend sur Cloud Run (Nginx)
- [ ] Configurer domaine personnalisé + SSL
- [ ] Tester pipeline complet en prod
- [ ] Rollback plan

**10.5 - Onboarding Utilisateurs**
- [ ] Page d'accueil : présentation produit
- [ ] Tutoriel intégré : première vidéo guidée
- [ ] FAQ / Help Center
- [ ] Vidéo démo (ex: "Comment créer Nano Banana")

**Livrables Phase 10**
- ✅ Application en production
- ✅ Domaine configuré + SSL
- ✅ Onboarding utilisateurs
- ✅ Documentation déploiement

---

## 📊 RÉSUMÉ DES 17 AMÉLIORATIONS

| # | Amélioration | Phase | Priorité | Durée |
|---|--------------|-------|----------|-------|
| 1 | WebSocket temps réel | 3 | Haute | 3j |
| 2 | Thumbnails | 3 | Haute | 2j |
| 3 | Durée vidéo | 3 | Haute | 1j |
| 4 | Cache Whisper | 3 | Haute | 1j |
| 5 | Retry backoff | 7 | Haute | 2j |
| 6 | Templates style | 4 | Moyenne | 3j |
| 7 | Musique fond | 5 | Moyenne | 3j |
| 8 | Historique favoris | 6 | Moyenne | 4j |
| 9 | Choix voix | 4 | Basse | 2j |
| 10 | Multi-langues | 4 | Moyenne | 3j |
| 11 | Batch Veo priorité | 7 | Basse | 2j |
| 12 | Compression vidéo | 7 | Haute | 2j |
| 13 | Cloud CDN | 7 | Haute | 2j |
| 14 | Logs structurés | 7 | Haute | 2j |
| 15 | Tests automatisés | 8 | Haute | 5j |
| 16 | Alertes budget | 9 | Moyenne | 1j |
| 17 | Cache Gemini | 7 | Moyenne | 2j |

**Total estimé : 8-10 semaines (2-2.5 mois)**

---

## 🎯 JALONS CLÉS

### Jalon 1 : MVP Veo 3.1 (Fin Phase 1)
- ✅ Pipeline Veo 3.1 fonctionnel (thème → vidéo 60-90s)
- ✅ Audio natif synchronisé
- ✅ Sous-titres Whisper

### Jalon 2 :  Personnages (Fin Phase 2)
- ✅ Création personnages avec Nano Banana
- ✅ Génération vidéos avec personnages récurrents
- ✅ Interface complète

### Jalon 3 :  UX Optimisée (Fin Phase 3)
- ✅ WebSocket progression live
- ✅ Thumbnails + durées
- ✅ Performance améliorée

### Jalon 4 : Personnalisation (Fin Phase 5)
- ✅ 7 styles + 3 langues
- ✅ Musique de fond
- ✅ Historique favoris

### Jalon 5 : Production Ready (Fin Phase 10)
- ✅ Tests complets (>80% coverage)
- ✅ Monitoring + alertes
- ✅ Déployé en production
- ✅ Documentation complète

---

## 📈 MÉTRIQUES DE SUCCÈS

### Qualité
- [ ] Taux de réussite génération vidéo :  >95%
- [ ] Synchronisation audio parfaite :  100%
- [ ] Note utilisateurs : >4.5/5

### Performance
- [ ] Temps génération vidéo : <30 min
- [ ] Temps chargement page : <2s
- [ ] Uptime : >99.5%

### Coûts
- [ ] Coût par vidéo : <$2. 00
- [ ] Budget mensuel : <$100 (phase test)

### Adoption
- [ ] 50+ vidéos générées (test)
- [ ] 10+ personnages créés
- [ ] 5+ utilisateurs actifs

---

## 🚀 STRATÉGIE DE DÉPLOIEMENT

### Approche Incrémentale
1. **Phase 1-2** : Dev local + staging
2. **Phase 3-6** : Staging avancé + bêta testeurs
3. **Phase 7-9** : Optimisation + monitoring
4. **Phase 10** : Production publique

### Rollback Plan
- Garder ancien système (8 clips) en parallèle (1 mois)
- Feature flags pour activer/désactiver Veo 3.1
- Backups quotidiens Firestore
- Scripts de rollback automatisés

---