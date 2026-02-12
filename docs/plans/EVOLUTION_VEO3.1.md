# 🎯 ANALYSE VEO 3.1 - RÉVOLUTION POUR TON PIPELINE ! 

---

## 🔥 **CE QUE VEO 3.1 APPORTE**

### ✅ **1. AUDIO NATIF INTÉGRÉ**
```python
# ✅ Veo 3.1 génère AUDIO + VIDÉO ensemble ! 
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="""A close up of two people staring at a cryptic drawing on a wall.
    A man murmurs, 'This must be it.  That's the secret code.' 
    The woman looks at him whispering excitedly, 'What did you find?'"""
)

# La vidéo générée CONTIENT DÉJÀ L'AUDIO (dialogues + effets sonores)
```

**🎉 FINI LES PROBLÈMES DE SYNCHRONISATION !**
- Audio ET vidéo générés **ensemble** par Veo
- Plus besoin de Google TTS séparé
- Synchronisation **parfaite** automatique

---

### ✅ **2. IMAGES DE RÉFÉRENCE (Character Consistency)**
```python
# ✅ NANO BANANA UNE SEULE FOIS
image_nano = client.models.generate_content(
    model="gemini-2.5-flash-image",  # Nano Banana
    contents="Nano Banana:  a cute cartoon banana character with sunglasses",
    config={"response_modalities": ['IMAGE']}
)

# ✅ RÉUTILISER DANS TOUTES LES VIDÉOS
nano_reference = types.VideoGenerationReferenceImage(
    image=image_nano. parts[0]. as_image(),
    reference_type="asset"  # Conserver le personnage
)

# Générer vidéo avec Nano Banana
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Nano Banana walking in a sunny park, waving at the camera",
    config=types.GenerateVideosConfig(
        reference_images=[nano_reference],  # ✅ MÊME PERSONNAGE
        duration_seconds=8
    )
)
```

**🎉 PERSONNAGE RÉCURRENT RÉSOLU !**
- Créer Nano Banana **1 fois** avec Nano Banana (Gemini 2.5 Flash Image)
- Le réutiliser dans **toutes** les vidéos
- Cohérence visuelle **garantie**

---

### ✅ **3. VIDÉOS JUSQU'À 8 SECONDES (ET EXTENSION ILLIMITÉE)**
```python
# ✅ Générer vidéo de 8s
operation1 = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Scene 1-2: Nano Banana discovers a treasure map",
    config=types. GenerateVideosConfig(duration_seconds=8)
)

# ✅ ÉTENDRE de 7 secondes (jusqu'à 20 fois = 141s total)
operation2 = client. models.generate_videos(
    model="veo-3.1-generate-preview",
    video=operation1.response.generated_videos[0].video,  # Vidéo précédente
    prompt="Nano Banana starts running towards the treasure location",
)

# ...  répéter jusqu'à 141 secondes
```

**🎉 VIDÉOS LONGUES ET FLUIDES !**
- Générer 8s initiaux
- Étendre par blocs de 7s
- **Jusqu'à 141 secondes** (2min21s) en une seule vidéo fluide
- Plus besoin d'assembler 8 clips séparés !

---

### ✅ **4. INTERPOLATION (Première + Dernière Image)**
```python
# ✅ Générer première et dernière image avec Nano Banana
first_frame = generate_image("Nano Banana at the start line, ready to race")
last_frame = generate_image("Nano Banana crossing the finish line, arms raised")

# ✅ Veo crée la TRANSITION entre les deux
operation = client. models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Nano Banana running a marathon race through the city",
    image=first_frame,
    config=types.GenerateVideosConfig(
        last_frame=last_frame,
        duration_seconds=8
    )
)
```

**🎉 CONTRÔLE TOTAL DES DÉBUTS ET FINS !**

---

## 🚀 **NOUVELLE ARCHITECTURE PROPOSÉE**

Voici comment refondre ton pipeline avec Veo 3.1 :

