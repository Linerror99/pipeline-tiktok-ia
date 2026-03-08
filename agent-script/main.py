import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage, firestore
import os
import json
import re
import math
import requests
from datetime import datetime

# --- Configuration ---
PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME_V2") or os.environ.get("BUCKET_NAME")
AGENT_VIDEO_URL = os.environ.get("AGENT_VIDEO_URL", "")

vertexai.init(project=PROJECT_ID, location=LOCATION)
storage_client = storage.Client()
firestore_client = firestore.Client()

@functions_framework.http
def generate_script(request):
    """
    Cloud Function HTTP qui génère un script vidéo V2 avec format BLOCS.
    Supporte durées variables (8s à 78s).
    """
    request_json = request.get_json(silent=True)
    if not request_json or "theme" not in request_json:
        return ("Le thème est manquant. Fournissez-le dans le corps JSON avec la clé 'theme'.", 400)
    
    theme = request_json["theme"]
    video_id = request_json.get("video_id", f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    target_duration = request_json.get("target_duration", 36)  # Défaut: 36s
    
    print(f"🎬 Thème: {theme} | Durée cible: {target_duration}s | Video ID: {video_id}")

    # Calculer nombre de blocs nécessaires
    target_blocks = calculate_blocks_count(target_duration)
    expected_duration = 8 if target_blocks == 1 else 8 + (target_blocks - 1) * 7
    
    print(f"📊 Blocs à générer: {target_blocks} (durée: {expected_duration}s)")
    
    model = GenerativeModel("gemini-3.1-pro-preview")
    
    # Nouveau prompt format BLOCS avec SAFETY GUIDELINES
    prompt = f"""
    Tu es un scénariste expert pour des vidéos TikTok virales.
    Ta tâche est de créer un script captivant sur le thème : "{theme}".

    FORMAT STRICT : {target_blocks} BLOCS
    - BLOC 1 : 8 secondes (premier bloc)
    - BLOCS 2 à {target_blocks} : 7 secondes chacun
    - Durée totale: {expected_duration} secondes

    Pour chaque bloc, utilise EXACTEMENT ce format :

    BLOC 1 (8s):
    DIALOGUE: "Texte exact que le narrateur va dire pendant ce bloc"
    VISUEL: Description détaillée de la scène visuelle pour une IA vidéo (décor, action, ambiance)

    BLOC 2 (7s):
    DIALOGUE: "Suite du texte parlé par le narrateur"
    VISUEL: Description de la suite visuelle

    [... jusqu'à BLOC {target_blocks}]

    RÈGLES IMPÉRATIVES :
    - Génère EXACTEMENT {target_blocks} blocs
    - Le DIALOGUE doit être parlé naturellement en {8 if target_blocks == 1 else '8 ou 7'}s selon le bloc
    - Le VISUEL doit décrire une scène cohérente avec le dialogue
    - Ton captivant et éducatif
    - Transitions fluides entre blocs
    - PAS d'astérisques ** dans le dialogue

    ⚠️ IMPORTANT - Respect des guidelines Vertex AI :
    - Les descriptions VISUEL doivent respecter les règles de sécurité de Google Vertex AI
    - Évite les contenus protégés par copyright (personnages de fiction, marques, logos)
    - Évite les contenus sensibles (violence, etc.)
    - OBLIGATOIRE : Scènes réalistes sans références copyrightées

    Génère maintenant le script pour : "{theme}"
    """

    print("🤖 Génération du script avec Gemini 2.5 Pro...")
    try:
        response = model.generate_content(prompt)
        script_content = response.text
    except Exception as e:
        print(f"❌ Erreur lors de l'appel à Gemini : {e}")
        update_firestore_status(video_id, "error", f"Erreur Gemini: {e}")
        return (f"Erreur interne lors de la génération du script : {e}", 500)

    # Parser le script au format BLOCS
    blocks = parse_blocks(script_content)
    
    if len(blocks) < target_blocks:
        print(f"⚠️ Seulement {len(blocks)} blocs générés sur {target_blocks} attendus. Régénération...")
        prompt_retry = prompt + f"\n\nATTENTION : Tu as généré seulement {len(blocks)} blocs. RÉGÉNÈRE avec EXACTEMENT {target_blocks} BLOCS."
        try:
            response = model.generate_content(prompt_retry)
            script_content = response.text
            blocks = parse_blocks(script_content)
            print(f"✅ Après régénération : {len(blocks)} blocs.")
        except Exception as e:
            print(f"❌ Erreur lors de la régénération : {e}")
    
    # Sauvegarder script en JSON structuré
    script_data = {
        "video_id": video_id,
        "theme": theme,
        "target_duration": target_duration,
        "actual_duration": expected_duration,
        "blocks": blocks,
        "total_blocks": len(blocks),
        "generated_at": datetime.now().isoformat(),
        "raw_script": script_content
    }
    
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        
        # JSON structuré
        json_blob = bucket.blob(f"{video_id}/script_v2.json")
        json_blob.upload_from_string(json.dumps(script_data, indent=2, ensure_ascii=False), content_type="application/json")
        
        # Texte brut pour backup
        txt_blob = bucket.blob(f"{video_id}/script_raw.txt")
        txt_blob.upload_from_string(script_content, content_type="text/plain")
        
        print(f"✅ Script sauvegardé dans gs://{BUCKET_NAME}/{video_id}/")
        print(f"📡 Upload script_v2.json déclenchera automatiquement agent-video-v2 (Cloud Storage trigger)")
        
        # Update Firestore status
        update_firestore_status(video_id, "script_generated", {
            "theme": theme,
            "blocks_count": len(blocks),
            "duration": expected_duration
        })
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde sur Cloud Storage : {e}")
        update_firestore_status(video_id, "error", f"Erreur sauvegarde: {e}")
        return (f"Erreur interne lors de la sauvegarde du fichier : {e}", 500)

    return {
        "status": "success",
        "video_id": video_id,
        "blocks_generated": len(blocks),
        "duration": expected_duration,
        "message": f"Script généré avec {len(blocks)} blocs ({expected_duration}s)"
    }, 200


# --- Fonctions Helper ---

def calculate_blocks_count(target_duration):
    """
    Calcule le nombre de blocs nécessaires pour une durée cible.
    
    Règle: 
    - 1 bloc = 8s
    - 2+ blocs = 8 + (n-1)*7 secondes
    
    Exemples:
    - 8s → 1 bloc
    - 15s → 2 blocs (8+7)
    - 36s → 5 blocs (8+7+7+7+7)
    - 78s → 11 blocs mais limité à 10
    """
    if target_duration <= 8:
        return 1
    
    # Pour durée > 8s, on calcule: 8 + (n-1)*7 = target
    # => (n-1)*7 = target - 8
    # => n = 1 + (target - 8) / 7
    blocks = 1 + math.ceil((target_duration - 8) / 7)
    
    # Limite à 10 blocs max (78s)
    return min(blocks, 10)


def parse_blocks(script_text):
    """
    Parse le script au format BLOCS.
    
    Format attendu:
    BLOC X (Ys):
    DIALOGUE: "texte parlé"
    VISUEL: description visuelle
    
    Accepte aussi format markdown avec **BLOC**, **DIALOGUE**, **VISUEL**
    """
    blocks = []
    
    # Nettoyer markdown (** autour des mots-clés)
    # Gemini génère souvent **BLOC 1**, **DIALOGUE:**, **VISUEL:**
    cleaned_text = script_text.replace('**BLOC', 'BLOC')
    cleaned_text = cleaned_text.replace('**DIALOGUE', 'DIALOGUE')
    cleaned_text = cleaned_text.replace('**VISUEL', 'VISUEL')
    cleaned_text = cleaned_text.replace(':**', ':')
    cleaned_text = cleaned_text.replace('**', '')  # Nettoyer ** restants
    
    # Regex pour extraire les blocs
    # Pattern: BLOC X ... DIALOGUE: ... VISUEL: ...
    bloc_pattern = r'BLOC\s+(\d+).*?DIALOGUE:\s*["\']?(.+?)["\']?\s*VISUEL:\s*(.+?)(?=(?:BLOC\s+\d+)|$)'
    
    matches = re.finditer(bloc_pattern, cleaned_text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        bloc_num = int(match.group(1))
        dialogue = match.group(2).strip()
        visuel = match.group(3).strip()
        
        # Nettoyer les guillemets et astérisques
        dialogue = dialogue.replace('**', '').strip()
        visuel = visuel.replace('**', '').strip()
        
        blocks.append({
            "bloc": bloc_num,
            "dialogue": dialogue,
            "visuel": visuel,
            "duration": 8 if bloc_num == 1 else 7
        })
    
    # Trier par numéro de bloc
    blocks.sort(key=lambda x: x['bloc'])
    
    print(f"📝 Parsed {len(blocks)} blocs du script")
    for block in blocks:
        print(f"  - Bloc {block['bloc']}: {len(block['dialogue'])} chars dialogue, {block['duration']}s")
    
    return blocks


def update_firestore_status(video_id, status, details=None):
    """Met à jour le statut dans Firestore v2_video_status."""
    try:
        doc_ref = firestore_client.collection('v2_video_status').document(video_id)
        
        update_data = {
            "status": status,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        if details:
            if isinstance(details, dict):
                update_data.update(details)
            else:
                update_data["details"] = str(details)
        
        doc_ref.set(update_data, merge=True)
        print(f"🔄 Firestore updated: {video_id} → {status}")
        
    except Exception as e:
        print(f"⚠️ Erreur update Firestore: {e}")