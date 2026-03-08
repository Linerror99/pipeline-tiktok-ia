# ✅ TODO - Tâches Immédiates Reetik

**Dernière mise à jour** : 7 Mars 2026  
**Sprint actuel** : Monitoring & Stabilité

> 📖 **Roadmap complète** : Voir [ROADMAP.md](ROADMAP.md) pour vision long terme

---

## 🔥 SPRINT ACTUEL (2-3 semaines)

### 🎯 Objectifs
1. ✅ Monitoring complet (dashboards + alertes)
2. ✅ Tests automatisés (backend + frontend)
3. ✅ Optimisations UX critiques

---

## 📊 Monitoring & Observabilité (Semaine 1-2)

### Cloud Monitoring Dashboards

#### Dashboard 1 : Cloud Run Services
**Fichier** : `terraform/monitoring-cloud-run.tf`

- [ ] Créer dashboard "Reetik - Cloud Run"
- [ ] Widget : Requêtes/min (Backend + Frontend)
- [ ] Widget : Latence P50/P95/P99 (Backend API)
- [ ] Widget : Taux erreurs 4xx/5xx
- [ ] Widget : CPU utilization (Backend containers)
- [ ] Widget : Memory utilization (Backend containers)
- [ ] Widget : Active instances count
- [ ] Widget : Cold starts count
- [ ] Déployer : `terraform apply`

**Commandes de test** :
```bash
# Vérifier métriques disponibles
gcloud monitoring metrics-descriptors list \
  --filter="resource.type=cloud_run_revision"

# Créer dashboard via gcloud (alternative)
gcloud monitoring dashboards create --config-from-file=dashboards/cloud-run.json
```

#### Dashboard 2 : Cloud Functions
**Fichier** : `terraform/monitoring-cloud-functions.tf`

- [ ] Dashboard "Reetik - Cloud Functions"
- [ ] Widget : Invocations/min par fonction (script, audio, video, assembler, monitor)
- [ ] Widget : Durée exécution moyenne par fonction
- [ ] Widget : Taux erreurs par fonction
- [ ] Widget : Cold starts vs warm starts
- [ ] Widget : Active instances
- [ ] Widget : Memory usage peak
- [ ] Déployer

#### Dashboard 3 : Firestore
**Fichier** : `terraform/monitoring-firestore.tf`

- [ ] Dashboard "Reetik - Firestore"
- [ ] Widget : Lectures/min par collection (users, videos, config)
- [ ] Widget : Écritures/min par collection
- [ ] Widget : Document count (estimation)
- [ ] Widget : Quota utilization (daily/monthly)
- [ ] Widget : Latence opérations
- [ ] Déployer

#### Dashboard 4 : Cloud Storage
**Fichier** : `terraform/monitoring-storage.tf`

- [ ] Dashboard "Reetik - Storage"
- [ ] Widget : Requests/min (GET, PUT, DELETE)
- [ ] Widget : Bande passante (upload/download)
- [ ] Widget : Storage size (par bucket)
- [ ] Widget : Object count
- [ ] Déployer

#### Dashboard 5 : Coûts
**Fichier** : `terraform/monitoring-costs.tf`

- [ ] Dashboard "Reetik - Coûts"
- [ ] Widget : Coûts quotidiens estimés (par service)
- [ ] Widget : Trend coûts (7 derniers jours)
- [ ] Widget : Top 5 services coûteux
- [ ] Widget : Coût/vidéo générée (calculé)
- [ ] Projection mensuelle
- [ ] Déployer

---

### Alerting Policies

#### Alertes Critiques (Pager Duty Level)
**Fichier** : `terraform/alerts-critical.tf`

- [ ] Alerte : Backend error rate > 5% (5 min)
  - Condition : `rate(error_count) / rate(request_count) > 0.05`
  - Notification : Email + Slack
  - Auto-close : Si < 2% pendant 10 min

- [ ] Alerte : Backend latency P95 > 5s (10 min)
  - Condition : `percentile(latency, 95) > 5000ms`
  - Notification : Email + Slack

