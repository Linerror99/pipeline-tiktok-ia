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

    # MODIFICATION : Compter les scènes
    scene_count = script_content.upper().count("VISUEL")
    print(f"Nombre de scènes détectées : {scene_count}")

    narration_text = ""
    
    for line in script_content.splitlines():
        cleaned_line = line.strip().upper()
        
        if "VISUEL" in cleaned_line or "SCÈNE" in cleaned_line or "DURÉE" in cleaned_line:
            continue

        voix_off_marker = "VOIX OFF"
        marker_pos = cleaned_line.find(voix_off_marker)
        
        if marker_pos != -1:
            colon_pos = cleaned_line.find(":", marker_pos)
            if colon_pos != -1:
                original_line = line.strip()
                text_part = original_line[colon_pos + 1:]
                
                # AJOUT : Nettoyage des astérisques et autres marqueurs
                text_part = text_part.replace('**', '')  # Enlever gras
                text_part = text_part.replace('*', '')   # Enlever italique
                text_part = text_part.strip()
                
                narration_text += text_part + " "

    if not narration_text.strip():
        print("Aucun texte de narration n'a pu être extrait. Arrêt.")
        return "OK"

    # AJOUT : Calcul durée cible et ajustement vitesse
    target_duration = scene_count * 8  # 8 secondes par scène
    print(f"Durée cible audio : {target_duration} secondes ({scene_count} scènes × 8s)")
    
    word_count = len(narration_text.split())
    estimated_duration = word_count / 2.5  # ~2.5 mots/seconde en vitesse normale
    
    # Calculer le ratio de vitesse pour atteindre la durée cible
    if estimated_duration > 0:
        speed_ratio = estimated_duration / target_duration
        # Limiter entre 0.8 et 1.2 pour rester naturel
        speed_ratio = max(0.8, min(1.2, speed_ratio))
    else:
        speed_ratio = 1.0
    
    print(f"Mots : {word_count}, Durée estimée : {estimated_duration:.1f}s, Ratio vitesse : {speed_ratio:.2f}x")
    
    print(f"Génération de l'audio avec la voix Gemini 'Rasalgethi'...")

    input_text = texttospeech.SynthesisInput(text=narration_text)

    try:
        response = tts_client.synthesize_speech(
            input=input_text,
            voice=texttospeech.VoiceSelectionParams(
                language_code="fr-fr", 
                name="Rasalgethi", 
                model_name="gemini-2.5-pro-tts"
            ),
            audio_config=texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3, 
                speaking_rate=speed_ratio,  # MODIFIÉ : vitesse ajustée
                pitch=0
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
    print(f"✅ Audio ajusté pour {scene_count} scènes (~{target_duration}s)")
    return "OK"