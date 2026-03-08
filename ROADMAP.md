# 🗺️ ROADMAP REETIK - Évolutions & Tâches Restantes

**Dernière mise à jour** : 7 Mars 2026  
**Status** : Application déployée en production ✅  
**URL Production** : https://portfolio-prod-portfolio-app-588105049123.us-west1.run.app

---

## ✅ CE QUI EST FAIT (V2.1 - Déployé)

### Infrastructure & Déploiement
- ✅ **Cloud Run** : Backend FastAPI + Frontend React déployés
- ✅ **Terraform** : Infrastructure as Code complète
- ✅ **CI/CD** : GitHub Actions avec Workload Identity Federation
- ✅ **Artifact Registry** : Images Docker avec rétention 5 versions
- ✅ **CORS Cloud Storage** : Configuration pour lecture vidéos

### Fonctionnalités Core
- ✅ **Interface Web** : React + TypeScript + Vite + TailwindCSS
- ✅ **Authentification JWT** : Tokens 7 jours avec refresh
- ✅ **Code d'accès rotatif** : Change toutes les heures (Cloud Scheduler)
- ✅ **Système de quotas** : 2 vidéos/utilisateur, illimité pour admins
- ✅ **WebSocket temps réel** : Suivi progression vidéos
- ✅ **Firestore** : Utilisateurs, vidéos, quotas
- ✅ **Cloud Functions** : 4 agents (Script, Audio, Vidéo, Assembleur)
- ✅ **Système de retry** : Réessai automatique clips échoués
- ✅ **Veo 3.1** : Génération vidéo HD 1080p (8 clips x 8s)

### DevOps
- ✅ **Docker Compose** : Environnement local complet
- ✅ **Documentation** : Structure organisée (deployment/, architecture/, plans/)
- ✅ **Scripts** : Déploiement et build automatisés

---

## 🔄 TÂCHES IMMÉDIATES (Sprint Actuel)

### 1. ⚠️ Monitoring & Observabilité (PRIORITÉ HAUTE)

#### 1.1 Cloud Monitoring Dashboards
**Objectif** : Visualiser métriques en temps réel

**Tâches** :
- [ ] Créer dashboard Cloud Run (requêtes, latence, erreurs, CPU, mémoire)
- [ ] Créer dashboard Cloud Functions (invocations, durées, erreurs, cold starts)
- [ ] Créer dashboard Firestore (lectures, écritures, quota)
- [ ] Créer dashboard Cloud Storage (téléchargements, bande passante)
- [ ] Créer dashboard coûts (estimations par service)

**Fichiers à créer** :
```
terraform/monitoring.tf         # Dashboards as code
terraform/alerts.tf             # Policies d'alertes
```

#### 1.2 Alertes Automatisées
**Objectif** : Être notifié des problèmes avant les utilisateurs

**Tâches** :
- [ ] Alerte : Erreur rate > 5% (Cloud Run/Functions)
- [ ] Alerte : Latence P95 > 5s (Backend API)
- [ ] Alerte : Coûts journaliers > $50
- [ ] Alerte : Quota Firestore > 80%
- [ ] Alerte : Échec génération vidéo > 3 fois consécutives
- [ ] Notification : Slack/Email via Cloud Pub/Sub

#### 1.3 Structured Logging
**Objectif** : Logs exploitables et recherchables

**Tâches** :
- [ ] Uniformiser format logs JSON (backend + functions)
- [ ] Ajouter trace_id pour suivre requêtes end-to-end
- [ ] Logs de sécurité : tentatives auth échouées, quota dépassé
- [ ] Logs de business : vidéos créées, durées génération, erreurs Veo/Gemini
- [ ] Créer requêtes Log Explorer sauvegardées (top erreurs, slow queries)

**Estimation** : 1-2 semaines  
**Impact** : Critique pour opérations production


### 2. 🧪 Tests Automatisés (PRIORITÉ HAUTE)

