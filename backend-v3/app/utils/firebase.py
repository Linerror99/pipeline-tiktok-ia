"""Firebase Admin SDK initialization for V3."""
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials, firestore
import os

_app = None
_db = None

# Base de données Firestore V3 séparée de V2
FIRESTORE_DATABASE_ID = os.getenv("FIRESTORE_DATABASE", "reetik-v3")


def get_firebase_app():
    """Initialise Firebase Admin (une seule fois)."""
    global _app
    if _app is None:
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if creds_path and os.path.exists(creds_path):
            cred = credentials.Certificate(creds_path)
            _app = firebase_admin.initialize_app(cred)
        else:
            _app = firebase_admin.initialize_app()
    return _app


def get_firestore_client():
    """Client Firestore V3 — utilise la base nommée 'reetik-v3' (pas '(default)')."""
    global _db
    if _db is None:
        get_firebase_app()
        _db = firestore.client(database_id=FIRESTORE_DATABASE_ID)
    return _db


def verify_firebase_token(id_token: str) -> dict:
    """
    Vérifie un Firebase ID token (envoyé par le frontend après Google Sign-In).
    Returns: decoded token dict avec uid, email, name, picture, etc.
    Raises: firebase_admin.auth.InvalidIdTokenError si invalide.
    """
    get_firebase_app()
    return firebase_auth.verify_id_token(id_token)
