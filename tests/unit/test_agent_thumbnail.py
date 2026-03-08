"""Tests unitaires Phase 2 — Agent Thumbnail (Imagen 4)."""
import pytest
import importlib.util
import os
import sys


def _load_module(name, path):
    """Charge un module Python depuis un chemin absolu."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    # Ne pas exécuter le module, juste le parser pour extraire les fonctions
    return mod, spec


# On charge le source manuellement pour tester les fonctions pures
# sans déclencher functions_framework ni les imports GCP
THUMBNAIL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "agent-thumbnail", "main.py"
)


class TestBuildThumbnailPrompt:
    """Tests pour build_thumbnail_prompt — fonction pure, pas d'API call."""

    def _get_func(self):
        """Charge build_thumbnail_prompt depuis le source."""
        import ast
        with open(THUMBNAIL_PATH, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)

        # Extraire le code de la fonction
        namespace = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "build_thumbnail_prompt":
                func_code = compile(
                    ast.Module(body=[node], type_ignores=[]),
                    THUMBNAIL_PATH,
                    "exec",
                )
                exec(func_code, namespace)
                break
        return namespace.get("build_thumbnail_prompt")

    def test_basic_prompt(self):
        func = self._get_func()
        assert func is not None
        result = func(
            video={"id": "v1"},
            scenario={"script": {"blocks": [{"visuel": "A cat playing piano"}]}},
            characters=[],
        )
        assert "TikTok" in result
        assert "A cat playing piano" in result

    def test_with_characters(self):
        func = self._get_func()
        result = func(
            video={"id": "v1"},
            scenario={"script": {"blocks": [{"visuel": "forest"}]}},
            characters=[
                {"name": "Nano Banana", "traits": {"style": "anime"}},
                {"name": "Cool Cat", "traits": {"style": "cartoon"}},
            ],
        )
        assert "Nano Banana" in result
        assert "Cool Cat" in result
        assert "anime" in result

    def test_empty_scenario(self):
        func = self._get_func()
        result = func(
            video={"id": "v1"},
            scenario={},
            characters=[],
        )
        assert "TikTok" in result
        assert "9:16" in result

    def test_max_two_characters(self):
        func = self._get_func()
        result = func(
            video={"id": "v1"},
            scenario={},
            characters=[
                {"name": "A", "traits": {}},
                {"name": "B", "traits": {}},
                {"name": "C", "traits": {}},
            ],
        )
        assert "A" in result
        assert "B" in result
        # C should not appear (max 2)
        assert "'C'" not in result


class TestBuildSimplePrompt:
    def _get_func(self):
        import ast
        with open(THUMBNAIL_PATH, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        namespace = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "build_simple_prompt":
                func_code = compile(
                    ast.Module(body=[node], type_ignores=[]),
                    THUMBNAIL_PATH,
                    "exec",
                )
                exec(func_code, namespace)
                break
        return namespace.get("build_simple_prompt")

    def test_basic(self):
        func = self._get_func()
        result = func(
            video={"id": "v1"},
            scenario={"title": "Funny Cats"},
        )
        assert "Funny Cats" in result
        assert "9:16" in result

    def test_default_title(self):
        func = self._get_func()
        result = func(video={"id": "v1"}, scenario={})
        assert "TikTok video" in result
