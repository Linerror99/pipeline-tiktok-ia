# 🎬 Fix Veo 3.1 Extensions - Spécification Technique

## Problème Actuel (V2.1)

L'agent-video actuel (`agent-video/main.py`) génère **N clips de 8s en parallèle**, chacun indépendant :

```python
# ❌ PROBLÈME : agent-video/main.py (V2.1)
for idx, block_data in enumerate(blocks, start=1):
    operation = genai_client.models.generate_videos(
        model="veo-3.1-generate-001",
        prompt=full_prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            resolution="720p",
            duration_seconds=8,         # Toujours 8s
            person_generation="allow_all"
        )
    )
    operations[idx] = operation.name    # Clip indépendant
```

**Résultat** : 8 clips de 8s assemblés par FFmpeg → **coupures audio**, pas de fluidité, chaque clip a sa propre bande son.

---

## Solution : Extensions Veo 3.1

Veo 3.1 GA (`veo-3.1-generate-001`) supporte les extensions vidéo :
- 1 vidéo initiale de **8s** avec audio natif
- Jusqu'à **7 extensions de 7s** chacune
- Audio **continu** sur toute la durée
- Cohérence visuelle maintenue entre segments

### Paliers de Durée

```
8s  = 1 génération initiale (0 extensions)
15s = 8s + 1×7s (1 extension)
22s = 8s + 2×7s (2 extensions)
29s = 8s + 3×7s (3 extensions)
36s = 8s + 4×7s (4 extensions)
43s = 8s + 5×7s (5 extensions)
50s = 8s + 6×7s (6 extensions)
57s = 8s + 7×7s (7 extensions) ← MAXIMUM
```

---

## Nouveau Agent : `agent-video-veo31/`

### `agent-video-veo31/main.py`

```python
import functions_framework
from google.cloud import storage, firestore
from google import genai
from google.genai import types
import os
import json
import time
from datetime import datetime

storage_client = storage.Client()
firestore_client = firestore.Client()

PROJECT_ID = os.environ.get("GCP_PROJECT", "reetik-project")
LOCATION = "us-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME_V3")

genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# Durées supportées : 8s initial + N×7s extensions
VALID_DURATIONS = [8, 15, 22, 29, 36, 43, 50, 57]


def calculate_extensions(target_duration: int) -> int:
    """Calcule le nombre d'extensions nécessaires."""
    if target_duration <= 8:
        return 0
    return min((target_duration - 8) // 7, 7)


def snap_to_valid_duration(target_duration: int) -> int:
    """Arrondit à la durée valide la plus proche."""
    for d in VALID_DURATIONS:
        if target_duration <= d:
            return d
    return 57  # Max


@functions_framework.cloud_event
def generate_video_veo31(cloudevent):
    """
    Cloud Function V3 : Génère une vidéo continue Veo 3.1 avec extensions.
    
    Déclenchée par upload de script_v3.json dans le bucket V3.
    Produit UNE SEULE vidéo avec audio natif continu.
    """
    try:
        data = cloudevent.data
        bucket_name = data["bucket"]
        file_name = data["name"]

        if not file_name.endswith("/script_v3.json"):
            return "OK"

        video_id = file_name.split("/")[0]
        print(f"🎬 [V3] Génération Veo 3.1 pour video_id: {video_id}")

    except Exception as e:
        print(f"❌ Erreur parsing CloudEvent: {e}")
        return "ERROR"

    try:
        # 1. Charger script V3
        bucket = storage_client.bucket(BUCKET_NAME)
        script_blob = bucket.blob(f"{video_id}/script_v3.json")

        if not script_blob.exists():
            print(f"❌ Script {video_id}/script_v3.json non trouvé")
            return "ERROR"

        script_data = json.loads(script_blob.download_as_text())
        blocks = script_data.get("blocks", [])
        target_duration = script_data.get("target_duration", 8)
        character_refs = script_data.get("character_references", [])

        actual_duration = snap_to_valid_duration(target_duration)
        num_extensions = calculate_extensions(actual_duration)

        print(f"📊 Blocs: {len(blocks)}, Durée cible: {actual_duration}s, Extensions: {num_extensions}")

        # Update Firestore status
        firestore_client.collection("videos_v3").document(video_id).update({
            "status": "generating",
            "target_duration": actual_duration,
            "extensions_planned": num_extensions,
            "updated_at": firestore.SERVER_TIMESTAMP
        })

        # 2. Générer vidéo initiale (8s)
        block_1 = blocks[0]
        initial_prompt = build_prompt(block_1, character_refs, is_initial=True)

        print(f"🎥 BLOC 1/{ 1 + num_extensions} - Vidéo initiale 8s")
        print(f"   Prompt: {initial_prompt[:100]}...")

        initial_operation = genai_client.models.generate_videos(
            model="veo-3.1-generate-001",
            prompt=initial_prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16",
                resolution="720p",
                duration_seconds=8,
                person_generation="allow_all"
            )
        )

        print(f"   ✅ Opération initiale lancée: {initial_operation.name[:60]}...")

        # Stocker opération dans Firestore pour monitoring
        firestore_client.collection("v3_veo_operations").document(video_id).set({
            "video_id": video_id,
            "status": "generating_initial",
            "initial_operation": initial_operation.name,
            "extensions_operations": [],
            "total_extensions": num_extensions,
            "completed_extensions": 0,
            "blocks": blocks,
            "character_references": character_refs,
            "target_duration": actual_duration,
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        })

        print(f"✅ Génération V3 lancée - {actual_duration}s ({num_extensions} extensions à suivre)")
        return "OK"

    except Exception as e:
        print(f"❌ Erreur génération V3: {e}")
        firestore_client.collection("videos_v3").document(video_id).update({
            "status": "failed",
            "error": str(e),
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        return "ERROR"


def build_prompt(block_data: dict, character_refs: list, is_initial: bool = True) -> str:
    """Construit le prompt Veo 3.1 avec références personnages."""
    visual = block_data.get("visuel", "")
    dialogue = block_data.get("dialogue", "")

    prompt = visual
    if dialogue:
        prompt += f"\n\nDialogue à générer en audio: \"{dialogue}\""

    if not is_initial:
        prompt = f"Suite de la scène précédente. {prompt}"

    return prompt
```

