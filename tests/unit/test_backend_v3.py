"""Tests unitaires Phase 1 — Backend V3 (models, auth, routers)."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import json

# ──────────────────────────────────────────────────────
# Fixtures et helpers
# ──────────────────────────────────────────────────────

MOCK_USER = {
    "id": "user123",
    "email": "test@example.com",
    "firebase_uid": "fb_uid_123",
    "display_name": "Test User",
    "photo_url": "",
    "is_admin": False,
    "project_count": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "last_login": "2025-01-01T00:00:00Z",
}

MOCK_PROJECT = {
    "id": "proj123",
    "name": "Test Project",
    "theme": "comédie",
    "description": "Un projet test",
    "user_id": "user123",
    "character_count": 0,
    "video_count": 0,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

MOCK_CHARACTER = {
    "id": "char123",
    "project_id": "proj123",
    "name": "Nano Banana",
    "description": "Une banane anime",
    "traits": {"style": "anime", "colors": "jaune"},
    "image_url": "",
    "status": "draft",
    "chat_history": [],
    "reference_images": [],
    "created_at": "2025-01-01T00:00:00Z",
}

MOCK_SCENARIO = {
    "id": "scen123",
    "project_id": "proj123",
    "title": "Scénario test",
    "script": {"blocks": [{"visuel": "test", "dialogue": "hello"}]},
    "status": "validated",
    "target_duration": 8,
    "character_ids": [],
    "chat_history": [],
    "uploaded_files": [],
    "created_at": "2025-01-01T00:00:00Z",
}

MOCK_VIDEO = {
    "id": "vid123",
    "user_id": "user123",
    "project_id": "proj123",
    "scenario_id": "scen123",
    "status": "pending",
    "target_duration": 8,
    "extensions_planned": 0,
    "extensions_completed": 0,
    "video_url": "",
    "thumbnail_url": "",
    "has_native_audio": True,
    "tiktok_title": "",
    "tiktok_hashtags": [],
    "created_at": "2025-01-01T00:00:00Z",
}


def _get_test_client():
    """Crée un TestClient avec mocks Firebase/JWT."""
    # Patch Firebase et JWT avant d'importer l'app
    with patch("app.utils.firebase.get_firebase_app"), \
         patch("app.utils.firebase.get_firestore_client"), \
         patch("app.utils.firebase.firebase_admin"):
        from app.main import app
        from app.utils.jwt import get_current_user

        # Override la dépendance auth
        async def mock_get_current_user():
            return MOCK_USER

        app.dependency_overrides[get_current_user] = mock_get_current_user
        return TestClient(app)


# ──────────────────────────────────────────────────────
# Tests Models
# ──────────────────────────────────────────────────────

class TestModels:
    def test_valid_durations(self):
        from app.models.video import VALID_DURATIONS
        assert VALID_DURATIONS == [8, 15, 22, 29, 36, 43, 50, 57]

    def test_duration_formula(self):
        """8 + N*7 pour N = 0..7."""
        from app.models.video import VALID_DURATIONS
        for i, d in enumerate(VALID_DURATIONS):
            assert d == 8 + i * 7

    def test_project_create_model(self):
        from app.models.project import ProjectCreate
        p = ProjectCreate(name="Test", theme="comédie")
        assert p.name == "Test"
        assert p.theme == "comédie"
        assert p.description is None

    def test_firebase_login_request(self):
        from app.models.auth import FirebaseLoginRequest
        req = FirebaseLoginRequest(id_token="abc123")
        assert req.id_token == "abc123"

    def test_video_generate_request(self):
        from app.models.video import VideoGenerateRequest
        req = VideoGenerateRequest(scenario_id="s1", project_id="p1")
        assert req.scenario_id == "s1"

    def test_character_chat_request(self):
        from app.models.character import CharacterChatRequest
        req = CharacterChatRequest(project_id="p1", message="Hello")
        assert req.character_id is None

    def test_scenario_validate_with_valid_duration(self):
        from app.models.scenario import ScenarioValidateRequest
        req = ScenarioValidateRequest(scenario_id="s1", project_id="proj123", target_duration=15)
        assert req.target_duration == 15

    def test_scenario_validate_with_character_ids(self):
        from app.models.scenario import ScenarioValidateRequest
        req = ScenarioValidateRequest(
            scenario_id="s1",
            project_id="proj123",
            target_duration=22,
            character_ids=["c1", "c2"],
        )
        assert len(req.character_ids) == 2


# ──────────────────────────────────────────────────────
# Tests Auth Router
# ──────────────────────────────────────────────────────

class TestAuthRouter:
    @patch("app.routers.auth.firestore_service")
    def test_verify_code_valid(self, mock_fs):
        mock_fs.verify_access_code.return_value = True
        client = _get_test_client()
        resp = client.post("/api/v3/auth/verify-code", json={"code": "ABCD1234"})
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

    @patch("app.routers.auth.firestore_service")
    def test_verify_code_invalid(self, mock_fs):
        mock_fs.verify_access_code.return_value = False
        client = _get_test_client()
        resp = client.post("/api/v3/auth/verify-code", json={"code": "WRONGXXX"})
        assert resp.status_code == 403

    @patch("app.routers.auth.firestore_service")
    @patch("app.routers.auth.verify_firebase_token")
    @patch("app.routers.auth.create_access_token")
    def test_login_existing_user(self, mock_jwt, mock_verify, mock_fs):
        mock_verify.return_value = {"uid": "fb_123", "email": "a@b.com", "name": "Test"}
        mock_fs.get_user_by_firebase_uid.return_value = MOCK_USER
        mock_jwt.return_value = "jwt_token_v3"
        client = _get_test_client()
        resp = client.post("/api/v3/auth/login", json={"id_token": "firebase_token"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "jwt_token_v3"
        assert data["token_type"] == "bearer"

    @patch("app.routers.auth.firestore_service")
    @patch("app.routers.auth.verify_firebase_token")
    def test_login_invalid_token(self, mock_verify, mock_fs):
        mock_verify.return_value = None
        client = _get_test_client()
        resp = client.post("/api/v3/auth/login", json={"id_token": "bad_token"})
        assert resp.status_code == 401

    def test_get_me(self):
        client = _get_test_client()
        resp = client.get("/api/v3/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@example.com"


# ──────────────────────────────────────────────────────
# Tests Projects Router
# ──────────────────────────────────────────────────────

class TestProjectsRouter:
    @patch("app.routers.projects.firestore_service")
    def test_create_project(self, mock_fs):
        mock_fs.create_project.return_value = MOCK_PROJECT
        client = _get_test_client()
        resp = client.post("/api/v3/projects/", json={
            "name": "Test Project",
            "theme": "comédie",
        })
        assert resp.status_code == 201

    @patch("app.routers.projects.firestore_service")
    def test_list_projects(self, mock_fs):
        mock_fs.list_projects.return_value = [MOCK_PROJECT]
        client = _get_test_client()
        resp = client.get("/api/v3/projects/")
        assert resp.status_code == 200
        assert resp.json()["count"] == 1

    @patch("app.routers.projects.firestore_service")
    def test_get_project_owned(self, mock_fs):
        mock_fs.get_project.return_value = MOCK_PROJECT
        client = _get_test_client()
        resp = client.get("/api/v3/projects/proj123")
        assert resp.status_code == 200

    @patch("app.routers.projects.firestore_service")
    def test_get_project_not_owned(self, mock_fs):
        other_project = {**MOCK_PROJECT, "user_id": "other_user"}
        mock_fs.get_project.return_value = other_project
        client = _get_test_client()
        resp = client.get("/api/v3/projects/proj123")
        assert resp.status_code == 403

    @patch("app.routers.projects.firestore_service")
    def test_get_project_not_found(self, mock_fs):
        mock_fs.get_project.return_value = None
        client = _get_test_client()
        resp = client.get("/api/v3/projects/nonexistent")
        assert resp.status_code == 404

    @patch("app.routers.projects.firestore_service")
    def test_delete_project(self, mock_fs):
        mock_fs.get_project.return_value = MOCK_PROJECT
        client = _get_test_client()
        resp = client.delete("/api/v3/projects/proj123")
        assert resp.status_code == 200
        mock_fs.delete_project.assert_called_once_with("proj123")


# ──────────────────────────────────────────────────────
# Tests Videos Router
# ──────────────────────────────────────────────────────

class TestVideosRouter:
    @patch("app.routers.videos.storage_service_v3")
    @patch("app.routers.videos.firestore_service")
    def test_generate_video(self, mock_fs, mock_storage):
        mock_fs.get_project.return_value = MOCK_PROJECT
        mock_fs.get_scenario.return_value = MOCK_SCENARIO
        mock_fs.get_character.return_value = MOCK_CHARACTER
        mock_fs.create_video_record.return_value = MOCK_VIDEO
        client = _get_test_client()
        resp = client.post("/api/v3/videos/generate", json={
            "scenario_id": "scen123",
            "project_id": "proj123",
        })
        assert resp.status_code == 201
        mock_storage.upload_script_v3.assert_called_once()

    @patch("app.routers.videos.firestore_service")
    def test_generate_video_unvalidated_scenario(self, mock_fs):
        mock_fs.get_project.return_value = MOCK_PROJECT
        unvalidated = {**MOCK_SCENARIO, "status": "draft"}
        mock_fs.get_scenario.return_value = unvalidated
        client = _get_test_client()
        resp = client.post("/api/v3/videos/generate", json={
            "scenario_id": "scen123",
            "project_id": "proj123",
        })
        assert resp.status_code == 400

    @patch("app.routers.videos.firestore_service")
    def test_list_videos(self, mock_fs):
        mock_fs.list_videos.return_value = [MOCK_VIDEO]
        client = _get_test_client()
        resp = client.get("/api/v3/videos/?project_id=proj123")
        assert resp.status_code == 200
        assert resp.json()["count"] == 1

    @patch("app.routers.videos.firestore_service")
    def test_video_status_completed(self, mock_fs):
        completed = {**MOCK_VIDEO, "status": "completed", "extensions_planned": 1, "extensions_completed": 1}
        mock_fs.get_video.return_value = completed
        client = _get_test_client()
        resp = client.get("/api/v3/videos/vid123/status")
        assert resp.status_code == 200
        assert resp.json()["progress"] == 100

    @patch("app.routers.videos.firestore_service")
    def test_video_status_in_progress(self, mock_fs):
        in_progress = {**MOCK_VIDEO, "status": "generating", "extensions_planned": 3, "extensions_completed": 1}
        mock_fs.get_video.return_value = in_progress
        client = _get_test_client()
        resp = client.get("/api/v3/videos/vid123/status")
        assert resp.status_code == 200
        data = resp.json()
        assert 0 < data["progress"] < 100

    @patch("app.routers.videos.storage_service_v3")
    @patch("app.routers.videos.firestore_service")
    def test_stream_not_completed(self, mock_fs, mock_storage):
        mock_fs.get_video.return_value = MOCK_VIDEO  # status=pending
        client = _get_test_client()
        resp = client.get("/api/v3/videos/vid123/stream")
        assert resp.status_code == 400


# ──────────────────────────────────────────────────────
# Tests TikTok Router
# ──────────────────────────────────────────────────────

class TestTikTokRouter:
    @patch("app.routers.tiktok.suggest_profile", new_callable=AsyncMock)
    @patch("app.routers.tiktok.firestore_service")
    def test_suggest_profile(self, mock_fs, mock_suggest):
        mock_fs.get_project.return_value = MOCK_PROJECT
        mock_suggest.return_value = {"username": "@comedy_king", "bio": "Le roi de la comédie"}
        client = _get_test_client()
        resp = client.post("/api/v3/tiktok/suggest-profile", json={
            "project_id": "proj123",
        })
        assert resp.status_code == 200
        assert "username" in resp.json()

    @patch("app.routers.tiktok.suggest_hashtags", new_callable=AsyncMock)
    @patch("app.routers.tiktok.firestore_service")
    def test_suggest_hashtags(self, mock_fs, mock_suggest):
        mock_fs.get_project.return_value = MOCK_PROJECT
        mock_suggest.return_value = {"hashtags": ["#funny", "#tiktok"]}
        client = _get_test_client()
        resp = client.post("/api/v3/tiktok/suggest-hashtags", json={
            "project_id": "proj123",
        })
        assert resp.status_code == 200
        assert "hashtags" in resp.json()


# ──────────────────────────────────────────────────────
# Tests Chat Service (unitaire)
# ──────────────────────────────────────────────────────

class TestChatService:
    def test_extract_script_json(self):
        from app.services.chat_service import _extract_script_json
        text = 'Voici le script:\n```json\n{"blocks": [{"visuel": "test", "dialogue": "ok"}]}\n```'
        result = _extract_script_json(text)
        assert result is not None
        assert len(result["blocks"]) == 1

    def test_extract_script_json_none(self):
        from app.services.chat_service import _extract_script_json
        result = _extract_script_json("pas de json ici")
        assert result is None

    def test_extract_character_traits(self):
        from app.services.chat_service import _extract_character_traits
        text = "**Nom** : Nano Banana\n**Style** : anime\n**Couleurs** : jaune, vert"
        traits = _extract_character_traits(text)
        assert traits is not None
        assert "Nano Banana" in traits.get("name", "")


# ──────────────────────────────────────────────────────
# Tests Notification Service
# ──────────────────────────────────────────────────────

class TestNotificationService:
    def test_sanitize_html(self):
        from app.services.notification_service import _sanitize_html
        assert _sanitize_html('<script>alert("xss")</script>') == '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'
        assert _sanitize_html("") == ""

    def test_sanitize_url(self):
        from app.services.notification_service import _sanitize_url
        assert _sanitize_url("javascript:alert(1)") == "#"
        assert _sanitize_url("https://example.com") == "https://example.com"
        assert _sanitize_url("") == "#"
        assert _sanitize_url("data:text/html,<h1>hi</h1>") == "#"


# ──────────────────────────────────────────────────────
# Tests Config
# ──────────────────────────────────────────────────────

class TestConfig:
    def test_settings_defaults(self):
        from app.config import settings
        assert settings.PROJECT_ID == "reetik-project"
        assert settings.BUCKET_NAME_V3 == "reetik-v3-artifacts"
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.JWT_EXPIRE_DAYS == 7
        assert settings.REGION == "us-central1"

    def test_valid_cors_origins(self):
        from app.config import settings
        assert "http://localhost:5173" in settings.CORS_ORIGINS


# ──────────────────────────────────────────────────────
# Tests TikTok Service (parse)
# ──────────────────────────────────────────────────────

class TestTikTokServiceParse:
    def test_parse_json_response_with_code_block(self):
        from app.services.tiktok_service import _parse_json_response
        text = '```json\n{"hashtags": ["#fun"]}\n```'
        result = _parse_json_response(text)
        assert result["hashtags"] == ["#fun"]

    def test_parse_json_response_raw(self):
        from app.services.tiktok_service import _parse_json_response
        text = '{"hashtags": ["#fun", "#cool"]}'
        result = _parse_json_response(text)
        assert len(result["hashtags"]) == 2

    def test_parse_json_response_fallback(self):
        from app.services.tiktok_service import _parse_json_response
        result = _parse_json_response("no json here", fallback_key="data")
        assert "data" in result
