import functions_framework
from google.cloud import firestore
import random
import string
from datetime import datetime

# Initialiser Firestore
db = firestore.Client()

def generate_access_code(length=8):
    """Génère un code aléatoire de 8 caractères (majuscules + chiffres)"""
    characters = string.ascii_uppercase + string.digits
    # Exclure les caractères similaires pour éviter confusion : 0/O, 1/I
    characters = characters.replace('O', '').replace('I', '').replace('0', '')
    return ''.join(random.choice(characters) for _ in range(length))

@functions_framework.http
def rotate_access_code(request):
    """
    Cloud Function qui régénère le code d'accès et le stocke dans Firestore.
    Appelée par Cloud Scheduler toutes les heures.
    """
    try:
        # Générer un nouveau code
        new_code = generate_access_code()
        
        # Mettre à jour dans Firestore
        config_ref = db.collection('config').document('access_code')
        config_ref.set({
            'code': new_code,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        
        print(f"✅ Code d'accès mis à jour: {new_code}")
        
        return {
            'success': True,
            'code': new_code,
            'message': 'Code d\'accès régénéré avec succès'
        }, 200
        
    except Exception as e:
        print(f"❌ Erreur lors de la rotation du code: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }, 500