### `agent-video-veo31/monitor_extensions.py`

Ce module est appelé périodiquement (Cloud Scheduler) pour :
1. Vérifier si la vidéo initiale est terminée
2. Lancer les extensions séquentiellement
3. Uploader la vidéo finale

```python
def check_and_extend(video_id: str):
    """
    Vérifie l'opération en cours et lance l'extension suivante si prête.
    Appelé par Cloud Scheduler toutes les 30s.
    """
    doc = firestore_client.collection("v3_veo_operations").document(video_id).get()
    if not doc.exists:
        return

    data = doc.to_dict()
    status = data["status"]
    total_ext = data["total_extensions"]
    completed_ext = data["completed_extensions"]

    if status == "generating_initial":
        # Vérifier si vidéo initiale terminée
        op_name = data["initial_operation"]
        operation = genai_client.models._get_operation(op_name)

        if operation.done:
            if operation.error:
                mark_failed(video_id, f"Vidéo initiale échouée: {operation.error}")
                return

            # Récupérer la vidéo générée
            initial_video = operation.result
            video_data = download_generated_video(initial_video)

            if total_ext == 0:
                # Pas d'extensions → vidéo finale
                upload_final_video(video_id, video_data)
                return

            # Sauvegarder vidéo intermédiaire et lancer extension 1
            save_intermediate(video_id, video_data, 0)
            launch_extension(video_id, data, 1, video_data)

    elif status.startswith("extending_"):
        # Vérifier extension en cours
        ext_ops = data["extensions_operations"]
        current_op = ext_ops[-1]
        operation = genai_client.models._get_operation(current_op)

        if operation.done:
            if operation.error:
                # Retry cette extension
                retry_extension(video_id, data, completed_ext + 1)
                return

            extended_video = operation.result
            video_data = download_generated_video(extended_video)

            new_completed = completed_ext + 1

            if new_completed >= total_ext:
                # Toutes les extensions terminées → vidéo finale
                upload_final_video(video_id, video_data)
            else:
                # Lancer extension suivante
                save_intermediate(video_id, video_data, new_completed)
                launch_extension(video_id, data, new_completed + 1, video_data)


def launch_extension(video_id: str, data: dict, ext_number: int, base_video):
    """Lance une extension Veo 3.1 (7s supplémentaires)."""
    blocks = data["blocks"]
    character_refs = data.get("character_references", [])

    block_index = min(ext_number, len(blocks) - 1)
    block = blocks[block_index]
    prompt = build_prompt(block, character_refs, is_initial=False)

    print(f"🔄 Extension {ext_number}/{data['total_extensions']} pour {video_id}")

    operation = genai_client.models.extend_video(
        model="veo-3.1-generate-001",
        base_video=base_video,
        prompt=prompt,
        config=types.ExtendVideoConfig(
            duration_seconds=7
        )
    )

    # Update Firestore
    firestore_client.collection("v3_veo_operations").document(video_id).update({
        "status": f"extending_{ext_number}",
        "extensions_operations": firestore.ArrayUnion([operation.name]),
        "completed_extensions": ext_number - 1,
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    print(f"   ✅ Extension {ext_number} lancée: {operation.name[:60]}...")


def upload_final_video(video_id: str, video_data: bytes):
    """Upload la vidéo finale dans Cloud Storage."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{video_id}/final.mp4")
    blob.upload_from_string(video_data, content_type="video/mp4")

    video_url = f"gs://{BUCKET_NAME}/{video_id}/final.mp4"

    # Update Firestore
    firestore_client.collection("videos_v3").document(video_id).update({
        "status": "completed",
        "video_url": video_url,
        "has_native_audio": True,
        "generation_completed_at": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    firestore_client.collection("v3_veo_operations").document(video_id).update({
        "status": "completed",
        "updated_at": firestore.SERVER_TIMESTAMP
    })

    print(f"✅ Vidéo finale uploadée: {video_url}")

    # Envoyer notification (sera implémenté)
    # send_email_notification(video_id)
```

