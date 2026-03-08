"""
Test ULTRA-SIMPLE : juste voir ce que Gemini génère
Pas de sauvegarde, juste affichage

Usage:
  python test_simple.py
"""

import os
import vertexai
from vertexai.generative_models import GenerativeModel

# Configuration
os.environ['GCP_PROJECT'] = 'reetik-project'
PROJECT_ID = 'reetik-project'
LOCATION = 'us-central1'

vertexai.init(project=PROJECT_ID, location=LOCATION)

def test_generation_simple():
    """Test minimaliste : voir la sortie Gemini"""
    
    theme = "Intelligence Artificielle"
    target_blocks = 5
    expected_duration = 36
    
    print("=" * 70)
    print(f"🧪 Test Génération Gemini - Format BLOCS")
    print("=" * 70)
    print(f"📝 Thème: {theme}")
    print(f"🎯 Blocs demandés: {target_blocks} ({expected_duration}s)")
    print("=" * 70)
    
    model = GenerativeModel("gemini-3.1-pro-preview")
    
    prompt = f"""
Tu es un scénariste expert pour des vidéos TikTok virales.
Ta tâche est de créer un script captivant sur le thème : "{theme}".

FORMAT STRICT : {target_blocks} BLOCS
- BLOC 1 : 8 secondes (premier bloc)
- BLOCS 2 à {target_blocks} : 7 secondes chacun
- Durée totale: {expected_duration} secondes

Pour chaque bloc, utilise EXACTEMENT ce format :

BLOC 1 (8s):
DIALOGUE: "Texte exact que le narrateur va dire pendant ce bloc"
VISUEL: Description détaillée de la scène visuelle pour une IA vidéo (décor, action, ambiance)

BLOC 2 (7s):
DIALOGUE: "Suite du texte parlé par le narrateur"
VISUEL: Description de la suite visuelle

[... jusqu'à BLOC {target_blocks}]

RÈGLES IMPÉRATIVES :
- Génère EXACTEMENT {target_blocks} blocs
- Le DIALOGUE doit être parlé naturellement en {8 if target_blocks == 1 else '8 ou 7'}s selon le bloc
- Le VISUEL doit décrire une scène cohérente avec le dialogue
- Ton captivant et éducatif
- Transitions fluides entre blocs
- PAS d'astérisques ** dans le dialogue

Génère maintenant le script pour : "{theme}"
"""
    
    print("\n⏳ Appel à Gemini 2.5 Pro...\n")
    
    try:
        response = model.generate_content(prompt)
        script_content = response.text
        
        print("✅ RÉPONSE GEMINI:")
        print("=" * 70)
        print(script_content)
        print("=" * 70)
        
        # Test parsing
        print("\n🔍 TEST PARSING:")
        print("-" * 70)
        
        import re
        
        # Nettoyer markdown comme dans main.py
        cleaned_text = script_content.replace('**BLOC', 'BLOC')
        cleaned_text = cleaned_text.replace('**DIALOGUE', 'DIALOGUE')
        cleaned_text = cleaned_text.replace('**VISUEL', 'VISUEL')
        cleaned_text = cleaned_text.replace(':**', ':')
        cleaned_text = cleaned_text.replace('**', '')
        
        bloc_pattern = r'BLOC\s+(\d+).*?DIALOGUE:\s*["\']?(.+?)["\']?\s*VISUEL:\s*(.+?)(?=(?:BLOC\s+\d+)|$)'
        matches = list(re.finditer(bloc_pattern, cleaned_text, re.IGNORECASE | re.DOTALL))
        
        print(f"Blocs trouvés: {len(matches)}")
        
        for i, match in enumerate(matches, 1):
            bloc_num = match.group(1)
            dialogue = match.group(2).strip()[:60]
            visuel = match.group(3).strip()[:60]
            print(f"\n  {i}. BLOC {bloc_num}")
            print(f"     Dialogue: {dialogue}...")
            print(f"     Visuel: {visuel}...")
        
        if len(matches) == 0:
            print("\n❌ AUCUN BLOC PARSÉ !")
            print("Le format de sortie ne correspond pas au regex.")
            print("\n💡 Solution: Ajuster le regex ou le prompt Gemini")
        elif len(matches) < target_blocks:
            print(f"\n⚠️  Seulement {len(matches)}/{target_blocks} blocs parsés")
        else:
            print(f"\n✅ Parsing OK : {len(matches)} blocs")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation_simple()
