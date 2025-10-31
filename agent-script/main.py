import functions_framework
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
import os

# --- Configuration ---
PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = "us-central1"  # Région compatible avec les modèles Gemini récents
BUCKET_NAME = os.environ.get("BUCKET_NAME")

# Initialisation des clients GCP
vertexai.init(project=PROJECT_ID, location=LOCATION)
storage_client = storage.Client()

@functions_framework.http
def generate_script(request):
    """
    Cloud Function HTTP qui génère un script vidéo à partir d'un thème.
    """
    # 1. Récupérer le thème depuis la requête
    request_json = request.get_json(silent=True)
    if not request_json or "theme" not in request_json:
        return ("Le thème est manquant. Fournissez-le dans le corps JSON avec la clé 'theme'.", 400)
    
    theme = request_json["theme"]
    print(f"Thème reçu : {theme}")

    # 2. Construire le prompt pour Gemini (modèle mis à jour)
    # Utilisation du modèle que vous avez fourni : gemini-2.5-pro
    model = GenerativeModel("gemini-2.5-pro")
    
    prompt = f"""
    Tu es un scénariste expert pour des vidéos TikTok virales.
    Ta tâche est de créer un script captivant et détaillé sur le thème suivant : "{theme}".

    Le script doit respecter les contraintes STRICTES suivantes :
    - La durée totale de la narration (la somme de toutes les "VOIX OFF") doit être comprise entre 70 et 85 secondes. C'est une contrainte impérative pour la monétisation et la rétention d'audience.
    - Le ton doit être intrigant et éducatif.
    - Structure le script en scènes claires, avec des descriptions de visuels et le texte de la voix off.
    - Pour chaque scène, utilise le format :
      **VISUEL:** brève description pour une IA vidéo.
      **VOIX OFF:** texte exact à lire.

    Génère maintenant le script pour le thème : "{theme}"
    """

    # 3. Appeler l'API Gemini
    print("Génération du script avec Gemini 2.5 Pro...")
    try:
        response = model.generate_content(prompt)
        script_content = response.text
    except Exception as e:
        print(f"Erreur lors de l'appel à Gemini : {e}")
        return (f"Erreur interne lors de la génération du script : {e}", 500)

    print("Script généré avec succès.")
    
    # 4. Sauvegarder le script dans Cloud Storage
    file_name = f"script_{theme.lower().replace(' ', '_')[:30]}.txt"
    
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file_name)
        blob.upload_from_string(script_content, content_type="text/plain")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde sur Cloud Storage : {e}")
        return (f"Erreur interne lors de la sauvegarde du fichier : {e}", 500)

    print(f"Script sauvegardé dans gs://{BUCKET_NAME}/{file_name}")

    # 5. Renvoyer une réponse de succès
    return (f"Script généré et sauvegardé avec succès sous le nom : {file_name}", 200)