```
┌──────────────────────────────────────────────────────────────┐
│ 1. CRÉER PERSONNAGE (1 FOIS)                                │
│    ├── Utilisateur définit:  nom, description, style         │
│    ├── Gemini 2.5 Flash Image (Nano Banana) génère image   │
│    ├── Stockage: gs://bucket/characters/nano_banana.png     │
│    └── Firestore:  {character_id, name, reference_image_uri} │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. GÉNÉRER SCRIPT (avec personnage)                         │
│    ├── Utilisateur:  thème + character_id                    │
│    ├── Gemini 2.5 Pro génère script (inclut personnage)     │
│    ├── Format:  SCÈNE 1-2, SCÈNE 3-4...  (groupes de 2)       │
│    └── Sauvegarde: script_theme_character. txt               │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. GÉNÉRER VIDÉO COMPLÈTE (Veo 3.1)                         │
│    ├── Étape 1: Générer clip initial (8s)                   │
│    │   ├── Prompt:  Scènes 1-2 + dialogues + audio           │
│    │   ├── Image de référence: personnage                   │
│    │   └── Résultat: clip_1.mp4 (AVEC AUDIO)                │
│    ├── Étape 2: Étendre (7s) ×4-8 fois                      │
│    │   ├── Prompt: Scènes suivantes                         │
│    │   ├── Input: vidéo précédente                          │
│    │   └── Résultat: clip_extended.mp4 (60-141s)            │
│    └── Résultat final: UNE SEULE VIDÉO FLUIDE AVEC AUDIO    │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. GÉNÉRER SOUS-TITRES (Whisper)                            │
│    ├── Extraire audio de la vidéo finale avec FFmpeg        │
│    ├── Whisper transcrit l'audio → timestamps par mot       │
│    ├── Générer fichier ASS (sous-titres karaoke)            │
│    └── Incruster sous-titres dans la vidéo                  │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. FINALISATION                                             │
│    ├── Vidéo finale: 60-90s, 1080p, 9: 16                   │
│    ├── Audio: dialogues + effets sonores (natif Veo)        │
│    ├── Sous-titres: synchronisés parfaitement               │
│    ├── Personnage: cohérent dans toute la vidéo             │
│    └── Upload: final_theme_character.mp4                    │
└──────────────────────────────────────────────────────────────┘
```

---

## 💡 **IMPLÉMENTATION CONCRÈTE**

### **Étape 1: Créer personnage (Backend)**

#### `backend/app/routers/characters.py` (NOUVEAU)
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from google import genai
from .. services.firestore_service import get_firestore_client
from ..utils.jwt import get_current_user

router = APIRouter(prefix="/characters", tags=["Characters"])

class CharacterCreateRequest(BaseModel):
    name: str
    description: str
    style: str = "anime"

@router.post("/create")
async def create_character(
    request: CharacterCreateRequest,
    current_user = Depends(get_current_user)
):
    """Créer un personnage avec Nano Banana"""
    
    client = genai.Client()
    
    # ✅ GÉNÉRER IMAGE AVEC NANO BANANA
    prompt = f"{request.description}, {request.style} style, high quality"
    
    image_response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config={"response_modalities": ['IMAGE']}
    )
    
    # Sauvegarder l'image dans GCS
    character_id = f"{request.name.lower().replace(' ', '_')}_{int(time.time())}"
    image_path = f"characters/{character_id}.png"
    
    # Upload vers GCS
    from .. services.storage import storage_service
    bucket = storage_service.bucket
    blob = bucket.blob(image_path)
    
    # Convertir l'image Gemini en bytes
    image_bytes = image_response.parts[0].inline_data. data
    blob.upload_from_string(image_bytes, content_type="image/png")
    
    # Stocker dans Firestore
    db = get_firestore_client()
    doc_ref = db.collection('characters').document(character_id)
    doc_ref.set({
        'name': request.name,
        'description': request.description,
        'style': request.style,
        'reference_image_uri': f"gs://{bucket.name}/{image_path}",
        'created_by': current_user.id,
        'created_at':  firestore. SERVER_TIMESTAMP
    })
    
    return {
        "character_id": character_id,
        "name": request.name,
        "image_url": blob.public_url
    }

@router.get("/list")
async def list_characters(current_user = Depends(get_current_user)):
    """Liste les personnages de l'utilisateur"""
    
    db = get_firestore_client()
    characters = db.collection('characters')\
        .where('created_by', '==', current_user.id)\
        .stream()
    
    result = []
    for char in characters:
        data = char.to_dict()
        result.append({
            'id': char.id,
            'name':  data['name'],
            'description': data['description'],
            'image_url': data['reference_image_uri']. replace('gs://', 'https://storage.googleapis.com/')
        })
    
    return {"characters": result}
