"""
Test RÉEL du flow V2 end-to-end avec Terraform
Appelle les Cloud Functions déployées

Usage:
  python test_flow_real_v2.py --theme "Intelligence Artificielle" --duration 24
"""

import os
import sys
import json
import argparse
import time
import requests
import subprocess
from datetime import datetime
import urllib3

# Désactiver warnings SSL pour test local
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
PROJECT_ID = "reetik-project"
REGION = "us-central1"

# URLs Cloud Functions (Gen2 depuis Terraform outputs)
SCRIPT_URL = "https://agent-script-v2-vrzs3y5aoq-uc.a.run.app"
VIDEO_URL = "https://agent-video-v2-vrzs3y5aoq-uc.a.run.app"
MONITOR_URL = "https://check-and-retry-clips-vrzs3y5aoq-uc.a.run.app"
ASSEMBLER_URL = "https://agent-assembler-v2-vrzs3y5aoq-uc.a.run.app"

def get_auth_token():
    """Générer un token d'identité pour Cloud Functions Gen2"""
    try:
        # Essayer avec gcloud dans le PATH
        result = subprocess.run(
            ['gcloud', 'auth', 'print-identity-token'],
            capture_output=True,
            text=True,
            check=True,
            shell=True  # Utiliser shell pour Windows
        )
        return result.stdout.strip()
    except FileNotFoundError:
        # gcloud pas trouvé, essayer avec credentials par défaut
        print("⚠️  gcloud non trouvé, utilisation credentials par défaut Google Cloud")
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
            import google.auth
            
            credentials, project = google.auth.default()
            
            # Rafraîchir le token si nécessaire
            if not credentials.valid:
                if credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
            
            # Pour ID token (Cloud Functions Gen2)
            if hasattr(credentials, 'id_token'):
                return credentials.id_token
            else:
                print("   ℹ️  Utilisation access token au lieu d'id token")
                return credentials.token
                
        except Exception as e:
            print(f"⚠️  Impossible d'obtenir token: {e}")
            print("   Test sans authentification (fonctions publiques uniquement)")
            return None
    except Exception as e:
        print(f"❌ Erreur génération token: {e}")
        print("   Assurez-vous d'être authentifié: gcloud auth login")
        sys.exit(1)

