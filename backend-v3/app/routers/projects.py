"""Router Projects V3 — CRUD projets."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from ..models.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from ..utils.jwt import get_current_user
from ..services.firestore_service import firestore_service

router = APIRouter(prefix="/api/v3/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
):
    """Crée un nouveau projet."""
    project = firestore_service.create_project(
        user_id=current_user["id"],
        name=data.name,
        theme=data.theme,
        description=data.description,
    )
    return project


@router.get("", response_model=ProjectListResponse)
async def list_projects(current_user: dict = Depends(get_current_user)):
    """Liste les projets de l'utilisateur."""
    projects = firestore_service.list_projects(user_id=current_user["id"])
    return ProjectListResponse(projects=projects, count=len(projects))


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Récupère un projet par ID."""
    project = firestore_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    if project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Met à jour un projet."""
    project = firestore_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    if project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")

    updated = firestore_service.update_project(project_id, update_data)
    return updated


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Supprime un projet."""
    project = firestore_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    if project.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    firestore_service.delete_project(project_id, current_user["id"])
    return {"message": "Projet supprimé"}
