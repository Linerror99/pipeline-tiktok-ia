#!/usr/bin/env python3
"""
Script pour définir un code d'accès de test dans Firestore
Pour simplifier les tests locaux
"""

from google.cloud import firestore
import os
from datetime import datetime

# Configurer les credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "backend/credentials.json"

# Code de test fixe pour le développement local
TEST_ACCESS_CODE = "DEV12345"

def set_test_access_code():
    """Définit un code d'accès de test dans Firestore"""
    try:
        db = firestore.Client()
        
        config_ref = db.collection('config').document('access_code')
        config_ref.set({
            'code': TEST_ACCESS_CODE,
            'updated_at': datetime.utcnow(),
            'environment': 'development'
        })
        
        print(f"✅ Code d'accès de test défini: {TEST_ACCESS_CODE}")
        print(f"   Ce code est fixe pour les tests locaux")
        print(f"   À utiliser dans le frontend via VITE_ACCESS_CODE={TEST_ACCESS_CODE}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    set_test_access_code()
