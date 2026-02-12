# 🔐 Système de Code d'Accès Rotatif

## Vue d'ensemble

L'application Reetik utilise un **code d'accès rotatif** qui change **toutes les heures** pour sécuriser la génération de vidéos en production.

## Architecture

1. **Cloud Function `rotate-access-code`**
   - Génère un nouveau code aléatoire (8 caractères: A-Z + 1-9, sans O/0/I)
   - Stocke dans Firestore `config/access_code`
   - Déclenchée par Cloud Scheduler toutes les heures

2. **Cloud Scheduler**
   - Job: `rotate-access-code-hourly`
   - Fréquence: `0 * * * *` (chaque heure à 0 minutes)
   - Endpoint: Cloud Function `rotate-access-code`

3. **Firestore Rules**
   - Collection `config`: **Lecture/Écriture INTERDITE** depuis le frontend
   - Accessible uniquement via Console Firebase (admin) ou Service Account (backend)

4. **Frontend**
   - Demande le code à l'utilisateur dans le formulaire
   - Valide avant d'appeler l'API de génération

5. **Backend**
   - Vérifie le code via `verify_access_code()`
   - Retourne erreur 400 si code invalide

## Déploiement

### 1. Déployer la rotation automatique

```bash
bash deploy-rotation-code.sh
```

**Ce script va:**
- Déployer la Cloud Function `rotate-access-code`
- Créer le Cloud Scheduler job
- Générer le premier code immédiatement

### 2. Déployer les règles Firestore

```bash
bash deploy-firestore-rules.sh
```

**Sécurise:**
- Collection `config` → Accès admin seulement
- Collections `v2_*` → Lecture publique, écriture backend

### 3. Rebuild et redéployer le frontend

```bash
docker compose up -d --build frontend
# ou pour production: déployer sur Cloud Run
```

## Comment Obtenir le Code (Admin Seulement)

### Option 1: Console Firebase (Recommandé)

1. Aller sur https://console.firebase.google.com/project/reetik-project/firestore
2. Naviguer vers: `config` → `access_code`
3. Le code est dans le champ `code`

### Option 2: gcloud CLI

```bash
gcloud firestore documents describe \
  access_code \
  --collection=config \
  --project=reetik-project \
  --format='value(fields.code.stringValue)'
```

### Option 3: Python Script

```python
from google.cloud import firestore

db = firestore.Client(project='reetik-project')
doc = db.collection('config').document('access_code').get()
code = doc.to_dict()['code']
print(f"Code actuel: {code}")
```

## Utilisation

### Pour les Utilisateurs

1. Contactez l'administrateur pour obtenir le code actuel
2. Allez sur https://reetik.app/create
3. Entrez le code dans le champ "Code d'accès" (8 caractères)
4. Le code change toutes les heures, redemandez si expiré

### Pour les Administrateurs

1. Récupérez le code via une des méthodes ci-dessus
2. Partagez le code aux utilisateurs autorisés
3. Le code change automatiquement à chaque heure pile (ex: 14:00, 15:00, etc.)

## Monitoring

### Vérifier que la rotation fonctionne

```bash
# Voir les logs de la Cloud Function
gcloud functions logs read rotate-access-code \
  --region=us-central1 \
  --limit=10 \
  --project=reetik-project

# Voir les exécutions du Scheduler
gcloud scheduler jobs describe rotate-access-code-hourly \
  --location=us-central1 \
  --project=reetik-project
```

### Tester manuellement la rotation

```bash
# Déclencher immédiatement (sans attendre l'heure)
gcloud scheduler jobs run rotate-access-code-hourly \
  --location=us-central1 \
  --project=reetik-project

# Vérifier le nouveau code
# (via Console Firebase ou CLI)
```

## Sécurité

✅ **Ce qui est sécurisé:**
- Le code n'est jamais exposé côté client
- Le code n'apparaît pas dans les URLs ou logs frontend
- Firestore Rules empêchent la lecture depuis le frontend
- Le code change automatiquement toutes les heures

⚠️ **Points d'attention:**
- Partagez le code uniquement via canal sécurisé (Signal, email chiffré, etc.)
- Ne publiez JAMAIS le code sur GitHub, Slack public, etc.
- Vérifiez régulièrement les logs pour détecter tentatives d'accès non autorisées

## Dépannage

### Le code ne fonctionne pas

1. Vérifier que le code est exact (8 caractères, majuscules)
2. Vérifier l'heure de la dernière rotation dans Firestore (champ `updated_at`)
3. Si expiré, obtenir le nouveau code

### La rotation ne fonctionne plus

1. Vérifier que le Cloud Scheduler est actif:
   ```bash
   gcloud scheduler jobs describe rotate-access-code-hourly --location=us-central1
   ```

2. Vérifier les logs de la Cloud Function:
   ```bash
   gcloud functions logs read rotate-access-code --region=us-central1 --limit=50
   ```

3. Déclencher manuellement pour tester:
   ```bash
   gcloud scheduler jobs run rotate-access-code-hourly --location=us-central1
   ```

### Désactiver temporairement (développement)

Pour désactiver la rotation en dev:

```bash
gcloud scheduler jobs pause rotate-access-code-hourly --location=us-central1
```

Réactiver avec:

```bash
gcloud scheduler jobs resume rotate-access-code-hourly --location=us-central1
```

## Coûts

- **Cloud Function**: ~$0.0000004 par invocation (24 invocations/jour)
- **Cloud Scheduler**: ~$0.10/mois (1 job)
- **Firestore**: Négligeable (1 document lu/écrit par heure)

**Total estimé: < $0.15/mois**
