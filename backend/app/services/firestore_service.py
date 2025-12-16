"""
Service Firestore pour gérer les utilisateurs et la configuration
"""
from firebase_admin import firestore, credentials, initialize_app
from datetime import datetime
from typing import Optional
import os

from ..models.auth import UserInDB

# Variable globale pour le client Firestore
_db = None

def get_firestore_client():
    """Récupère le client Firestore (initialise Firebase si nécessaire)"""
    global _db
    if _db is None:
        # Initialiser Firebase Admin si pas déjà fait
        try:
            # Vérifier si Firebase est déjà initialisé
            _db = firestore.client()
        except ValueError:
            # Firebase pas initialisé, l'initialiser maintenant
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path and os.path.exists(creds_path):
                cred = credentials.Certificate(creds_path)
                initialize_app(cred)
            else:
                # Cloud Run: credentials automatiques
                initialize_app()
            _db = firestore.client()
    return _db


def get_current_access_code() -> Optional[str]:
    """Récupère le code d'accès actuel"""
    try:
        db = get_firestore_client()
        doc_ref = db.collection('config').document('access_code')
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict().get('code')
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération du code: {str(e)}")
        return None


def verify_access_code(code: str) -> bool:
    """Vérifie si le code d'accès est valide"""
    current_code = get_current_access_code()
    return current_code is not None and current_code == code


def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Récupère un utilisateur par son email"""
    try:
        db = get_firestore_client()
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        docs = query.stream()
        
        for doc in docs:
            data = doc.to_dict()
            return UserInDB(
                id=doc.id,
                email=data['email'],
                password_hash=data['password_hash'],
                is_admin=data.get('is_admin', False),
                video_count=data.get('video_count', 0),
                max_videos=data.get('max_videos', 2),
                created_at=data.get('created_at', datetime.now()),
                last_login=data.get('last_login')
            )
        
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
        return None


def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    """Récupère un utilisateur par son ID"""
    try:
        db = get_firestore_client()
        doc_ref = db.collection('users').document(user_id)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            return UserInDB(
                id=doc.id,
                email=data['email'],
                password_hash=data['password_hash'],
                is_admin=data.get('is_admin', False),
                video_count=data.get('video_count', 0),
                max_videos=data.get('max_videos', 2),
                created_at=data.get('created_at', datetime.now()),
                last_login=data.get('last_login')
            )
        
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération de l'utilisateur: {str(e)}")
        return None


def create_user(email: str, password_hash: str, is_admin: bool = False) -> Optional[UserInDB]:
    """Crée un nouvel utilisateur"""
    try:
        db = get_firestore_client()
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'is_admin': is_admin,
            'video_count': 0,
            'max_videos': -1 if is_admin else 2,  # -1 = illimité pour admin
            'created_at': firestore.SERVER_TIMESTAMP,
            'last_login': None
        }
        
        doc_ref = db.collection('users').document()
        doc_ref.set(user_data)
        
        # Récupérer l'utilisateur créé
        return get_user_by_id(doc_ref.id)
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur: {str(e)}")
        return None


def update_last_login(user_id: str) -> bool:
    """Met à jour la date de dernière connexion"""
    try:
        db = get_firestore_client()
        doc_ref = db.collection('users').document(user_id)
        doc_ref.update({
            'last_login': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        print(f"Erreur lors de la mise à jour du last_login: {str(e)}")
        return False


def increment_video_count(user_id: str) -> bool:
    """Incrémente le compteur de vidéos"""
    try:
        db = get_firestore_client()
        doc_ref = db.collection('users').document(user_id)
        doc_ref.update({
            'video_count': firestore.Increment(1)
        })
        return True
    except Exception as e:
        print(f"Erreur lors de l'incrémentation du compteur: {str(e)}")
        return False


def can_create_video(user: UserInDB) -> bool:
    """Vérifie si l'utilisateur peut créer une vidéo"""
    # Admin illimité
    if user.is_admin or user.max_videos == -1:
        return True
    
    # Utilisateur normal: vérifier quota
    return user.video_count < user.max_videos
