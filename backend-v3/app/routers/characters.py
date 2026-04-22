"""Router Characters V3 — Chat IA + Imagen 4 génération."""
from fastapi import APIRouter, HTTPException, Depends

from ..models.character import (
    CharacterChatRequest,
    CharacterChatResponse,
    CharacterGenerateRequest,
    CharacterResponse,
    CharacterListResponse,
)
from ..utils.jwt import get_current_user
from ..services.firestore_service import firestore_service
from ..services.chat_service import chat_character
from ..services.character_service import generate_character_image, generate_character_variations

router = APIRouter(prefix="/api/v3/characters", tags=["characters"])


@router.post("/chat", response_model=CharacterChatResponse)
async def chat_with_ai(
    data: CharacterChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Chat IA pour créer/affiner un personnage."""
    # Vérifier ownership du projet
    project = firestore_service.get_project(data.project_id)
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Charger historique si personnage existant
    chat_history = []
    if data.character_id:
        char = firestore_service.get_character(data.character_id)
        if char and char.get("project_id") == data.project_id:
            chat_history = char.get("chat_history", [])

    # Chat avec Gemini
    result = chat_character(
        chat_history=chat_history,
        user_message=data.message,
        project_theme=project.get("theme", ""),
    )

    # Sauvegarder dans l'historique
    if data.character_id:
        firestore_service.append_character_chat(
            data.character_id,
            role="user",
            content=data.message,
        )
        firestore_service.append_character_chat(
            data.character_id,
            role="model",
            content=result["ai_message"],
        )
    else:
        # Créer un nouveau personnage avec le début de conversation
        char = firestore_service.create_character(
            project_id=data.project_id,
            name="Nouveau personnage",
        )
        firestore_service.append_character_chat(
            char["id"],
            role="user",
            content=data.message,
        )
        firestore_service.append_character_chat(
            char["id"],
            role="model",
            content=result["ai_message"],
        )
        result["character_id"] = char["id"]

    return CharacterChatResponse(
        ai_message=result["ai_message"],
        character_id=data.character_id or result.get("character_id"),
        suggested_traits=result.get("suggested_traits"),
        ready_to_generate=result.get("ready_to_generate", False),
    )


@router.post("/{character_id}/generate", response_model=CharacterResponse)
async def generate_character(
    character_id: str,
    data: CharacterGenerateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Génère l'image du personnage avec Imagen 4."""
    char = firestore_service.get_character(character_id)
    if not char:
        raise HTTPException(status_code=404, detail="Personnage non trouvé")

    project = firestore_service.get_project(char.get("project_id"))
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Mettre à jour les traits
    traits = data.traits or char.get("traits", {})
    firestore_service.update_character(character_id, {
        "traits": traits,
        "status": "generating",
    })

    # Générer avec Imagen 4
    result = await generate_character_image(
        character_id=character_id,
        project_id=char["project_id"],
        traits=traits,
        custom_prompt=data.custom_prompt,
    )

    if not result["success"]:
        firestore_service.update_character(character_id, {"status": "error"})
        raise HTTPException(status_code=500, detail=result.get("error", "Erreur de génération"))

    # Mettre à jour le personnage
    firestore_service.update_character(character_id, {
        "image_url": result["image_url"],
        "status": "ready",
        "traits": traits,
    })

    updated = firestore_service.get_character(character_id)
    return updated


@router.post("/{character_id}/regenerate", response_model=CharacterResponse)
async def regenerate_character(
    character_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Regénère l'image du personnage."""
    char = firestore_service.get_character(character_id)
    if not char:
        raise HTTPException(status_code=404, detail="Personnage non trouvé")

    project = firestore_service.get_project(char.get("project_id"))
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    traits = char.get("traits", {})
    firestore_service.update_character(character_id, {"status": "generating"})

    result = await generate_character_image(
        character_id=character_id,
        project_id=char["project_id"],
        traits=traits,
    )

    if not result["success"]:
        firestore_service.update_character(character_id, {"status": "error"})
        raise HTTPException(status_code=500, detail=result.get("error", "Erreur de génération"))

    firestore_service.update_character(character_id, {
        "image_url": result["image_url"],
        "status": "ready",
    })

    return firestore_service.get_character(character_id)


@router.get("", response_model=CharacterListResponse)
async def list_characters(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Liste les personnages d'un projet."""
    project = firestore_service.get_project(project_id)
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    chars = firestore_service.list_characters(project_id)
    return CharacterListResponse(characters=chars, count=len(chars))


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Récupère un personnage."""
    char = firestore_service.get_character(character_id)
    if not char:
        raise HTTPException(status_code=404, detail="Personnage non trouvé")

    project = firestore_service.get_project(char.get("project_id"))
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    return char


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: str,
    data: dict,
    current_user: dict = Depends(get_current_user),
):
    """Met à jour un personnage (nom, description, traits)."""
    char = firestore_service.get_character(character_id)
    if not char:
        raise HTTPException(status_code=404, detail="Personnage non trouvé")

    project = firestore_service.get_project(char.get("project_id"))
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    allowed_fields = {"name", "description", "traits"}
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucun champ valide")

    return firestore_service.update_character(character_id, update_data)