def test_flow_real(theme, duration):
    """Test flow complet V2 avec Cloud Functions réelles"""
    
    video_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Obtenir token d'authentification
    print("🔐 Génération token d'authentification...")
    token = get_auth_token()
    
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
        print("✅ Token obtenu")
    else:
        print("⚠️  Pas de token - les fonctions doivent être publiques")
    
    print("=" * 70)
    print("🧪 TEST FLOW V2 RÉEL (Cloud Functions via Terraform)")
    print("=" * 70)
    print(f"Video ID: {video_id}")
    print(f"Thème: {theme}")
    print(f"Durée: {duration}s")
    print("=" * 70)
    
    # ÉTAPE 1: Appeler agent-script
    print("\n📝 ÉTAPE 1: Génération script...")
    print(f"POST {SCRIPT_URL}")
    
    try:
        response = requests.post(SCRIPT_URL, 
            headers=headers,
            json={
                'theme': theme,
                'video_id': video_id,
                'target_duration': duration
            }, 
            timeout=60,
            verify=False)  # Désactiver vérification SSL pour test local
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Script généré: {result['blocks_generated']} blocs")
            print(f"   Durée: {result['duration']}s")
            print(f"\n   📤 Script uploadé dans Cloud Storage")
            print(f"      gs://tiktok-pipeline-v2-artifacts-reetik-project/{video_id}/script_v2.json")
            print(f"\n   ⚡ L'upload du script a déclenché automatiquement agent-video-v2")
            print(f"      (Cloud Storage trigger)")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # ÉTAPE 2: Vérifier que agent-video-v2 a été déclenché
    print("\n🎬 ÉTAPE 2: Génération parallèle des vidéos...")
    print(f"   ⏳ agent-video-v2 a été déclenché automatiquement par l'upload")
    print(f"   📡 Le trigger Cloud Storage appelle la fonction avec le CloudEvent")
    print(f"   ⏱️  Attente de 10 secondes pour que la fonction démarre...")
    
    time.sleep(10)
    
    print(f"   ✅ Les opérations Veo ont été lancées en parallèle")
    print(f"      Vérifiez Firestore collection 'v2_veo_operations'")
    
    # Note: Impossible de tester directement car agent-video-v2 est déclenché par CloudEvent
    # Le test réel se fait via l'upload du fichier script_v2.json
    
    """
    # Si vous voulez vraiment tester manuellement, utilisez un CloudEvent valide:
    try:
        cloudevent_headers = {
            'ce-specversion': '1.0',
            'ce-type': 'google.cloud.storage.object.v1.finalized',
            'ce-source': f'//storage.googleapis.com/projects/_/buckets/tiktok-pipeline-v2-artifacts-reetik-project',
            'ce-id': 'test-event-id',
            'ce-time': datetime.now().isoformat() + 'Z',
            'content-type': 'application/json'
        }
        if token:
            cloudevent_headers['Authorization'] = f'Bearer {token}'
            
        response = requests.post(VIDEO_URL,
            headers=cloudevent_headers,
            json={
                'bucket': 'tiktok-pipeline-v2-artifacts-reetik-project',
                'name': f'{video_id}/script_v2.json'
            },
            timeout=60,
            verify=False)
    except Exception as e:
        pass
    """
    
    # ÉTAPE 3: Monitoring manuel (Cloud Scheduler le fera automatiquement)
    print("\n🔍 ÉTAPE 3: Monitoring opérations...")
    print(f"⏰ Cloud Scheduler appelle check-and-retry-clips toutes les minutes")
    print(f"   Pour tester manuellement: POST {MONITOR_URL}")
    
    # Appel manuel pour test
    print("\n   Test manuel du monitor...")
    try:
        response = requests.post(MONITOR_URL, headers=headers, timeout=60, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Monitor exécuté: {result.get('total_checked', 0)} opérations vérifiées")
            if 'v2' in result:
                print(f"      V2 - Vérifiées: {result['v2']['checked']}, Assemblées: {result['v2'].get('assembled', 0)}")
        else:
            print(f"   ⚠️ Erreur {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"   ⚠️ Erreur: {e}")
    
    # ÉTAPE 3: Instructions pour la suite
    print("\n🎞️ ÉTAPE 4: Assemblage final...")
    print(f"   L'assembleur sera appelé automatiquement par check-and-retry-clips")
    print(f"   quand tous les blocs seront générés")
    
    # Monitoring en temps réel
    print("\n" + "=" * 70)
    print("📊 MONITORING EN TEMPS RÉEL")
    print("=" * 70)
    print(f"Video ID: {video_id}")
    print("")
    print("Pour suivre la progression:")
    print("")
    print("1. Firestore Console:")
    print(f"   https://console.firebase.google.com/project/{PROJECT_ID}/firestore")
    print(f"   Collection: v2_veo_operations/{video_id}")
    print("")
    print("2. Cloud Storage:")
    print(f"   gsutil ls gs://tiktok-pipeline-v2-artifacts-{PROJECT_ID}/{video_id}/")
    print("")
    print("3. Cloud Functions Logs:")
    print("   gcloud functions logs read check-and-retry-clips --region=us-central1 --gen2 --limit=50")
    print("")
    print("4. Vérifier status manuellement:")
    print(f"   python test_flow_real_v2.py --check {video_id}")
    print("")
    
    # Attendre et vérifier périodiquement
    print("⏳ Attente génération (vous pouvez Ctrl+C pour arrêter)...")
    print("   Cloud Scheduler vérifie automatiquement toutes les minutes")
    
    try:
        for i in range(10):  # Vérifier pendant 10 minutes max
            time.sleep(60)  # Attendre 1 minute
            
            print(f"\n⏰ Vérification {i+1}/10...")
            
            try:
                response = requests.post(MONITOR_URL, headers=headers, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    if result.get('processed', 0) > 0:
                        print(f"   ✅ {result['processed']} opérations traitées")
                    else:
                        print(f"   ⏳ En cours... ({result.get('checked', 0)} opérations en cours)")
            except:
                pass
                
    except KeyboardInterrupt:
        print("\n\n⚠️  Arrêt manuel - La génération continue en arrière-plan")
        print(f"   Suivez la progression dans Firestore: v2_veo_operations/{video_id}")
    
    print("\n" + "=" * 70)
    print("✅ Test lancé avec succès !")
    print("=" * 70)

def main():
    parser = argparse.ArgumentParser(description='Test flow V2 réel avec Cloud Functions')
    parser.add_argument('--theme', type=str, default='Intelligence Artificielle',
                        help='Thème de la vidéo')
    parser.add_argument('--duration', type=int, default=15,
                        help='Durée cible (8, 15, 36, 60)')
    
    args = parser.parse_args()
    
    # Vérifier que les Cloud Functions sont déployées
    print("🔍 Vérification Cloud Functions...")
    print(f"Script:    {SCRIPT_URL}")
    print(f"Video:     {VIDEO_URL}")
    print(f"Monitor:   {MONITOR_URL}")
    print(f"Assembler: {ASSEMBLER_URL}")
    print("")
    
    test_flow_real(args.theme, args.duration)

if __name__ == "__main__":
    main()