#### 2.1 Tests Backend
- [ ] Tests API endpoints (pytest + FastAPI TestClient)
  - Auth (login, register, quota)
  - Vidéos CRUD
  - Validation inputs
- [ ] Tests d'intégration Firestore (émulateur)
- [ ] Tests Cloud Storage (mock)
- [ ] CI : Exécution automatique sur PR

#### 2.2 Tests Frontend
- [ ] Tests composants React (Vitest + React Testing Library)
- [ ] Tests E2E Playwright (flow complet création vidéo)
- [ ] Tests WebSocket (connexion, déconnexion, messages)

**Estimation** : 2-3 semaines  
**Impact** : Haute (réduction bugs production)


### 3. 🎨 Améliorations UX/UI (PRIORITÉ MOYENNE)

#### 3.1 Interface Utilisateur
- [ ] Dashboard analytics personnel (vidéos créées, temps moyen)
- [ ] Galerie vidéos avec preview thumbnails
- [ ] Filtres/recherche dans historique vidéos
- [ ] Partage vidéos via liens publics
- [ ] Mode sombre/clair

#### 3.2 Expérience Création
- [ ] Suggestions thèmes populaires
- [ ] Preview script avant génération vidéo
- [ ] Estimation temps/coût avant création
- [ ] Système de favoris vidéos
- [ ] Export vidéo en différents formats (9:16, 16:9, 1:1)

**Estimation** : 3-4 semaines  
**Impact** : Moyenne (améliore rétention utilisateurs)

---

## 🚀 ÉVOLUTIONS MAJEURES (Roadmap Long Terme)

### PHASE 1 : Migration Veo 3.1 Audio Natif (2-3 mois)

**Révolution** : Veo 3.1 génère **audio + vidéo ensemble** !

