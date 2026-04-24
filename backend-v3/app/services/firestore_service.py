"""Service Firestore V3 — CRUD pour users, projets, personnages, scénarios, vidéos."""
from firebase_admin import firestore
from datetime import datetime
from typing import Optional, List

from ..models.auth import UserInDB
from ..utils.firebase import get_firestore_client


# ──────────────────────────────────────────────
# ACCESS CODE
# ──────────────────────────────────────────────

def verify_access_code(code: str) -> bool:
    db = get_firestore_client()
    doc = db.collection("config").document("access_code").get()
    if doc.exists:
        return doc.to_dict().get("code") == code
    return False


# ──────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────

def get_user_by_id(user_id: str) -> Optional[UserInDB]:
    db = get_firestore_client()
    doc = db.collection("users_v3").document(user_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    return UserInDB(id=doc.id, **_parse_user_data(data))


def get_user_by_firebase_uid(firebase_uid: str) -> Optional[UserInDB]:
    db = get_firestore_client()
    docs = db.collection("users_v3").where("firebase_uid", "==", firebase_uid).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        return UserInDB(id=doc.id, **_parse_user_data(data))
    return None


def create_user_from_firebase(firebase_uid: str, email: str, display_name: str = None, photo_url: str = None) -> UserInDB:
    db = get_firestore_client()
    user_data = {
        "firebase_uid": firebase_uid,
        "email": email,
        "display_name": display_name or "",
        "photo_url": photo_url or "",
        "is_admin": False,
        "video_count": 0,
        "project_count": 0,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
    }
    doc_ref = db.collection("users_v3").document()
    doc_ref.set(user_data)
    return get_user_by_id(doc_ref.id)


def update_last_login(user_id: str):
    db = get_firestore_client()
    db.collection("users_v3").document(user_id).update(
        {"last_login": datetime.utcnow()}
    )


def _parse_user_data(data: dict) -> dict:
    return {
        "email": data.get("email", ""),
        "display_name": data.get("display_name"),
        "photo_url": data.get("photo_url"),
        "firebase_uid": data.get("firebase_uid", ""),
        "is_admin": data.get("is_admin", False),
        "video_count": data.get("video_count", 0),
        "project_count": data.get("project_count", 0),
        "created_at": data.get("created_at"),
        "last_login": data.get("last_login"),
    }


# ──────────────────────────────────────────────
# PROJECTS
# ──────────────────────────────────────────────

def create_project(user_id: str, name: str, theme: str, description: str = None) -> dict:
    db = get_firestore_client()
    project_data = {
        "name": name,
        "theme": theme,
        "description": description or "",
        "user_id": user_id,
        "character_count": 0,
        "video_count": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    doc_ref = db.collection("projects_v3").document()
    doc_ref.set(project_data)

    # Increment user project count
    db.collection("users_v3").document(user_id).update(
        {"project_count": firestore.Increment(1)}
    )

    return {"id": doc_ref.id, **project_data}


def get_project(project_id: str) -> Optional[dict]:
    db = get_firestore_client()
    doc = db.collection("projects_v3").document(project_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


def list_projects(user_id: str) -> List[dict]:
    db = get_firestore_client()
    docs = db.collection("projects_v3").where("user_id", "==", user_id).order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def update_project(project_id: str, updates: dict) -> bool:
    db = get_firestore_client()
    updates["updated_at"] = datetime.utcnow()
    db.collection("projects_v3").document(project_id).update(updates)
    return True


def delete_project(project_id: str, user_id: str) -> bool:
    db = get_firestore_client()
    db.collection("projects_v3").document(project_id).delete()
    db.collection("users_v3").document(user_id).update(
        {"project_count": firestore.Increment(-1)}
    )
    return True


# ──────────────────────────────────────────────
# CHARACTERS
# ──────────────────────────────────────────────

def create_character(project_id: str, name: str = "Nouveau personnage") -> dict:
    db = get_firestore_client()
    char_data = {
        "project_id": project_id,
        "name": name,
        "description": "",
        "traits": {},
        "image_url": None,
        "reference_images": [],
        "chat_history": [],
        "status": "draft",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    doc_ref = db.collection("characters").document()
    doc_ref.set(char_data)

    db.collection("projects_v3").document(project_id).update(
        {"character_count": firestore.Increment(1), "updated_at": datetime.utcnow()}
    )
    return {"id": doc_ref.id, **char_data}


def get_character(character_id: str) -> Optional[dict]:
    db = get_firestore_client()
    doc = db.collection("characters").document(character_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


def list_characters(project_id: str) -> List[dict]:
    db = get_firestore_client()
    docs = db.collection("characters").where("project_id", "==", project_id).stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def update_character(character_id: str, updates: dict) -> bool:
    db = get_firestore_client()
    updates["updated_at"] = datetime.utcnow()
    db.collection("characters").document(character_id).update(updates)
    return True


def append_character_chat(character_id: str, role: str, content: str):
    db = get_firestore_client()
    db.collection("characters").document(character_id).update({
        "chat_history": firestore.ArrayUnion([{"role": role, "content": content}]),
        "updated_at": datetime.utcnow(),
    })


def delete_character(character_id: str) -> bool:
    db = get_firestore_client()
    doc = db.collection("characters").document(character_id)
    char = doc.get()
    if char.exists:
        project_id = char.to_dict().get("project_id")
        doc.delete()
        if project_id:
            db.collection("projects_v3").document(project_id).update(
                {"character_count": firestore.Increment(-1), "updated_at": datetime.utcnow()}
            )
    return True


# ──────────────────────────────────────────────
# SCENARIOS
# ──────────────────────────────────────────────

def create_scenario(project_id: str) -> dict:
    db = get_firestore_client()
    scenario_data = {
        "project_id": project_id,
        "title": None,
        "description": None,
        "script": None,
        "uploaded_files": [],
        "chat_history": [],
        "character_ids": [],
        "status": "draft",
        "target_duration": 22,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    doc_ref = db.collection("scenarios").document()
    doc_ref.set(scenario_data)
    return {"id": doc_ref.id, **scenario_data}


def get_scenario(scenario_id: str) -> Optional[dict]:
    db = get_firestore_client()
    doc = db.collection("scenarios").document(scenario_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


def list_scenarios(project_id: str) -> List[dict]:
    db = get_firestore_client()
    docs = db.collection("scenarios").where("project_id", "==", project_id).stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]


def update_scenario(scenario_id: str, updates: dict) -> bool:
    db = get_firestore_client()
    updates["updated_at"] = datetime.utcnow()
    db.collection("scenarios").document(scenario_id).update(updates)
    return True


def append_scenario_chat(scenario_id: str, role: str, content: str):
    db = get_firestore_client()
    db.collection("scenarios").document(scenario_id).update({
        "chat_history": firestore.ArrayUnion([{"role": role, "content": content}]),
        "updated_at": datetime.utcnow(),
    })


def delete_scenario(scenario_id: str) -> bool:
    db = get_firestore_client()
    db.collection("scenarios").document(scenario_id).delete()
    return True


# ──────────────────────────────────────────────
# VIDEOS V3
# ──────────────────────────────────────────────

def create_video_record(project_id: str, scenario_id: str, target_duration: int, user_id: str = "", script: dict = None) -> dict:
    db = get_firestore_client()
    video_data = {
        "project_id": project_id,
        "user_id": user_id,
        "scenario_id": scenario_id,
        "status": "pending",
        "video_url": None,
        "thumbnail_url": None,
        "target_duration": target_duration,
        "actual_duration": None,
        "has_native_audio": True,
        "extensions_planned": 0,
        "extensions_completed": 0,
        "tiktok_title": None,
        "tiktok_hashtags": [],
        "error": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "completed_at": None,
    }
    doc_ref = db.collection("videos_v3").document()
    doc_ref.set(video_data)
    return {"id": doc_ref.id, **video_data}


def get_video(video_id: str) -> Optional[dict]:
    db = get_firestore_client()
    doc = db.collection("videos_v3").document(video_id).get()
    if not doc.exists:
        return None
    return {"id": doc.id, **doc.to_dict()}


def list_videos(project_id: str) -> List[dict]:
    db = get_firestore_client()
    docs = db.collection("videos_v3").where("project_id", "==", project_id).stream()
    results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
    return sorted(results, key=lambda v: v.get("created_at") or "", reverse=True)


def update_video(video_id: str, updates: dict) -> bool:
    db = get_firestore_client()
    updates["updated_at"] = datetime.utcnow()
    db.collection("videos_v3").document(video_id).update(updates)
    return True


def delete_video(video_id: str) -> bool:
    db = get_firestore_client()
    db.collection("videos_v3").document(video_id).delete()
    return True


# Alias du module — permet `from app.services.firestore_service import firestore_service`
import sys as _sys
firestore_service = _sys.modules[__name__]
