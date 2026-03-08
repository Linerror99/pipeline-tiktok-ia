"""Tests d'intégration — scénarios end-to-end pour chaque phase.

Ces tests vérifient les flux complets sans appeler les APIs réelles.
Ils utilisent des mocks pour Firestore, Storage, et les APIs IA.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import json

# ──────────────────────────────────────────────────────
# Données partagées
# ──────────────────────────────────────────────────────

USER = {
    "id": "user_integ",
    "email": "integ@test.com",
    "firebase_uid": "fb_integ",
    "display_name": "Integration User",
    "photo_url": "",
    "is_admin": False,
    "project_count": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-01-01T00:00:00Z",
}


def _get_app():
    with patch("app.utils.firebase.get_firebase_app"), \
         patch("app.utils.firebase.get_firestore_client"), \
         patch("app.utils.firebase.firebase_admin"):
        from app.main import app
        from app.utils.jwt import get_current_user

        async def mock_user():
            return USER

        app.dependency_overrides[get_current_user] = mock_user
        return app


# ──────────────────────────────────────────────────────
# Scénario 1 : Flux complet projet → personnage → scénario → vidéo
# ──────────────────────────────────────────────────────

class TestFullProjectFlow:
    """Teste le flux complet : créer projet, personnage, scénario, lancer vidéo."""

    @patch("app.routers.videos.storage_service_v3")
    @patch("app.routers.videos.firestore_service")
    @patch("app.routers.scenarios.firestore_service")
    @patch("app.routers.characters.firestore_service")
    @patch("app.routers.characters.chat_character")
    @patch("app.routers.projects.firestore_service")
    def test_full_flow(
        self, mock_proj_fs, mock_chat, mock_char_fs, mock_scen_fs, mock_vid_fs, mock_storage
    ):
        app = _get_app()
        client = TestClient(app)

        # 1. Créer un projet
        project = {
            "id": "proj_flow", "name": "Flow Test", "theme": "humour",
            "description": "", "user_id": "user_integ",
            "character_count": 0, "video_count": 0,
            "created_at": "2025-01-01", "updated_at": "2025-01-01",
        }
        mock_proj_fs.create_project.return_value = project
        resp = client.post("/api/v3/projects/", json={"name": "Flow Test", "theme": "humour"})
        assert resp.status_code == 201

        # 2. Chat personnage
        mock_char_fs.get_project.return_value = project
        mock_chat.return_value = {
            "ai_message": "Super ! Comment s'appelle ton personnage ?",
            "ready_to_generate": False,
            "suggested_traits": None,
        }
        new_char = {
            "id": "char_flow", "project_id": "proj_flow", "name": "Nouveau personnage",
            "description": "", "traits": {}, "image_url": "", "status": "draft",
            "chat_history": [], "reference_images": [], "created_at": "2025-01-01",
        }
        mock_char_fs.create_character.return_value = new_char

        resp = client.post("/api/v3/characters/chat", json={
            "project_id": "proj_flow",
            "message": "Je veux un personnage banane",
        })
        assert resp.status_code == 200
        assert "character_id" in resp.json() or resp.json().get("ai_message")

        # 3. Créer scénario via chat
        mock_scen_fs.get_project.return_value = project
        mock_scen_fs.list_characters.return_value = [new_char]

        # 4. Lancer vidéo
        scenario = {
            "id": "scen_flow", "project_id": "proj_flow",
            "title": "Test Scénario", "status": "validated",
            "target_duration": 15,
            "script": {"blocks": [
                {"visuel": "Banana danse", "dialogue": "Salut !"},
                {"visuel": "Banana saute", "dialogue": "Youhou !"},
            ]},
            "character_ids": ["char_flow"],
            "chat_history": [], "uploaded_files": [],
            "created_at": "2025-01-01",
        }
        video = {
            "id": "vid_flow", "user_id": "user_integ", "project_id": "proj_flow",
            "scenario_id": "scen_flow", "status": "pending",
            "target_duration": 15, "extensions_planned": 1, "extensions_completed": 0,
            "video_url": "", "thumbnail_url": "", "has_native_audio": True,
            "tiktok_title": "", "tiktok_hashtags": [],
            "created_at": "2025-01-01",
        }
        mock_vid_fs.get_project.return_value = project
        mock_vid_fs.get_scenario.return_value = scenario
        mock_vid_fs.get_character.return_value = new_char
        mock_vid_fs.create_video_record.return_value = video

        resp = client.post("/api/v3/videos/generate", json={
            "scenario_id": "scen_flow",
            "project_id": "proj_flow",
        })
        assert resp.status_code == 201
        assert resp.json()["status"] == "pending"
        mock_storage.upload_script_v3.assert_called_once()


# ──────────────────────────────────────────────────────
# Scénario 2 : Contrôle d'accès
# ──────────────────────────────────────────────────────

class TestAccessControl:
    """Vérifie que les ressources d'un autre user sont interdites."""

    @patch("app.routers.projects.firestore_service")
    def test_cannot_access_other_user_project(self, mock_fs):
        app = _get_app()
        client = TestClient(app)
        other_project = {
            "id": "other", "name": "Not mine", "theme": "x",
            "user_id": "OTHER_USER",
            "character_count": 0, "video_count": 0,
            "created_at": "2025-01-01", "updated_at": "2025-01-01",
        }
        mock_fs.get_project.return_value = other_project
        resp = client.get("/api/v3/projects/other")
        assert resp.status_code == 403

    @patch("app.routers.projects.firestore_service")
    def test_cannot_delete_other_user_project(self, mock_fs):
        app = _get_app()
        client = TestClient(app)
        other = {"id": "x", "name": "x", "theme": "x", "user_id": "OTHER",
                 "character_count": 0, "video_count": 0,
                 "created_at": "2025-01-01", "updated_at": "2025-01-01"}
        mock_fs.get_project.return_value = other
        resp = client.delete("/api/v3/projects/x")
        assert resp.status_code == 403

    @patch("app.routers.videos.firestore_service")
    def test_cannot_view_other_user_video(self, mock_fs):
        app = _get_app()
        client = TestClient(app)
        mock_fs.get_video.return_value = {
            "id": "v1", "user_id": "OTHER", "status": "completed",
        }
        resp = client.get("/api/v3/videos/v1")
        assert resp.status_code == 403


