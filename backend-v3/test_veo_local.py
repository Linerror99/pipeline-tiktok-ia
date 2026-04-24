"""
Test de génération vidéo Veo 3.1 — exécuté dans le conteneur backend-v3.
Usage : docker exec -it pipeline-tiktok-ia-backend-v3-1 python test_veo_local.py
"""
import asyncio
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Variables d'environnement pour Vertex AI
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "reetik-project")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")

TEST_VIDEO_ID = "test-veo-local-001"
TARGET_DURATION = 8  # 8s = 1 seule génération, pas d'extension


async def main():
    logger.info("=== Test Veo 3.1 local ===")
    logger.info(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    logger.info(f"GOOGLE_CLOUD_PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")

    # 1. Tester l'import du SDK
    try:
        from google import genai
        from google.genai.types import GenerateVideosConfig
        logger.info("✅ SDK google-genai importé")
    except ImportError as e:
        logger.error(f"❌ Import SDK échoué: {e}")
        sys.exit(1)

    # 2. Tester la connexion GCS (écriture d'un objet test)
    try:
        from google.cloud import storage
        client_gcs = storage.Client(project="reetik-project")
        bucket = client_gcs.bucket("reetik-v3-artifacts")
        # Vérifier l'accès en écriture (objectAdmin ne permet pas buckets.get)
        test_blob = bucket.blob("_preflight_test/ok.txt")
        test_blob.upload_from_string("ok")
        test_blob.delete()
        logger.info("✅ GCS connecté — écriture/suppression sur reetik-v3-artifacts OK")
    except Exception as e:
        logger.error(f"❌ GCS connection échouée: {e}")
        sys.exit(1)

    # 3. Tester Firestore
    try:
        from google.cloud import firestore
        db = firestore.Client(project="reetik-project", database="reetik-v3")
        # Simple ping
        db.collection("_test_ping").document("ping").set({"ts": "ok"})
        db.collection("_test_ping").document("ping").delete()
        logger.info("✅ Firestore reetik-v3 connecté")
    except Exception as e:
        logger.error(f"❌ Firestore connexion échouée: {e}")
        sys.exit(1)

    # 4. Tester l'appel Veo
    logger.info(f"\n🎬 Lancement génération Veo 3.1 (8s) — video_id={TEST_VIDEO_ID}")
    logger.info("   Prompt: 'A young hero standing at the edge of a cliff at sunset, cinematic, vertical 9:16'")
    logger.info("   Durée estimée: 3-5 minutes...\n")

    try:
        client = genai.Client()

        operation = client.models.generate_videos(
            model="veo-3.1-generate-001",
            prompt="A young hero standing at the edge of a cliff at sunset, cinematic, vertical 9:16",
            config=GenerateVideosConfig(
                aspect_ratio="9:16",
                output_gcs_uri=f"gs://reetik-v3-artifacts/{TEST_VIDEO_ID}/clip_0.mp4",
            ),
        )
        logger.info(f"✅ Opération lancée: {operation.name}")

        # Polling
        poll_count = 0
        while not operation.done:
            poll_count += 1
            logger.info(f"   ⏳ Poll #{poll_count} — en attente (15s)...")
            await asyncio.sleep(15)
            operation = client.operations.get(operation)
            logger.info(f"   done={operation.done}")

        logger.info(f"\n✅ Opération terminée après {poll_count * 15}s")

        # Vérifier le résultat
        if hasattr(operation, 'result') and operation.result:
            logger.info(f"   Résultat: {operation.result}")
        if hasattr(operation, 'error') and operation.error:
            logger.error(f"   Erreur Veo: {operation.error}")
            sys.exit(1)

        # Vérifier que le fichier existe dans GCS
        blob = bucket.blob(f"{TEST_VIDEO_ID}/clip_0.mp4")
        if blob.exists():
            blob.reload()
            logger.info(f"✅ Fichier GCS créé: gs://reetik-v3-artifacts/{TEST_VIDEO_ID}/clip_0.mp4")
            logger.info(f"   Taille: {blob.size / 1024 / 1024:.2f} MB")
        else:
            logger.warning("⚠️  Fichier GCS non trouvé (peut être dans un sous-chemin)")

    except Exception as e:
        logger.error(f"❌ Génération Veo échouée: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    logger.info("\n=== Test terminé avec succès ===")


if __name__ == "__main__":
    asyncio.run(main())
