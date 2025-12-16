# 🔐 Backend Authentification - Implémenté ! ✅

## 📦 Fichiers créés/modifiés

### Nouveaux fichiers
- ✅ `cloud-functions/rotate-access-code/main.py` - Cloud Function rotation code
- ✅ `cloud-functions/rotate-access-code/requirements.txt`
- ✅ `cloud-functions/deploy-scheduler.sh` - Script déploiement
- ✅ `cloud-functions/init-firestore.py` - Initialisation Firestore
- ✅ `backend/app/models/auth.py` - Modèles Pydantic
- ✅ `backend/app/services/firestore_service.py` - Service Firestore
- ✅ `backend/app/utils/jwt.py` - Utilitaires JWT
- ✅ `backend/app/routers/auth.py` - Routes authentification

### Fichiers modifiés
- ✅ `backend/requirements.txt` - Ajout PyJWT, bcrypt, firebase-admin
- ✅ `backend/app/config.py` - Ajout JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_DAYS
- ✅ `backend/app/main.py` - Inclusion router auth
- ✅ `backend/app/routers/videos.py` - Protection JWT + quota enforcement
- ✅ `backend/app/models/__init__.py` - Export modèles auth
- ✅ `backend/app/utils/__init__.py` - Export fonctions JWT

## 🎯 Endpoints Backend disponibles

### Authentification (Public)
- `POST /auth/verify-code` - Vérifier si code d'accès valide
- `POST /auth/register` - Inscription avec code d'accès
- `POST /auth/login` - Connexion
- `GET /auth/me` - Récupérer infos utilisateur (JWT requis)

### Vidéos (JWT requis pour TOUS)
- `POST /api/videos/create` - Créer vidéo (vérifie quota)
- `GET /api/videos` - Lister vidéos
- `GET /api/videos/{id}/status` - Statut vidéo
- `GET /api/videos/{id}/download` - Télécharger
- `GET /api/videos/{id}/stream` - Streamer

## 🔒 Sécurité implémentée

1. **Code d'accès rotatif**
   - Stocké dans Firestore `config/access_code`
   - Rotation automatique toutes les heures (Cloud Scheduler)
   - Vérifié lors de l'inscription

2. **Mots de passe**
   - Hachés avec bcrypt (salt auto)
   - Jamais stockés en clair

3. **JWT Tokens**
   - Expiration 7 jours
   - Contient: user_id, email, is_admin
   - Bearer token dans header Authorization

4. **Quota vidéos**
   - Utilisateurs normaux: 2 vidéos max
   - Admin: illimité (`max_videos = -1`)
   - Vérifié AVANT création vidéo
   - Incrémenté APRÈS succès

## 📊 Structure Firestore

### Collection `users`
```json
{
  "email": "user@example.com",
  "password_hash": "bcrypt_hash",
  "is_admin": false,
  "video_count": 0,
  "max_videos": 2,
  "created_at": "timestamp",
  "last_login": "timestamp"
}
```

### Collection `config`
Document `access_code`:
```json
{
  "code": "ABC12345",
  "updated_at": "timestamp"
}
```

## 🚀 Prochaines étapes (Frontend)

### 1. Configuration environnement
```bash
cd frontend
npm install axios react-router-dom
```

### 2. Créer AuthContext
- `src/contexts/AuthContext.jsx`
- État: user, token, loading
- Fonctions: login, register, logout, verifyCode

### 3. Créer page Login/Register
- `src/pages/Auth.jsx`
- Tabs: Login / Register
- Register: vérifier code → formulaire
- Login: email + password
- Stocker token dans localStorage

### 4. Protéger routes
- `src/components/ProtectedRoute.jsx`
- Redirect vers /auth si non connecté

### 5. Mettre à jour navbar
- Afficher email et quota
- Exemple: "john@email.com (1/2 ✨)"
- Admin: "admin@email.com (∞)"
- Bouton Déconnexion

### 6. Interceptor Axios
- Ajouter token JWT automatiquement
- Gérer expiration (redirect /auth)

### 7. Mettre à jour routes App.jsx
```jsx
<Routes>
  <Route path="/auth" element={<Auth />} />
  <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
    <Route path="create" element={<CreateVideo />} />
    <Route path="my-videos" element={<MyVideos />} />
    {/* ... */}
  </Route>
</Routes>
```

## 📝 Notes importantes

1. **JWT_SECRET_KEY**: Changer la clé en production via variable d'environnement
2. **Premier déploiement**: Exécuter `init-firestore.py` pour créer admin et code initial
3. **Cloud Function**: Déployer avec `cd cloud-functions && ./deploy-scheduler.sh`
4. **Test local**: 
   - Installer requirements: `pip install -r backend/requirements.txt`
   - Exécuter: `python -m uvicorn app.main:app --reload`

## 🧪 Tester l'API

### 1. Vérifier le code
```bash
curl -X POST http://localhost:8000/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"code": "ABC12345"}'
```

### 2. S'inscrire
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "access_code": "ABC12345"
  }'
```

### 3. Se connecter
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 4. Créer vidéo (avec token)
```bash
curl -X POST http://localhost:8000/api/videos/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"theme": "Les chats mignons"}'
```

## ✨ Avantages de cette implémentation

- ✅ Sécurité forte (bcrypt + JWT)
- ✅ Code rotatif empêche partage infini
- ✅ Quota protège budget GCP
- ✅ Admin peut créer illimité
- ✅ Facile à tester et déployer
- ✅ Compatible Cloud Run avec Workload Identity

---

**Tu peux maintenant:**
1. Déployer la Cloud Function: `cd cloud-functions && ./deploy-scheduler.sh`
2. Initialiser Firestore: `python cloud-functions/init-firestore.py`
3. Tester l'API backend en local
4. Passer au frontend ! 🎨
