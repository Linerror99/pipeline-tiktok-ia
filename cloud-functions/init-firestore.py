#!/usr/bin/env python3
"""
Script d'initialisation Firestore
- Crée les collections nécessaires
- Génère le premier code d'accès
- Crée un utilisateur admin
"""

from google.cloud import firestore
import bcrypt
import random
import string
from datetime import datetime

# Initialiser Firestore
db = firestore.Client()

def generate_access_code(length=8):
    """Génère un code aléatoire"""
    characters = string.ascii_uppercase + string.digits
    characters = characters.replace('O', '').replace('I', '').replace('0', '')
    return ''.join(random.choice(characters) for _ in range(length))

def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_firestore():
    """Initialise Firestore avec les données de base"""
    
    print("🔥 Initialisation Firestore...")
    
    # 1. Créer le code d'accès initial
    print("\n📋 Génération du code d'accès initial...")
    access_code = generate_access_code()
    
    config_ref = db.collection('config').document('access_code')
    config_ref.set({
        'code': access_code,
        'updated_at': firestore.SERVER_TIMESTAMP
    })
    
    print(f"✅ Code d'accès créé: {access_code}")
    print(f"   📝 Notez-le bien, il sera régénéré toutes les heures!")
    
    # 2. Créer un utilisateur admin
    print("\n👤 Création de l'utilisateur admin...")
    admin_email = input("Email admin (votre email): ")
    admin_password = input("Mot de passe admin: ")
    
    admin_ref = db.collection('users').document()
    admin_ref.set({
        'email': admin_email,
        'password_hash': hash_password(admin_password),
        'is_admin': True,
        'video_count': 0,
        'max_videos': -1,  # -1 = illimité
        'created_at': firestore.SERVER_TIMESTAMP,
        'last_login': None
    })
    
    print(f"✅ Admin créé: {admin_email}")
    
    # 3. Créer les index (optionnel, se font automatiquement)
    print("\n📊 Collections créées:")
    print("   - config (code d'accès)")
    print("   - users (utilisateurs)")
    
    print("\n✅ Initialisation terminée !")
    print(f"\n🔐 Code d'accès actuel: {access_code}")
    print(f"👤 Admin: {admin_email}")
    print("\n📱 Vous pouvez maintenant déployer le backend et le frontend.")

if __name__ == "__main__":
    try:
        init_firestore()
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        exit(1)