- [ ] Alerte : Cloud Function failed > 3 fois consécutives
  - Condition : `consecutive_failures > 3`
  - Scope : generate-assembler-agent-v2
  - Notification : Email immédiat

- [ ] Alerte : Firestore quota > 90%
  - Vérification : Toutes les heures
  - Notification : Email + Slack

#### Alertes Warning (Email Only)
**Fichier** : `terraform/alerts-warning.tf`

- [ ] Alerte : Coûts quotidiens > $50
  - Vérification : Minuit UTC
  - Notification : Email summary

- [ ] Alerte : Cold starts > 50% invocations (Cloud Run)
  - Période : 1 heure
  - Notification : Email

- [ ] Alerte : Storage bandwidth > 100GB/jour
  - Notification : Email

#### Configuration Notifications
**Fichier** : `terraform/notification-channels.tf`

- [ ] Créer Notification Channel : Email (admin@reetik.com)
- [ ] Créer Notification Channel : Slack webhook
- [ ] Tester envois notifications
- [ ] Documenter procédure on-call

---

### Structured Logging

#### Backend (FastAPI)
**Fichier** : `backend/app/utils/logging_config.py`

- [ ] Créer middleware logging structuré JSON
- [ ] Ajouter champs : `trace_id`, `user_id`, `endpoint`, `method`, `status_code`, `latency_ms`
- [ ] Logger événements business :
  - User registration
  - Login (success/failed)
  - Video creation request
  - Video generation completed
  - Quota exceeded
  - Error details (avec stacktrace)

**Exemple log** :
```json
{
  "timestamp": "2026-03-07T14:30:00.123Z",
  "severity": "INFO",
  "trace_id": "abc123...",
  "user_id": "user_xyz",
  "endpoint": "/videos/",
  "method": "POST",
  "status_code": 201,
  "latency_ms": 1234,
  "event": "video_created",
  "video_id": "vid_789",
  "theme": "Les pyramides"
}
```

- [ ] Tester logs dans Cloud Logging
- [ ] Créer requêtes sauvegardées :
  - Top 10 erreurs (24h)
  - Slow requests (> 3s)
  - Failed authentications
  - Quota exceeded events

#### Cloud Functions
**Fichiers** : `agent-*/main.py`

- [ ] Standardiser format logs JSON
- [ ] Ajouter `video_id` dans tous les logs
- [ ] Logger durées par étape :
  - Script generation time
  - Audio generation time
  - Video clip generation time (par clip)
  - Assembly time
- [ ] Logger coûts API estimés (Gemini, TTS, Veo)

---

## 🧪 Tests Automatisés (Semaine 2-3)

### Backend Tests
**Dossier** : `backend/tests/`

#### Tests API (pytest)
- [ ] Setup : `tests/conftest.py` (fixtures, test client)
- [ ] `tests/test_auth.py` :
  - [ ] Test registration (success)
  - [ ] Test registration (invalid email)
  - [ ] Test registration (invalid access code)
  - [ ] Test login (success)
  - [ ] Test login (wrong password)
  - [ ] Test JWT token validation
  - [ ] Test token expiration

- [ ] `tests/test_videos.py` :
  - [ ] Test create video (authenticated)
  - [ ] Test create video (quota exceeded)
  - [ ] Test list videos (own videos only)
  - [ ] Test get video details
  - [ ] Test create video (invalid theme)

- [ ] `tests/test_quota.py` :
  - [ ] Test quota check
  - [ ] Test quota increment
  - [ ] Test admin unlimited quota

#### Tests Intégration (Firestore Emulator)
- [ ] Setup emulator : `docker-compose.test.yml`
- [ ] `tests/integration/test_firestore.py` :
  - [ ] Test user CRUD operations
  - [ ] Test video CRUD operations
  - [ ] Test concurrent writes
  - [ ] Test transactions

#### CI/CD Integration
- [ ] `.github/workflows/backend-tests.yml` :
  - Trigger : PR vers main
  - Steps : Install deps → Run tests → Coverage report
  - Fail si coverage < 70%