```

---

### **Étape 2: Modifier agent-script (avec personnage)**

#### `agent-script/main.py`
```python
@functions_framework.http
def generate_script(request):
    request_json = request.get_json(silent=True)
    
    theme = request_json["theme"]
    character_id = request_json. get("character_id")  # ✅ OPTIONNEL
    
    # Récupérer le personnage depuis Firestore
    character_description = ""
    if character_id: 
        doc = firestore_client.collection('characters').document(character_id).get()
        if doc.exists:
            char_data = doc.to_dict()
            character_description = f"\n\n✅ PERSONNAGE PRINCIPAL: {char_data['name']} - {char_data['description']}"
    
    prompt = f"""
    Génère un script TikTok de 60-90 secondes sur le thème:  "{theme}"
    {character_description}
    
    Structure en 4-6 BLOCS de 2 scènes (8-12 scènes au total).
    
    Pour chaque bloc:
    **BLOC X (Scènes Y-Z):**
    - DIALOGUES: "Texte exact à dire" (guillemets pour Veo 3.1)
    - DESCRIPTION VISUELLE: Actions et mouvements du personnage
    - EFFETS SONORES: Bruits ambiants (ex: vent, pas, porte qui grince)
    
    Exemple: 
    **BLOC 1 (Scènes 1-2):**
    - DIALOGUES:  Nano Banana murmure "Où est cette carte au trésor?"
    - VISUEL: Nano Banana cherche dans une vieille bibliothèque poussiéreuse
    - AUDIO: Planches de bois qui grincent, vent qui souffle à travers les fenêtres cassées
    
    Génère maintenant pour le thème "{theme}"
    """
    
    # ...  (génération Gemini)
```

---

### **Étape 3: Agent Vidéo (Veo 3.1 avec extensions)**

#### `agent-video-veo31/main.py` (NOUVEAU)
```python
import functions_framework
from google import genai
from google.genai import types
import time

@functions_framework.cloud_event
def generate_video_veo31(cloudevent):
    """
    Génère UNE vidéo longue avec Veo 3.1 (8s initial + extensions)
    """
    data = cloudevent.data
    bucket_name = data["bucket"]
    script_file_name = data["name"]
    
    # Lire le script
    bucket = storage_client.bucket(bucket_name)
    script_blob = bucket.blob(script_file_name)
    script_content = script_blob.download_as_text(encoding="utf-8")
    
    # Extraire character_id depuis le nom de fichier
    # Format: script_theme_character_nano_banana_123. txt
    character_id = extract_character_id(script_file_name)
    
    # Récupérer l'image de référence du personnage
    character_image_uri = None
    if character_id: 
        char_doc = firestore_client. collection('characters').document(character_id).get()
        if char_doc.exists:
            character_image_uri = char_doc.to_dict()['reference_image_uri']
    
    # Extraire les blocs de scènes
    blocks = extract_scene_blocks(script_content)
    
    print(f"🎬 Génération Veo 3.1 :  {len(blocks)} blocs")
    
    client = genai.Client()
    
    # ✅ BLOC 1 :  Générer vidéo initiale (8s)
    first_block = blocks[0]
    
    # Préparer image de référence
    reference_images = []
    if character_image_uri:
        # Télécharger l'image depuis GCS
        char_blob = bucket.blob(character_image_uri. replace(f'gs://{bucket_name}/', ''))
        image_bytes = char_blob.download_as_bytes()
        
        # Convertir en objet Image
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(image_bytes))
        
        reference_images.append(
            types.VideoGenerationReferenceImage(
                image=image,
                reference_type="asset"
            )
        )
    
    print(f"  📹 Bloc 1: {first_block['prompt'][: 60]}...")
    
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=first_block['prompt'],
        config=types.GenerateVideosConfig(
            reference_images=reference_images if reference_images else None,
            duration_seconds=8,
            resolution="1080p",
            aspect_ratio="9:16"
        )
    )
    
    # Attendre génération
    while not operation.done:
        print("    ⏳ Génération en cours...")
        time.sleep(10)
        operation = client.operations.get(operation)
    
    current_video = operation.response.generated_videos[0]. video
    print(f"  ✅ Bloc 1 généré")
    
    # ✅ BLOCS 2-N : Extensions successives (7s chacune)
    for i, block in enumerate(blocks[1:], start=2):
        print(f"  📹 Bloc {i}: Extension...")
        
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            video=current_video,  # ✅ VIDÉO PRÉCÉDENTE
            prompt=block['prompt'],
            config=types.GenerateVideosConfig(
                resolution="720p"  # Extension = 720p seulement
            )
        )
        
        while not operation. done:
            print(f"    ⏳ Extension {i} en cours...")
            time.sleep(10)
            operation = client.operations.get(operation)
        
        current_video = operation.response.generated_videos[0].video
        print(f"  ✅ Bloc {i} ajouté")
    
    # ✅ TÉLÉCHARGER LA VIDÉO FINALE
    video_base_name = script_file_name.replace("script_", "").replace(".txt", "")
    final_video_path = f"veo31_videos/{video_base_name}. mp4"
    
    # Sauvegarder dans GCS
    client.files.download(file=current_video)
    current_video. save(f"/tmp/{video_base_name}.mp4")
    
    final_blob = bucket.blob(final_video_path)
    final_blob.upload_from_filename(f"/tmp/{video_base_name}.mp4")
    
    print(f"🎉 Vidéo complète générée: {final_video_path}")
    
    # ✅ METTRE À JOUR FIRESTORE
    firestore_client.collection('video_status').document(video_base_name).set({
        'video_id': video_base_name,
        'status': 'video_ready',
        'veo31_video_uri': f"gs://{bucket_name}/{final_video_path}",
        'character_id': character_id,
        'created_at': datetime.utcnow()
    })
    
    return "OK"

