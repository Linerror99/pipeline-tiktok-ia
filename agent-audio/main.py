import functions_framework
from google.cloud import storage
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
    
    # --- CORRECTION ULTIME : Logique insensible aux espaces et variations ---
    for line in script_content.splitlines():
        # 1. On met en majuscules et on enlève les espaces superflus
        cleaned_line = line.strip().upper()
        
        # 2. On ignore les lignes qui ne sont pas de la narration
        if "VISUEL" in cleaned_line or "SCÈNE" in cleaned_line or "DURÉE" in cleaned_line:
            continue

        # 3. On cherche la balise "VOIX OFF" (sans les deux-points)
        voix_off_marker = "VOIX OFF"
        marker_pos = cleaned_line.find(voix_off_marker)
        
        if marker_pos != -1:
            # On cherche la position des deux-points après la balise
            colon_pos = cleaned_line.find(":", marker_pos)
            if colon_pos != -1:
                # On extrait le texte original (avec casse) après les deux-points
                original_line = line.strip()
                text_part = original_line[colon_pos + 1:]
                narration_text += text_part.strip() + " "

    if not narration_text.strip():
        print("Aucun texte de narration n'a pu être extrait. Arrêt.")
        return "OK"

    print(f"Génération de l'audio avec la voix Gemini 'Rasalgethi'...")

    # Le reste du code est identique et correct
    input_text = texttospeech.SynthesisInput(text=narration_text)

    try:
        response = tts_client.synthesize_speech(
            input=input_text,
            voice=texttospeech.VoiceSelectionParams(
                language_code="fr-fr", name="Rasalgethi", model_name="gemini-2.5-pro-tts"
            ),
            audio_config=texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=1.0, pitch=0
            )
        )
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Text-to-Speech : {e}")
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