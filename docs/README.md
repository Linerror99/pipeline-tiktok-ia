# 📚 Documentation Pipeline TikTok IA

Cette documentation est organisée par catégorie pour faciliter la navigation.

## 📖 Guide de Navigation

### 🚀 Déploiement (`deployment/`)

Documentation pour déployer et configurer l'infrastructure :

- **[DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)** - Guide complet de déploiement Cloud Functions
- **[PRODUCTION_DEPLOYMENT.md](deployment/PRODUCTION_DEPLOYMENT.md)** - Déploiement production (Cloud Run + CI/CD)
- **[WIF_SETUP.md](deployment/WIF_SETUP.md)** - Configuration Workload Identity Federation pour GitHub Actions
- **[PRODUCTION_URLS.md](deployment/PRODUCTION_URLS.md)** - URLs et endpoints de production
- **[SERVICE_ACCOUNT_SETUP.md](deployment/SERVICE_ACCOUNT_SETUP.md)** - Configuration des service accounts GCP
- **[DOCKER_OPTIMIZATION.md](deployment/DOCKER_OPTIMIZATION.md)** - Optimisation des images Docker

### 🏗️ Architecture (`architecture/`)

Documentation sur l'architecture et les systèmes :

- **[AUTH_SYSTEM.md](architecture/AUTH_SYSTEM.md)** - Système d'authentification complet (JWT, quotas)
- **[ACCESS_CODE_SYSTEM.md](architecture/ACCESS_CODE_SYSTEM.md)** - Système de codes d'accès rotatifs
- **[RETRY_SYSTEM.md](architecture/RETRY_SYSTEM.md)** - Système de retry automatique pour clips vidéo
- **[FLOW_SYNC_V2.md](architecture/FLOW_SYNC_V2.md)** - Flow de synchronisation V2
- **[Structure_actuelle.md](architecture/Structure_actuelle.md)** - Structure actuelle détaillée du projet

### 🔄 Migration (`migration/`)

Historique des migrations et comparaisons de versions :

- **[MIGRATION_V2_RESUME.md](migration/MIGRATION_V2_RESUME.md)** - Résumé de la migration V2
- **[V1_VS_V2_COMPARISON.md](migration/V1_VS_V2_COMPARISON.md)** - Comparaison détaillée V1 vs V2
- **[V2.1_MIGRATION.md](migration/V2.1_MIGRATION.md)** - Notes de migration V2.1

### 📋 Plans & Analyses (`plans/`)

Plans de développement, évolutions et analyses de coûts :

- **[PLAN_DEVELOPPEMENT_COMPLET.md](plans/PLAN_DEVELOPPEMENT_COMPLET.md)** - Plan de développement complet
- **[PLAN_EVOLUTION_V2.md](plans/PLAN_EVOLUTION_V2.md)** - Plan d'évolution V2
- **[PLAN_MIGRATION_INCREMENTAL.md](plans/PLAN_MIGRATION_INCREMENTAL.md)** - Plan de migration incrémentale
- **[PLAN-AMELIORATION_V2.md](plans/PLAN-AMELIORATION_V2.md)** - Plan d'amélioration V2
- **[EVOLUTION_VEO3.1.md](plans/EVOLUTION_VEO3.1.md)** - Évolution vers Veo 3.1
- **[VEO3.1_doc.md](plans/VEO3.1_doc.md)** - Documentation Veo 3.1
- **[PRICING_ANALYSIS_REAL.md](plans/PRICING_ANALYSIS_REAL.md)** - Analyse de coûts réels
- **[Pricing_vertexAI.md](plans/Pricing_vertexAI.md)** - Tarification Vertex AI

### 📦 Archive (`legacy/`)

Documentation obsolète conservée pour référence :

- **[TEST_PLAN_COMPLETE.md](legacy/TEST_PLAN_COMPLETE.md)** - Plan de tests (ancien)
- **[WEBAPP_README.md](legacy/WEBAPP_README.md)** - README webapp (ancien)
- **[README_DOCKER.md](legacy/README_DOCKER.md)** - README Docker (ancien)
- **[DOCKER_README.md](legacy/DOCKER_README.md)** - README Docker alternatif (ancien)

---

## 🎯 Parcours Recommandés

### Pour Démarrer le Projet
1. [README.md](../README.md) - Vue d'ensemble
2. [DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md) - Déploiement Cloud Functions
3. [AUTH_SYSTEM.md](architecture/AUTH_SYSTEM.md) - Comprendre l'authentification

### Pour Déployer en Production
1. [PRODUCTION_DEPLOYMENT.md](deployment/PRODUCTION_DEPLOYMENT.md) - Setup Cloud Run
2. [WIF_SETUP.md](deployment/WIF_SETUP.md) - CI/CD avec GitHub Actions
3. [SERVICE_ACCOUNT_SETUP.md](deployment/SERVICE_ACCOUNT_SETUP.md) - Permissions GCP

### Pour Comprendre l'Architecture
1. [Structure_actuelle.md](architecture/Structure_actuelle.md) - Structure du projet
2. [AUTH_SYSTEM.md](architecture/AUTH_SYSTEM.md) - Système d'authentification
3. [FLOW_SYNC_V2.md](architecture/FLOW_SYNC_V2.md) - Flow de génération vidéo

### Pour Estimer les Coûts
1. [PRICING_ANALYSIS_REAL.md](plans/PRICING_ANALYSIS_REAL.md) - Analyse détaillée
2. [Pricing_vertexAI.md](plans/Pricing_vertexAI.md) - Tarifs Vertex AI

---

## 📞 Support

Pour toute question, consultez d'abord la documentation pertinente ci-dessus.

**Navigation rapide :**
- 🐛 Problèmes de déploiement → `deployment/`
- 🔐 Questions sécurité/auth → `architecture/AUTH_SYSTEM.md`
- 💰 Questions budget → `plans/PRICING_ANALYSIS_REAL.md`
- 🔄 Historique changements → `migration/`