def extract_scene_blocks(script_content):
    """Extrait les blocs de scènes du script"""
    blocks = []
    current_block = ""
    
    for line in script_content. splitlines():
        if line.startswith("**BLOC"):
            if current_block:
                blocks. append({'prompt': current_block. strip()})
            current_block = ""
        else:
            current_block += line + "\n"
    
    if current_block:
        blocks.append({'prompt': current_block.strip()})
    
    return blocks
```

---

### **Étape 4: Agent Assembleur (Extraction audio + Whisper)**

#### `agent-assembler-veo31/main.py` (NOUVEAU)
```python
@functions_framework.http
def assemble_veo31_video(request):
    """
    Assemble:  Vidéo Veo 3.1 + Sous-titres Whisper
    """
    request_json = request.get_json(silent=True)
    video_id = request_json['video_id']
    
    bucket = storage_client.bucket(BUCKET_NAME)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # ✅ TÉLÉCHARGER VIDÉO VEO 3.1 (AVEC AUDIO)
        veo_video_path = tmpdir_path / "veo31_video.mp4"
        veo_blob = bucket.blob(f"veo31_videos/{video_id}.mp4")
        veo_blob.download_to_filename(str(veo_video_path))
        
        print("🎵 Extraction de l'audio...")
        
        # ✅ EXTRAIRE L'AUDIO DE LA VIDÉO VEO
        audio_path = tmpdir_path / "extracted_audio.mp3"
        subprocess.run([
            'ffmpeg', '-i', str(veo_video_path),
            '-vn',  # Pas de vidéo
            '-acodec', 'mp3',
            '-y', str(audio_path)
        ], check=True)
        
        print("🎙️ Génération sous-titres avec Whisper...")
        
        # ✅ WHISPER SUR L'AUDIO EXTRAIT
        ass_path = tmpdir_path / "subtitles.ass"
        generate_whisper_subtitles(str(audio_path), str(ass_path))
        
        print("🎬 Incrustation des sous-titres...")
        
        # ✅ INCRUSTER SOUS-TITRES DANS LA VIDÉO
        final_video = tmpdir_path / "final_with_subs.mp4"
        subprocess.run([
            'ffmpeg', '-i', str(veo_video_path),
            '-vf', f"ass={str(ass_path)}",
            '-c:a', 'copy',  # Garder l'audio original
            '-y', str(final_video)
        ], check=True)
        
        # ✅ UPLOAD FINAL
        final_blob = bucket.blob(f"final_{video_id}.mp4")
        final_blob.upload_from_filename(str(final_video))
        
        print(f"✅ TERMINÉ: final_{video_id}.mp4")
        
        # Mise à jour Firestore
        firestore_client.collection('video_status').document(video_id).update({
            'status': 'completed',
            'final_video_url': f"gs://{BUCKET_NAME}/final_{video_id}.mp4"
        })
    
    return {"status": "success"}
```

---

## 🎯 **AVANTAGES DE CETTE NOUVELLE ARCHITECTURE**

| Aspect | Avant (8 clips) | Après (Veo 3.1) |
|--------|----------------|-----------------|
| **Synchronisation audio** | ❌ Décalages fréquents | ✅ Parfaite (natif) |
| **Personnage cohérent** | ❌ Varie entre clips | ✅ Identique partout |
| **Transitions** | ❌ Coupures visibles | ✅ Fluides naturelles |
| **Durée vidéo** | 32-64s (8×4s-8s) | 60-141s (8s+7s×20) |
| **Temps génération** | ~15-20 min (8 clips) | ~25-30 min (1+extensions) |
| **Coût** | ~$0.80 (8×$0.10) | ~$1.50-2.00 |
| **Complexité code** | ⚠️ Élevée (assemblage) | ✅ Simple (extensions) |
| **Qualité audio** | ⚠️ TTS robotique | ✅ Voix naturelle |

---