### `agent-video-veo31/requirements.txt`

```
functions-framework==3.*
google-cloud-storage>=2.14.0
google-cloud-firestore>=2.14.0
google-genai>=1.0.0
```

---

## 🧪 Tests

### `tests/unit/test_veo31_extensions.py`

```python
"""
Tests unitaires pour le système d'extensions Veo 3.1.
Teste la logique SANS appeler l'API (mock).
"""
import pytest
from unittest.mock import MagicMock, patch


def test_calculate_extensions():
    """Vérifier le calcul du nombre d'extensions."""
    from agent_video_veo31.main import calculate_extensions

    assert calculate_extensions(8) == 0    # 8s = pas d'extension
    assert calculate_extensions(15) == 1   # 8 + 1×7 = 15
    assert calculate_extensions(22) == 2   # 8 + 2×7 = 22
    assert calculate_extensions(29) == 3   # 8 + 3×7 = 29
    assert calculate_extensions(36) == 4   # 8 + 4×7 = 36
    assert calculate_extensions(57) == 7   # 8 + 7×7 = 57 (max)
    assert calculate_extensions(100) == 7  # Capped à 7


def test_snap_to_valid_duration():
    """Vérifier l'arrondi aux durées valides."""
    from agent_video_veo31.main import snap_to_valid_duration

    assert snap_to_valid_duration(5) == 8
    assert snap_to_valid_duration(8) == 8
    assert snap_to_valid_duration(10) == 15
    assert snap_to_valid_duration(15) == 15
    assert snap_to_valid_duration(20) == 22
    assert snap_to_valid_duration(25) == 29
    assert snap_to_valid_duration(100) == 57  # Max


def test_build_prompt_initial():
    """Tester construction prompt pour vidéo initiale."""
    from agent_video_veo31.main import build_prompt

    block = {
        "visuel": "Un stade de football éclairé la nuit",
        "dialogue": "Bienvenue dans le top 5 des buts !"
    }

    prompt = build_prompt(block, [], is_initial=True)

    assert "Un stade de football" in prompt
    assert "Bienvenue dans le top 5" in prompt
    assert "Suite de la scène" not in prompt


def test_build_prompt_extension():
    """Tester construction prompt pour extension."""
    from agent_video_veo31.main import build_prompt

    block = {
        "visuel": "Le ballon entre dans le filet",
        "dialogue": "Et c'est le but !"
    }

    prompt = build_prompt(block, [], is_initial=False)

    assert "Suite de la scène précédente" in prompt
    assert "Le ballon entre" in prompt


def test_valid_durations_list():
    """Vérifier que tous les paliers sont cohérents."""
    from agent_video_veo31.main import VALID_DURATIONS

    assert VALID_DURATIONS == [8, 15, 22, 29, 36, 43, 50, 57]

    # Vérifier la formule : 8 + N×7
    for i, d in enumerate(VALID_DURATIONS):
        assert d == 8 + i * 7
```