**Commandes** :
```bash
# Local
cd backend
pytest tests/ -v --cov=app --cov-report=html

# CI
pytest tests/ -v --cov=app --cov-report=xml
```

---

### Frontend Tests
**Dossier** : `frontend-v2/tests/`

#### Tests Composants (Vitest + React Testing Library)
- [ ] Setup : `vitest.config.ts`
- [ ] `tests/components/LoginForm.test.tsx` :
  - [ ] Render form
  - [ ] Submit valid credentials
  - [ ] Show error invalid code
  - [ ] Show loading state

- [ ] `tests/components/CreateVideoForm.test.tsx` :
  - [ ] Render form
  - [ ] Submit valid theme
  - [ ] Show error empty theme
  - [ ] Show quota exceeded message

- [ ] `tests/components/VideoList.test.tsx` :
  - [ ] Render video list
  - [ ] Show empty state
  - [ ] Filter by status

#### Tests E2E (Playwright)
- [ ] Setup : `playwright.config.ts`
- [ ] `tests/e2e/auth.spec.ts` :
  - [ ] User can register
  - [ ] User can login
  - [ ] User can logout

- [ ] `tests/e2e/video-creation.spec.ts` :
  - [ ] User can create video
  - [ ] User sees progress updates (WebSocket)
  - [ ] User can download completed video
  - [ ] User sees quota limit

#### CI/CD Integration
- [ ] `.github/workflows/frontend-tests.yml` :
  - Unit tests : Vitest
  - E2E tests : Playwright (si PR vers main)

**Commandes** :
```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e

# CI
npm run test:ci
```

---

## 🎨 Optimisations UX Critiques (Semaine 3)

### Interface
- [ ] **Loading states améliorés** :
  - Skeleton screens pendant chargement vidéos
  - Progress bar détaillée (étape actuelle visible)
  - Estimation temps restant

- [ ] **Messages erreurs clairs** :
  - "Code d'accès expiré. Nouveau code : ABC123XY"
  - "Quota atteint (2/2). Prochain quota dans 23h."
  - "Erreur génération. Réessayer automatiquement..."

- [ ] **Preview thumbnails** :
  - Générer thumbnail de chaque vidéo (FFmpeg)
  - Afficher dans galerie

### Performance Frontend
- [ ] Lazy loading composants (React.lazy)
- [ ] Pagination liste vidéos (10 par page)
- [ ] Cache API responses (React Query)
- [ ] Optimisation bundle Vite (code splitting)

---

## 📝 Documentation

- [ ] `docs/monitoring/DASHBOARDS.md` - Guide dashboards
- [ ] `docs/monitoring/ALERTS.md` - Procédures alertes
- [ ] `docs/testing/BACKEND_TESTS.md` - Guide tests backend
- [ ] `docs/testing/FRONTEND_TESTS.md` - Guide tests frontend
- [ ] `docs/operations/RUNBOOK.md` - Procédures incidents
- [ ] Mettre à jour `ROADMAP.md` après sprint

---

## 🎯 Critères de Succès Sprint

### Monitoring
- ✅ 5 dashboards déployés et fonctionnels
- ✅ 10+ alertes configurées (critical + warning)
- ✅ Logs structurés JSON sur tous services
- ✅ Requêtes sauvegardées Log Explorer

### Tests
- ✅ Backend coverage > 70%
- ✅ Frontend tests composants clés
- ✅ E2E flow création vidéo
- ✅ CI/CD exécute tests automatiquement

### UX
- ✅ Loading states améliorés
- ✅ Messages erreurs clairs
- ✅ Preview thumbnails

---

## 📞 Support

**Questions** : Voir [ROADMAP.md](ROADMAP.md) pour vision long terme  
**Bugs** : Ouvrir issue GitHub  
**Docs** : Dossier `docs/`

---

**Maintenu par** : [@Linerror99](https://github.com/Linerror99)  
**Projet** : Reetik