#### Avantages
- ✅ **Audio natif** : Dialogues et effets sonores générés par Veo
- ✅ **Synchro parfaite** : Plus de décalage audio/vidéo
- ✅ **Vidéos fluides** : 1 vidéo continue (vs 8 clips assemblés)
- ✅ **Extensions** : 8s initiaux + extensions 7s (jusqu'à 141s)
- ✅ **Coût réduit** : Moins d'appels API (Google TTS supprimé)

#### Tâches Principales
1. **Nouveau Format Script** (Gemini prompt)
   - [ ] Script avec "BLOCS" narratifs au lieu de "SCÈNES"
   - [ ] Chaque bloc inclut : VISUEL + DIALOGUE + EFFETS SONORES
   - [ ] Validation : minimum 4 blocs (60-90s vidéo finale)

2. **Agent Vidéo Veo 3.1** (Réécriture complète)
   - [ ] Génération vidéo initiale 8s avec audio natif
   - [ ] Extensions successives 7s par bloc
   - [ ] Polling opérations asynchrones Veo
   - [ ] Gestion erreurs et retry

3. **Agent Assembleur** (Simplification)
   - [ ] Télécharger 1 vidéo Veo (au lieu de 8 clips)
   - [ ] Extraire audio de la vidéo Veo (FFmpeg)
   - [ ] Générer sous-titres Whisper (inchangé)
   - [ ] Incruster sous-titres sur vidéo finale

4. **Monitoring** (Adaptation)
   - [ ] Suivre statut extensions Veo
   - [ ] Gérer timeouts longs (génération jusqu'à 10 min)

**Livrables** :
- Pipeline Veo 3.1 avec audio natif fonctionnel
- Vidéos 60-141s fluides (vs 64-80s assemblées)
- Documentation technique migration
- Métriques performance (temps, coûts, qualité)

**Estimation** : 2-3 mois  
**Impact** : TRÈS HAUTE (game changer qualité)


### PHASE 2 : Système de Personnages Récurrents (1-2 mois)

**Objectif** : Créer et réutiliser personnages (ex: Nano Banana)

#### Fonctionnalités
- [ ] **Création personnage** : Interface utilisateur
- [ ] **Génération image référence** : Gemini 2.5 Flash Image (Imagen 3)
- [ ] **Stockage** : GCS + Firestore (`characters` collection)
- [ ] **Réutilisation** : Inject image référence dans prompts Veo 3.1
- [ ] **Cohérence visuelle** : Même personnage dans toutes vidéos

#### API Endpoints
```python
POST /characters/create     # Créer personnage
GET /characters/list        # Lister mes personnages
GET /characters/{id}        # Détails personnage
POST /videos/create         # + character_id optionnel
```

**Estimation** : 1-2 mois  
**Impact** : HAUTE (storytelling récurrent)


### PHASE 3 : Templates & Styles Visuels (1 mois)

**Objectif** : 7 styles prédéfinis pour vidéos

#### Styles
1. **Photorealistic** : Hyper-réaliste (défaut actuel)
2. **Cartoon** : Style animation BD
3. **Anime** : Style manga/anime japonais
4. **Cinematic** : Hollywood, dramatique
5. **Vintage** : Années 70-80, grain film
6. **Futuristic** : Cyberpunk, néon
7. **Documentary** : Style reportage BBC

#### Implémentation
- [ ] Créer templates prompts Veo par style
- [ ] UI : Sélecteur style avant création
- [ ] Stockage : `video.style` dans Firestore
- [ ] Preview exemples par style

**Estimation** : 1 mois  
**Impact** : MOYENNE (diversification contenu)


### PHASE 4 : Multi-langues (2-3 semaines)

**Objectif** : Scripts en FR, EN, ES, DE, IT

#### Tâches
- [ ] Frontend : Sélecteur langue avant création
- [ ] Agent Script : Paramètre langue dans prompt Gemini
- [ ] Agent Audio : Voix TTS adaptée (ou Veo 3.1 avec accent)
- [ ] Sous-titres Whisper : Detection auto langue

**Estimation** : 2-3 semaines  
**Impact** : HAUTE (marché international)


### PHASE 5 : Musique de Fond (2 semaines)

**Objectif** : Ajouter musique libre de droits

#### Tâches
- [ ] Intégration bibliothèque musique (YouTube Audio Library, Epidemic Sound API)
- [ ] Détection genre vidéo (Gemini) → musique adaptée
- [ ] Mixage audio : Voix + Musique (FFmpeg volume ducking)
- [ ] UI : Option activer/désactiver musique

**Estimation** : 2 semaines  
**Impact** : MOYENNE (engagement +20%)


### PHASE 6 : Publication Automatique (1 mois)

**Objectif** : Upload auto TikTok/YouTube Shorts

#### Tâches
- [ ] Intégration TikTok Business API
- [ ] Intégration YouTube Data API v3
- [ ] Authentification OAuth2 utilisateur
- [ ] UI : Connexion comptes sociaux
- [ ] Post-processing : Hashtags auto (Gemini)
- [ ] Scheduling : Publication différée

**Estimation** : 1 mois  
**Impact** : TRÈS HAUTE (workflow complet)


### PHASE 7 : Analytics Avancés (2-3 semaines)

**Objectif** : Métriques business et engagement

#### Métriques
- [ ] Dashboard admin : Vidéos totales, utilisateurs actifs, coûts
- [ ] Temps moyen génération par étape
- [ ] Taux succès/échec par agent
- [ ] Top thèmes populaires
- [ ] Engagement vidéos (si publication auto activée)
- [ ] A/B testing styles/durées

**Estimation** : 2-3 semaines  
**Impact** : MOYENNE (insights business)


### PHASE 8 : Optimisation Coûts (Ongoing)

**Objectif** : Réduire coût/vidéo de $6.58 à $4-5

#### Optimisations
- [ ] Cache responses Gemini (thèmes similaires)
- [ ] Réduction durée clips : 6s au lieu de 8s
- [ ] Batch processing vidéos (reduce cold starts)
- [ ] Compression vidéos output (maintain quality)
- [ ] Utilisation Spot instances pour Cloud Functions (si disponible)
- [ ] Auto-scaling intelligent (prédiction demande)

**Estimation** : Ongoing  
**Impact** : HAUTE (rentabilité)


### PHASE 9 : Monétisation (1-2 mois)

**Objectif** : Système de paiement et crédits

#### Fonctionnalités
- [ ] Plans : Free (2 vidéos), Pro ($9.99/mois, 20 vidéos), Business ($49.99/mois, illimité)
- [ ] Intégration Stripe Checkout
- [ ] Système de crédits (1 crédit = 1 vidéo)
- [ ] Achat crédits à l'unité ($3.99/vidéo)
- [ ] Facturation mensuelle automatique
- [ ] Dashboard facturation utilisateur

**Estimation** : 1-2 mois  
**Impact** : CRITIQUE (générer revenus)

---

## 📊 PRIORISATION GLOBALE

### Court Terme (0-3 mois)
**Focus : Stabilité & Qualité**
1. 🔴 **Monitoring & Alertes** (critique)
2. 🔴 **Tests Automatisés** (critique)
3. 🟡 **Améliorations UX/UI** (important)
4. 🟡 **Migration Veo 3.1 Audio Natif** (game changer)

### Moyen Terme (3-6 mois)
**Focus : Différenciation**
1. 🔵 **Personnages Récurrents**
2. 🔵 **Templates Styles Visuels**
3. 🔵 **Multi-langues**
4. 🔵 **Musique de Fond**

### Long Terme (6-12 mois)
**Focus : Croissance & Revenus**
1. 🟢 **Publication Automatique TikTok/YouTube**
2. 🟢 **Analytics Avancés**
3. 🟢 **Monétisation (Stripe)**
4. 🟢 **Optimisation Coûts Continue**

---

## 🎯 MÉTRIQUES DE SUCCÈS

### Performance
- ⏱️ Temps génération vidéo : **< 8 minutes** (actuel: ~6-10 min)
- 💰 Coût par vidéo : **< $5** (actuel: $6.58)
- ✅ Taux succès génération : **> 95%** (actuel: ~85%)
- 🚀 Latence API : **< 200ms P95** (actuel: non mesuré)

### Business
- 👥 Utilisateurs actifs mensuels : **> 100** (Q2 2026)
- 🎬 Vidéos générées/mois : **> 500** (Q2 2026)
- 💵 Revenus mensuels : **> $1,000** (Q3 2026)
- ⭐ Satisfaction utilisateurs (NPS) : **> 50**

### Technique
- 🐛 Bug rate : **< 1% des vidéos**
- 📊 Code coverage tests : **> 80%**
- 🔒 Taux incidents sécurité : **0**
- ⏰ Uptime : **> 99.5%**

---

## 📝 NOTES & DÉCISIONS

### Choix Techniques En Attente
- [ ] **Veo 3.1 vs Veo 3.0** : Attendre stabilité API Veo 3.1 avant migration complète
- [ ] **Firestore vs PostgreSQL** : Évaluer migration si > 10k utilisateurs
- [ ] **Cloud Run vs GKE** : Rester Cloud Run tant que < 1M req/jour
- [ ] **Gemini vs GPT-4** : Benchmark qualité scripts avant changement

### Risques Identifiés
⚠️ **Coûts Veo** : Prix Veo 3.1 peut augmenter (~$0.80/clip actuellement)  
⚠️ **Quotas GCP** : Surveiller quotas Vertex AI (100 req/min)  
⚠️ **Dépendance API** : Veo/Gemini = single point of failure  
⚠️ **Concurrence** : Nouveaux acteurs IA vidéo (Runway, Pika)

### Opportunités
💡 **Partenariats** : TikTok Creator Fund, YouTube Shorts Fund  
💡 **Niches** : Focus éducation, e-commerce, actualités  
💡 **API B2B** : Licence API pour agences marketing  
💡 **White Label** : Version brandée pour entreprises

---

**Dernière révision** : 7 Mars 2026  
**Maintenu par** : [@Linerror99](https://github.com/Linerror99)  
**Projet** : Reetik - https://portfolio-prod-portfolio-app-588105049123.us-west1.run.app