### Test d'Intégration (avec vraie API Veo 3.1)

```python
"""
Test d'intégration RÉEL avec Veo 3.1 API.
⚠️ COÛTEUX - Ne pas exécuter en CI/CD.
Exécuter manuellement : pytest tests/integration/test_veo31_real.py -v
"""
import pytest
from google import genai
from google.genai import types
import os


PROJECT_ID = os.environ.get("GCP_PROJECT", "reetik-project")
LOCATION = "us-central1"

client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)


@pytest.mark.integration
@pytest.mark.expensive
def test_veo31_generate_8s():
    """Test : Générer 1 vidéo de 8s."""
    operation = client.models.generate_videos(
        model="veo-3.1-generate-001",
        prompt="A colorful abstract animation with geometric shapes moving smoothly",
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            resolution="720p",
            duration_seconds=8,
            person_generation="allow_all"
        )
    )

    assert operation.name is not None
    print(f"✅ Opération 8s lancée: {operation.name}")

    # Attendre résultat (timeout 5 min)
    result = operation.result(timeout=300)
    assert result is not None
    print(f"✅ Vidéo 8s générée avec succès")


@pytest.mark.integration
@pytest.mark.expensive
def test_veo31_generate_15s_with_extension():
    """Test : Générer 8s + 1 extension 7s = 15s."""
    # 1. Vidéo initiale 8s
    initial_op = client.models.generate_videos(
        model="veo-3.1-generate-001",
        prompt="A calm ocean wave at sunset with ambient sound",
        config=types.GenerateVideosConfig(
            aspect_ratio="9:16",
            resolution="720p",
            duration_seconds=8,
            person_generation="allow_all"
        )
    )

    initial_result = initial_op.result(timeout=300)
    assert initial_result is not None
    print(f"✅ Vidéo initiale 8s OK")

    # 2. Extension 7s
    extend_op = client.models.extend_video(
        model="veo-3.1-generate-001",
        base_video=initial_result,
        prompt="The wave crashes gently on a sandy beach",
        config=types.ExtendVideoConfig(
            duration_seconds=7
        )
    )

    extended_result = extend_op.result(timeout=300)
    assert extended_result is not None
    print(f"✅ Extension 7s OK - Vidéo totale: 15s")
```

---

## 📋 Changements agent-assembler (V3)

En V3, l'assembler est **simplifié** : il reçoit **1 seule vidéo** (déjà complète avec audio natif) au lieu de 8 clips à assembler.

### V2.1 (actuel) : assembler combine N clips
```
clip_1.mp4 + clip_2.mp4 + ... + clip_8.mp4 + audio.mp3 → ffmpeg concat → final.mp4
```

### V3 (nouveau) : assembler ajoute juste les sous-titres
```
final_veo31.mp4 (audio natif inclus) → whisper → sous-titres ASS → ffmpeg overlay → final_with_subs.mp4
```

L'assembler V3 :
1. Télécharge la vidéo unique depuis Storage
2. Exécute Whisper pour transcription
3. Génère les sous-titres ASS
4. Overlay les sous-titres avec FFmpeg
5. Upload la vidéo finale avec sous-titres

---

## ⚠️ Points d'Attention

### 1. API Extensions Veo 3.1
L'API `extend_video` est en preview. Vérifier la documentation exacte Vertex AI avant implémentation. Les noms de méthodes peuvent différer.

### 2. Extensions Séquentielles
Les extensions DOIVENT être séquentielles (chaque extension prend la vidéo précédente en entrée). Pas de parallélisation possible ici.

### 3. Coûts
- Chaque extension = même coût qu'une génération initiale (~$0.80)
- Vidéo 57s = 1 initial + 7 extensions = 8 × $0.80 = **~$6.40**
- Pour les tests, utiliser `veo-3.1-fast-generate-001` (moins cher, plus rapide)

### 4. Timeouts
- Vidéo initiale : ~30-60s
- Chaque extension : ~30-60s
- Vidéo 57s : ~4-8 min au total
- Prévoir timeout Cloud Function >= 540s (9 min)

### 5. Retry
Si une extension échoue, on peut retenter depuis le dernier checkpoint (vidéo intermédiaire sauvegardée).
