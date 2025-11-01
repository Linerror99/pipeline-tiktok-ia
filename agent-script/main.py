import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import os

# --- Configuration ---
PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME")

vertexai.init(project=PROJECT_ID, location=LOCATION)
storage_client = storage.Client()

@functions_framework.http
def generate_script(request):
    """
    Cloud Function HTTP qui génère un script vidéo à partir d'un thème.
    """
    request_json = request.get_json(silent=True)
    if not request_json or "theme" not in request_json:
        return ("Le thème est manquant. Fournissez-le dans le corps JSON avec la clé 'theme'.", 400)
    
    theme = request_json["theme"]
    print(f"Thème reçu : {theme}")

    model = GenerativeModel("gemini-2.5-pro")
    
    # MODIFICATION : Prompt avec contrainte de 8 scènes MINIMUM
    prompt = f"""
    Tu es un scénariste expert pour des vidéos TikTok virales.
    Ta tâche est de créer un script captivant et détaillé sur le thème suivant : "{theme}".

    Le script doit respecter les contraintes STRICTES suivantes :
    - Le script DOIT contenir AU MINIMUM 8 scènes (IMPÉRATIF pour atteindre 64+ secondes de vidéo).
    - Chaque scène dure environ 8 secondes de vidéo.
    - La durée totale de la narration (la somme de toutes les "VOIX OFF") doit être comprise entre 64 et 90 secondes.
    - Le ton doit être intrigant et éducatif.
    - Structure le script en scènes claires, avec des descriptions de visuels et le texte de la voix off.
    
    Pour chaque scène, utilise EXACTEMENT ce format :
      **VISUEL:** brève description pour une IA vidéo.
      **VOIX OFF:** texte exact à lire (SANS astérisques ** dans le texte).

    IMPORTANT : 
    - NE PAS mettre d'astérisques ** dans le texte de la VOIX OFF
    - Générer AU MINIMUM 8 scènes
    - Le texte VOIX OFF doit être naturel et fluide

    Génère maintenant le script pour le thème : "{theme}"
    """

    print("Génération du script avec Gemini 2.5 Pro...")
    try:
        response = model.generate_content(prompt)
        script_content = response.text
    except Exception as e:
        print(f"Erreur lors de l'appel à Gemini : {e}")
        return (f"Erreur interne lors de la génération du script : {e}", 500)

    # AJOUT : Vérification du nombre de scènes
    scene_count = script_content.upper().count("VISUEL")
    print(f"Script généré avec {scene_count} scènes.")
    
    if scene_count < 8:
        print(f"⚠️ Seulement {scene_count} scènes. Régénération...")
        prompt_retry = prompt + f"\n\nATTENTION : Tu as généré seulement {scene_count} scènes. RÉGÉNÈRE avec AU MOINS 8 SCÈNES."
        try:
            response = model.generate_content(prompt_retry)
            script_content = response.text
            scene_count = script_content.upper().count("VISUEL")
            print(f"Après régénération : {scene_count} scènes.")
        except Exception as e:
            print(f"Erreur lors de la régénération : {e}")
    
    file_name = f"script_{theme.lower().replace(' ', '_')[:30]}.txt"
    
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_name)
        blob.upload_from_string(script_content, content_type="text/plain")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde sur Cloud Storage : {e}")
        return (f"Erreur interne lors de la sauvegarde du fichier : {e}", 500)

    print(f"Script sauvegardé dans gs://{BUCKET_NAME}/{file_name}")

    return (f"Script généré avec {scene_count} scènes et sauvegardé : {file_name}", 200)