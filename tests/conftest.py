"""
Configuration pytest — ajoute les dossiers nécessaires au sys.path.
Permet d'importer 'app' (backend-v3) depuis n'importe quel répertoire.
"""
import sys
import os

# Racine du projet
ROOT = os.path.dirname(os.path.dirname(__file__))

# backend-v3 → permet `from app.xxx import ...`
sys.path.insert(0, os.path.join(ROOT, "backend-v3"))
