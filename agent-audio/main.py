import functions_framework
from google.cloud import storage
# On importe bien la v1beta1, c'est crucial
from google.cloud import texttospeech_v1beta1 as texttospeech
import re

storage_client = storage.Client()
tts_client = texttospeech.TextToSpeechClient()

@functions_framework.cloud_event
def generate_audio(cloudevent):
    data = cloudevent.data
    bucket_name = data["bucket"]
    file_name = data["name"]

    print(f"Déclencheur reçu pour le fichier : {file_name}")

    if not file_name.startswith("script_") or not file_name.endswith(".txt"):
        print(f"Fichier non-script {file_name}. Traitement ignoré.")
        return "OK"

    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        script_content = blob.download_as_text(encoding="utf-8")
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {file_name} : {e}")
        return

    print("Contenu du script lu avec succès.")

    narration_text = ""
    script_started = False
    
    for line in script_content.splitlines():
        cleaned_line = line.strip().replace('*', '').replace('#', '')
        if not cleaned_line: continue
        if not script_started:
            if cleaned_line.upper().startswith(("(SCÈNE", "[SCÈNE")):
                script_started = True
            else:
                continue
        line_upper = cleaned_line.upper()
        if any(keyword in line_upper for keyword in ["(SCÈNE", "[SCÈNE", "VISUEL:", "TITRE:", "MUSIQUE:"]): continue
        if line_upper.startswith("VOIX OFF:"):
            narration_text += cleaned_line[9:].strip() + " "

    if not narration_text.strip():
        print("Aucun texte de narration n'a pu être extrait. Arrêt.")
        return "OK"

    print(f"Génération de l'audio avec la voix Gemini 'Rasalgethi'...")

    input_text = texttospeech.SynthesisInput(text=narration_text)

    # --- CORRECTION FINALE : Reproduction exacte de votre JSON ---
    voice = texttospeech.VoiceSelectionParams(
        language_code="fr-fr",  # Votre format
        name="Rasalgethi",      # Votre format
        # On ne met PAS modelName ici
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, # On garde MP3 pour la taille
        speaking_rate=1.0,
        pitch=0
    )

    # On construit la requête avec le paramètre `model_name` dans `voice`
    # La bibliothèque Python mappe `modelName` à `model_name`
    try:
        response = tts_client.synthesize_speech(
            input=input_text,
            voice=texttospeech.VoiceSelectionParams(
                language_code="fr-fr",
                name="Rasalgethi",
                model_name="gemini-2.5-pro-tts" # Le paramètre est ici
            ),
            audio_config=audio_config
        )
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Text-to-Speech : {e}")
        # On ajoute plus de détails sur l'erreur pour le débogage
        import traceback
        traceback.print_exc()
        return

    print("Audio généré avec succès.")

    output_audio_filename = file_name.replace("script_", "audio_").replace(".txt", ".mp3")
    try:
        audio_blob = bucket.blob(output_audio_filename)
        audio_blob.upload_from_string(response.audio_content, content_type="audio/mpeg")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du fichier audio : {e}")
        return

    print(f"Fichier audio sauvegardé : {output_audio_filename}")
    return "OK"