# ──────────────────────────────────────────────────────
# Scénario 3 : Validation durées vidéo
# ──────────────────────────────────────────────────────

class TestVideoDurationValidation:
    """Vérifie les paliers de durée 8/15/22/29/36/43/50/57."""

    def test_all_valid_durations(self):
        from app.models.video import VALID_DURATIONS
        expected = [8, 15, 22, 29, 36, 43, 50, 57]
        assert VALID_DURATIONS == expected

    def test_duration_formula_consistency(self):
        from app.models.video import VALID_DURATIONS
        for i, d in enumerate(VALID_DURATIONS):
            assert d == 8 + i * 7, f"Duration at index {i} should be {8 + i * 7}, got {d}"

    def test_min_duration(self):
        from app.models.video import VALID_DURATIONS
        assert min(VALID_DURATIONS) == 8

    def test_max_duration(self):
        from app.models.video import VALID_DURATIONS
        assert max(VALID_DURATIONS) == 57


# ──────────────────────────────────────────────────────
# Scénario 4 : Progression vidéo
# ──────────────────────────────────────────────────────

class TestVideoProgressCalculation:
    """Vérifie le calcul de progression pour différents états."""

    @patch("app.routers.videos.firestore_service")
    def test_progress_pending(self, mock_fs):
        app = _get_app()
        client = TestClient(app)
        mock_fs.get_video.return_value = {
            "id": "v1", "user_id": "user_integ", "status": "pending",
            "extensions_planned": 3, "extensions_completed": 0,
            "target_duration": 29,
        }
        resp = client.get("/api/v3/videos/v1/status")
        assert resp.status_code == 200
        assert resp.json()["progress"] == 0

    @patch("app.routers.videos.firestore_service")
    def test_progress_generating_with_extensions(self, mock_fs):
        app = _get_app()
        client = TestClient(app)
        mock_fs.get_video.return_value = {
            "id": "v1", "user_id": "user_integ", "status": "generating",
            "extensions_planned": 3, "extensions_completed": 1,
            "target_duration": 29,
        }
        resp = client.get("/api/v3/videos/v1/status")
        data = resp.json()
        assert 0 < data["progress"] < 100
        assert data["current_step"] == "Extension 2/3"

    @patch("app.routers.videos.firestore_service")
    def test_progress_completed(self, mock_fs):
        app = _get_app()
        client = TestClient(app)
        mock_fs.get_video.return_value = {
            "id": "v1", "user_id": "user_integ", "status": "completed",
            "extensions_planned": 3, "extensions_completed": 3,
            "target_duration": 29,
        }
        resp = client.get("/api/v3/videos/v1/status")
        assert resp.json()["progress"] == 100

    @patch("app.routers.videos.firestore_service")
    def test_progress_failed(self, mock_fs):
        app = _get_app()
        client = TestClient(app)
        mock_fs.get_video.return_value = {
            "id": "v1", "user_id": "user_integ", "status": "failed",
            "extensions_planned": 3, "extensions_completed": 1,
            "target_duration": 29, "error": "Safety filter",
        }
        resp = client.get("/api/v3/videos/v1/status")
        assert resp.json()["progress"] == 0


# ──────────────────────────────────────────────────────
# Scénario 5 : Endpoints de santé
# ──────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_root(self):
        app = _get_app()
        client = TestClient(app)
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["app"] == "Reetik V3"
        assert resp.json()["version"] == "3.0.0"

    def test_health(self):
        app = _get_app()
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_docs_accessible(self):
        app = _get_app()
        client = TestClient(app)
        resp = client.get("/api/v3/docs")
        assert resp.status_code == 200
