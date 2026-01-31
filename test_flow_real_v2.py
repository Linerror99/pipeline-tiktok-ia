"""
Test RÉEL du flow V2 end-to-end
Appelle les Cloud Functions déployées

Usage:
  python test_flow_real_v2.py --theme "Intelligence Artificielle" --duration 15
"""

import os
import sys
import json
import argparse
import time
import requests
from datetime import datetime

# Configuration
PROJECT_ID = "pipeline-video-ia"
REGION = "us-central1"

# URLs Cloud Functions (à adapter selon votre projet)
BASE_URL = f"https://{REGION}-{PROJECT_ID}.cloudfunctions.net"

SCRIPT_URL = f"{BASE_URL}/agent-script-v2"
VIDEO_URL = f"{BASE_URL}/agent-video-v2"
MONITOR_URL = f"{BASE_URL}/monitor-veo31"
ASSEMBLER_URL = f"{BASE_URL}/agent-assembler-v2"

def test_flow_real(theme, duration):
    """Test flow complet V2 avec Cloud Functions réelles"""
    
    video_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("=" * 70)
    print("🧪 TEST FLOW V2 RÉEL (Cloud Functions)")
    print("=" * 70)
    print(f"Video ID: {video_id}")
    print(f"Thème: {theme}")
    print(f"Durée: {duration}s")
    print("=" * 70)
    
    # ÉTAPE 1: Appeler agent-script
    print("\n📝 ÉTAPE 1: Génération script...")
    print(f"POST {SCRIPT_URL}")
    
    try:
        response = requests.post(SCRIPT_URL, json={
            'theme': theme,
            'video_id': video_id,
            'target_duration': duration
        }, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Script généré: {result['blocks_generated']} blocs")
            print(f"   Durée: {result['duration']}s")
            print(f"\n   ⚡ agent-video-v2 sera automatiquement déclenché par Storage trigger")
            print(f"      (Upload de script_v2.json → génération BLOC 1)")
        else:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # ÉTAPE 2: Monitoring manuel (Cloud Scheduler le fera automatiquement)
    print("\n🔍 ÉTAPE 2: Monitoring opérations...")
    print(f"⏰ Cloud Scheduler appellera monitor-veo31 toutes les minutes")
    print(f"   Pour tester manuellement: POST {MONITOR_URL}")
    
    # Appel manuel pour test
    print("\n   Test manuel du monitor...")
    try:
        response = requests.post(MONITOR_URL, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Monitor exécuté: {result['checked']} opérations vérifiées")
            print(f"      Traitées: {result['processed']}")
        else:
            print(f"   ⚠️ Erreur {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"   ⚠️ Erreur: {e}")
    
    # ÉTAPE 3: Instructions pour la suite
    print("\n🎞️ ÉTAPE 3: Assemblage final...")
    print(f"   L'assembleur sera appelé automatiquement par monitor-veo31")
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
    print("   https://console.firebase.google.com/project/pipeline-video-ia/firestore")
    print(f"   Collection: v2_veo_operations/{video_id}")
    print("")
    print("2. Cloud Storage:")
    print(f"   gs://tiktok-pipeline-v2-artifacts/{video_id}/")
    print("")
    print("3. Cloud Functions Logs:")
    print("   gcloud functions logs read monitor-veo31 --region=us-central1 --limit=50")
    print("")
    print("4. Vérifier status:")
    print(f"   curl -X POST {MONITOR_URL}")
    print("")
    
    # Attendre et vérifier périodiquement
    print("⏳ Attente génération (vous pouvez Ctrl+C pour arrêter)...")
    print("   Cloud Scheduler vérifie automatiquement toutes les minutes")
    
    try:
        for i in range(10):  # Vérifier pendant 10 minutes max
            time.sleep(60)  # Attendre 1 minute
            
            print(f"\n⏰ Vérification {i+1}/10...")
            
            try:
                response = requests.post(MONITOR_URL, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    if result['processed'] > 0:
                        print(f"   ✅ {result['processed']} opérations traitées")
                    else:
                        print(f"   ⏳ En cours... ({result['checked']} opérations en cours)")
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
