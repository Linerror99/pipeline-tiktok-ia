"""Router Scenarios V3 — Chat IA, upload fichiers, validation script."""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
import uuid

from ..models.scenario import (
    ScenarioChatRequest,
    ScenarioChatResponse,
    ScenarioValidateRequest,
    ScenarioResponse,
    ScenarioListResponse,
)
from ..models.video import VALID_DURATIONS
from ..utils.jwt import get_current_user
from ..services.firestore_service import firestore_service
from ..services.chat_service import chat_scenario
from ..services.storage import storage_service_v3

router = APIRouter(prefix="/api/v3/scenarios", tags=["scenarios"])


@router.post("/chat", response_model=ScenarioChatResponse)
async def chat_with_ai(
    data: ScenarioChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Chat IA pour créer/affiner un scénario."""
    project = firestore_service.get_project(data.project_id)
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Charger historique si scénario existant
    chat_history = []
    uploaded_files_context = ""
    if data.scenario_id:
        scenario = firestore_service.get_scenario(data.scenario_id)
        if scenario and scenario.get("project_id") == data.project_id:
            chat_history = scenario.get("chat_history", [])
            uploaded_files = scenario.get("uploaded_files", [])
            if uploaded_files:
                uploaded_files_context = "\n".join(
                    f"- {f.get('name', '?')}: {f.get('context', 'pas de contexte')}"
                    for f in uploaded_files
                )

    # Charger les personnages du projet
    characters = firestore_service.list_characters(data.project_id)

    result = chat_scenario(
        chat_history=chat_history,
        user_message=data.message,
        project_theme=project.get("theme", ""),
        characters=characters,
        uploaded_files_context=uploaded_files_context,
    )

    # Sauvegarder
    if data.scenario_id:
        firestore_service.append_scenario_chat(
            data.scenario_id,
            {"role": "user", "content": data.message},
        )
        firestore_service.append_scenario_chat(
            data.scenario_id,
            {"role": "model", "content": result["ai_message"]},
        )
    else:
        scenario = firestore_service.create_scenario(
            project_id=data.project_id,
            title="Nouveau scénario",
        )
        firestore_service.append_scenario_chat(
            scenario["id"],
            {"role": "user", "content": data.message},
        )
        firestore_service.append_scenario_chat(
            scenario["id"],
            {"role": "model", "content": result["ai_message"]},
        )
        result["scenario_id"] = scenario["id"]

    return ScenarioChatResponse(
        ai_message=result["ai_message"],
        scenario_id=data.scenario_id or result.get("scenario_id"),
        script_preview=result.get("script_preview"),
        ready_to_validate=result.get("ready_to_validate", False),
    )


@router.post("/{scenario_id}/upload")
async def upload_context_file(
    scenario_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """Upload un fichier de contexte pour le scénario."""
    scenario = firestore_service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scénario non trouvé")

    project = firestore_service.get_project(scenario.get("project_id"))
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Valider le type de fichier
    allowed_types = {
        "text/plain", "application/pdf",
        "image/jpeg", "image/png", "image/webp",
        "application/json",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Type de fichier non autorisé: {file.content_type}. Acceptés: txt, pdf, jpg, png, webp, json",
        )

    # Limiter la taille (10 MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Fichier trop volumineux (max 10 MB)")

    # Upload vers GCS
    file_id = uuid.uuid4().hex
    gcs_path = f"uploads/{project['id']}/{scenario_id}/{file_id}_{file.filename}"
    url = storage_service_v3.upload_file(content, gcs_path, file.content_type)

    # Enregistrer dans le scénario
    file_record = {
        "id": file_id,
        "name": file.filename,
        "content_type": file.content_type,
        "gcs_path": gcs_path,
        "size": len(content),
    }

    uploaded_files = scenario.get("uploaded_files", [])
    uploaded_files.append(file_record)
    firestore_service.update_scenario(scenario_id, {"uploaded_files": uploaded_files})

    return {"file_id": file_id, "name": file.filename, "size": len(content)}


@router.post("/{scenario_id}/validate", response_model=ScenarioResponse)
async def validate_scenario(
    scenario_id: str,
    data: ScenarioValidateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Valide et finalise le scénario avec le script JSON."""
    scenario = firestore_service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scénario non trouvé")

    project = firestore_service.get_project(scenario.get("project_id"))
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    if data.target_duration not in VALID_DURATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Durée invalide. Valeurs acceptées: {VALID_DURATIONS}",
        )

    # Le script doit avoir été généré par le chat
    if not scenario.get("script"):
        raise HTTPException(status_code=400, detail="Aucun script généré. Continuez le chat IA.")

    firestore_service.update_scenario(scenario_id, {
        "status": "validated",
        "target_duration": data.target_duration,
        "character_ids": data.character_ids or [],
    })

    return firestore_service.get_scenario(scenario_id)


@router.get("/", response_model=ScenarioListResponse)
async def list_scenarios(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Liste les scénarios d'un projet."""
    project = firestore_service.get_project(project_id)
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    scenarios = firestore_service.list_scenarios(project_id)
    return ScenarioListResponse(scenarios=scenarios, total=len(scenarios))


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Récupère un scénario."""
    scenario = firestore_service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scénario non trouvé")

    project = firestore_service.get_project(scenario.get("project_id"))
    if not project or project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    return scenario
