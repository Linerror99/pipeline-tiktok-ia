"""
Tests unitaires pour le système d'extensions Veo 3.1.
Teste la logique SANS appeler l'API (pas de coût, pas de réseau).

Exécuter : pytest tests/unit/test_veo31_extensions.py -v
"""
import pytest
import json
from unittest.mock import MagicMock, patch, PropertyMock
import sys
import os

# Ajouter agent-video-veo31 au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "agent-video-veo31"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "cloud-functions", "monitor-extensions-v3"))


# ============================================================
# Tests agent-video-veo31/main.py
# ============================================================

class TestCalculateExtensions:
    """Tests pour calculate_extensions()."""

    def test_8s_no_extension(self):
        from main import calculate_extensions
        assert calculate_extensions(8) == 0

    def test_15s_one_extension(self):
        from main import calculate_extensions
        assert calculate_extensions(15) == 1  # 8 + 1×7

    def test_22s_two_extensions(self):
        from main import calculate_extensions
        assert calculate_extensions(22) == 2  # 8 + 2×7

    def test_29s_three_extensions(self):
        from main import calculate_extensions
        assert calculate_extensions(29) == 3

    def test_36s_four_extensions(self):
        from main import calculate_extensions
        assert calculate_extensions(36) == 4

    def test_43s_five_extensions(self):
        from main import calculate_extensions
        assert calculate_extensions(43) == 5

    def test_50s_six_extensions(self):
        from main import calculate_extensions
        assert calculate_extensions(50) == 6

    def test_57s_seven_extensions_max(self):
        from main import calculate_extensions
        assert calculate_extensions(57) == 7  # Max

    def test_100s_capped_at_7(self):
        from main import calculate_extensions
        assert calculate_extensions(100) == 7  # Capped

    def test_5s_no_extension(self):
        from main import calculate_extensions
        assert calculate_extensions(5) == 0

    def test_0s_no_extension(self):
        from main import calculate_extensions
        assert calculate_extensions(0) == 0


class TestSnapToValidDuration:
    """Tests pour snap_to_valid_duration()."""

    def test_exact_8s(self):
        from main import snap_to_valid_duration
        assert snap_to_valid_duration(8) == 8

    def test_exact_15s(self):
        from main import snap_to_valid_duration
        assert snap_to_valid_duration(15) == 15

    def test_exact_57s(self):
        from main import snap_to_valid_duration
        assert snap_to_valid_duration(57) == 57

    def test_5s_rounds_to_8s(self):
        from main import snap_to_valid_duration
        assert snap_to_valid_duration(5) == 8

    def test_10s_rounds_to_15s(self):
        from main import snap_to_valid_duration
        assert snap_to_valid_duration(10) == 15

    def test_20s_rounds_to_22s(self):
        from main import snap_to_valid_duration
        assert snap_to_valid_duration(20) == 22

    def test_25s_rounds_to_29s(self):
        from main import snap_to_valid_duration
        assert snap_to_valid_duration(25) == 29

    def test_100s_capped_at_57s(self):
        from main import snap_to_valid_duration
        assert snap_to_valid_duration(100) == 57

    def test_180s_capped_at_57s(self):
        from main import snap_to_valid_duration
        assert snap_to_valid_duration(180) == 57


class TestBuildPrompt:
    """Tests pour build_prompt()."""

    def test_initial_prompt_with_dialogue(self):
        from main import build_prompt
        block = {
            "visuel": "Un stade de football éclairé la nuit",
            "dialogue": "Bienvenue dans le top 5 des buts !",
        }
        prompt = build_prompt(block, [], is_initial=True)

        assert "Un stade de football" in prompt
        assert "Bienvenue dans le top 5" in prompt
        assert "Suite de la scène" not in prompt

    def test_extension_prompt_has_continuation(self):
        from main import build_prompt
        block = {
            "visuel": "Le ballon entre dans le filet",
            "dialogue": "Et c'est le but !",
        }
        prompt = build_prompt(block, [], is_initial=False)

        assert "Suite de la scène précédente" in prompt
        assert "Le ballon entre" in prompt

    def test_prompt_without_dialogue(self):
        from main import build_prompt
        block = {"visuel": "Plan large sur la ville"}
        prompt = build_prompt(block, [], is_initial=True)

        assert "Plan large" in prompt
        assert "Dialogue" not in prompt

    def test_prompt_with_character_refs(self):
        from main import build_prompt
        block = {"visuel": "Scène d'action", "dialogue": "En avant !"}
        chars = [{"name": "Nano Banana"}, {"name": "Fire Fox"}]
        prompt = build_prompt(block, chars, is_initial=True)

        assert "Nano Banana" in prompt
        assert "Fire Fox" in prompt

    def test_prompt_with_empty_character_refs(self):
        from main import build_prompt
        block = {"visuel": "Scène calme", "dialogue": "Bonjour"}
        prompt = build_prompt(block, [], is_initial=True)

        assert "Personnages" not in prompt


class TestValidDurationsList:
    """Tests pour la constante VALID_DURATIONS."""

    def test_valid_durations_values(self):
        from main import VALID_DURATIONS
        assert VALID_DURATIONS == [8, 15, 22, 29, 36, 43, 50, 57]

    def test_valid_durations_formula(self):
        """Vérifier que chaque durée suit la formule 8 + N×7."""
        from main import VALID_DURATIONS
        for i, d in enumerate(VALID_DURATIONS):
            assert d == 8 + i * 7, f"VALID_DURATIONS[{i}] = {d}, expected {8 + i * 7}"

    def test_veo_model_is_ga(self):
        """Vérifier qu'on utilise le modèle GA, pas preview."""
        from main import VEO_MODEL
        assert VEO_MODEL == "veo-3.1-generate-001"
        assert "preview" not in VEO_MODEL


# ============================================================
# Tests cloud-functions/monitor-extensions-v3/main.py
# ============================================================

class TestBuildExtensionPrompt:
    """Tests pour build_extension_prompt() du monitor."""

    def test_extension_prompt_uses_correct_block(self):
        # Import from monitor module
        monitor_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "cloud-functions", "monitor-extensions-v3"
        )
        sys.path.insert(0, monitor_path)
        import importlib
        # We need to handle the module name collision with agent-video-veo31's main
        # Load monitor's main module separately
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "monitor_main",
            os.path.join(monitor_path, "main.py"),
        )
        monitor_module = importlib.util.module_from_spec(spec)

        # Mock the google cloud imports
        with patch.dict("sys.modules", {
            "google.cloud": MagicMock(),
            "google.cloud.storage": MagicMock(),
            "google.cloud.firestore": MagicMock(),
            "google.auth": MagicMock(),
            "google.auth.transport": MagicMock(),
            "google.auth.transport.requests": MagicMock(),
            "functions_framework": MagicMock(),
        }):
            try:
                spec.loader.exec_module(monitor_module)
            except Exception:
                pytest.skip("Could not load monitor module (missing deps)")

            blocks = [
                {"visuel": "Bloc 1 intro", "dialogue": "Bonjour"},
                {"visuel": "Bloc 2 action", "dialogue": "En avant"},
                {"visuel": "Bloc 3 final", "dialogue": "Au revoir"},
            ]

            prompt = monitor_module.build_extension_prompt(blocks, 1, [])
            assert "Suite de la scène" in prompt
            assert "Bloc 2 action" in prompt

            prompt = monitor_module.build_extension_prompt(blocks, 2, [])
            assert "Bloc 3 final" in prompt

    def test_extension_prompt_caps_at_last_block(self):
        monitor_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "cloud-functions", "monitor-extensions-v3"
        )
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "monitor_main2",
            os.path.join(monitor_path, "main.py"),
        )
        monitor_module = importlib.util.module_from_spec(spec)

        with patch.dict("sys.modules", {
            "google.cloud": MagicMock(),
            "google.cloud.storage": MagicMock(),
            "google.cloud.firestore": MagicMock(),
            "google.auth": MagicMock(),
            "google.auth.transport": MagicMock(),
            "google.auth.transport.requests": MagicMock(),
            "functions_framework": MagicMock(),
        }):
            try:
                spec.loader.exec_module(monitor_module)
            except Exception:
                pytest.skip("Could not load monitor module (missing deps)")

            blocks = [
                {"visuel": "Seul bloc", "dialogue": "Hello"},
            ]
            # Extension 5 avec un seul bloc → doit utiliser l'index 0 (dernier dispo)
            prompt = monitor_module.build_extension_prompt(blocks, 5, [])
            assert "Seul bloc" in prompt


# ============================================================
# Tests de cohérence extensions / durées
# ============================================================

class TestDurationExtensionCoherence:
    """Tests de cohérence entre durée demandée et nombre d'extensions."""

    def test_all_durations_produce_correct_extensions(self):
        from main import calculate_extensions, snap_to_valid_duration

        test_cases = [
            (8, 8, 0),
            (10, 15, 1),
            (15, 15, 1),
            (20, 22, 2),
            (22, 22, 2),
            (30, 36, 4),
            (45, 50, 6),
            (57, 57, 7),
            (60, 57, 7),
        ]

        for input_dur, expected_snap, expected_ext in test_cases:
            snapped = snap_to_valid_duration(input_dur)
            extensions = calculate_extensions(snapped)
            assert snapped == expected_snap, (
                f"snap({input_dur}) = {snapped}, expected {expected_snap}"
            )
            assert extensions == expected_ext, (
                f"extensions({snapped}) = {extensions}, expected {expected_ext}"
            )

    def test_actual_duration_formula(self):
        """Vérifier que 8 + extensions × 7 = durée snappée."""
        from main import calculate_extensions, VALID_DURATIONS

        for duration in VALID_DURATIONS:
            ext = calculate_extensions(duration)
            actual = 8 + ext * 7
            assert actual == duration, (
                f"Duration {duration}: 8 + {ext}×7 = {actual}, mismatch"
            )
