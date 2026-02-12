# 💰 ANALYSE COÛTS RÉELS - Pipeline TikTok IA

**Date:** 31 Décembre 2025  
**Source:** Tarification officielle Vertex AI

---

## 📊 PRICING VERTEX AI (Données Officielles)

### Gemini 2.5 Pro
| Type | Prix (≤200K tokens) | Prix (>200K tokens) |
|------|---------------------|---------------------|
| **Entrée texte** | $1.25/M tokens | $2.50/M tokens |
| **Sortie texte** | $10.00/M tokens | $15.00/M tokens |

### Veo 3.0 (Version Actuelle)
| Fonctionnalité | Résolution | Prix |
|----------------|------------|------|
| **Vidéo seule** | 720p/1080p | **$0.20/seconde** |
| **Vidéo + Audio** | 720p/1080p | **$0.40/seconde** |

### Veo 3.1 (Version Future)
| Modèle | Fonctionnalité | Résolution | Prix |
|--------|----------------|------------|------|
| **Veo 3.1** | Vidéo seule | 720p/1080p | **$0.20/seconde** |
| **Veo 3.1** | Vidéo + Audio | 720p/1080p | **$0.40/seconde** |
| **Veo 3.1 Fast** | Vidéo seule | 720p/1080p | **$0.10/seconde** |
| **Veo 3.1 Fast** | Vidéo + Audio | 720p/1080p | **$0.15/seconde** |

### Google Cloud Text-to-Speech (TTS)
**Note:** Tarifs non listés dans le document Vertex AI. Basé sur documentation Google Cloud TTS:
- **Standard voices:** ~$4.00 par million de caractères
- **WaveNet/Neural2 voices:** ~$16.00 par million de caractères
- **Gemini 2.5 Pro TTS (Rasalgethi):** Estimé ~$16.00-20.00 par million de caractères

### Whisper
- **Open-source:** Gratuit (coût compute inclus dans Cloud Functions)

### Storage & Compute
- **Cloud Storage:** ~$0.02/GB/mois
- **Cloud Functions:** Inclus dans temps d'exécution
- **Firestore:** ~$0.06 par 100K reads/writes

---

## 🎬 SCÉNARIO VIDÉO TYPE

### Hypothèses
- **Thème:** "Les mystères de l'Égypte ancienne"
- **Script:** 8 scènes (V1) ou 5 blocs (V2)
- **Durée cible:** 64-80 secondes
- **Format:** 9:16 (TikTok/Shorts)

---

## 💸 V1 ACTUELLE - COÛTS DÉTAILLÉS

### 1. Agent Script (Gemini 2.5 Pro)

**Prompt d'entrée:** ~1,500 tokens
```
- Instructions système: 800 tokens
- Thème utilisateur: 50 tokens
- Contraintes format: 650 tokens
```

**Sortie générée:** ~2,500 tokens
```
- 8 scènes complètes
- VISUEL + VOIX OFF par scène
- ~300 tokens par scène
```

**Coût Script:**
- Entrée: 1,500 tokens × $1.25/M = **$0.001875**
- Sortie: 2,500 tokens × $10.00/M = **$0.025000**
- **Total Script: $0.0269** (~$0.03)

---

### 2. Agent Audio (Google TTS Gemini 2.5 Pro)

**Texte narration:** ~800 mots = ~4,000 caractères

**Calcul:**
```
8 scènes × ~100 mots/scène = 800 mots
800 mots × 5 caractères/mot = 4,000 caractères
```

**Coût Audio (Gemini 2.5 Pro TTS):**
- 4,000 caractères × $18.00/M caractères = **$0.072**

**Alternative (Neural2 voices):**
- 4,000 caractères × $16.00/M caractères = **$0.064**

**Coût conservateur:** **$0.07**

---

### 3. Agent Vidéo (Veo 3.0)

**Configuration:**
- 8 clips en parallèle
- 4 secondes par clip
- Format 9:16 (1080p)
- Vidéo SEULE (pas d'audio généré)

**Coût Vidéo:**
- 8 clips × 4 secondes = 32 secondes
- 32 secondes × $0.20/seconde = **$6.40**

---

### 4. Agent Assembleur (Whisper + FFmpeg)

**Composants:**
- Whisper transcription: Gratuit (open-source)
- FFmpeg processing: Gratuit (open-source)
- Compute (Cloud Function 4Gi, 540s): ~$0.01
- Storage temporaire: Négligeable

**Coût Assemblage:** **$0.01**

---

### 5. Infrastructure & Overhead

**Firestore:**
- 1 write video_status création: $0.00001
- 8 updates clips status: $0.00008
- 1 update final status: $0.00001
- **Total Firestore:** $0.0001

**Cloud Storage:**
- script_theme.txt: ~3KB
- audio_theme.mp3: ~500KB
- 8 clips vidéo: 8 × ~5MB = 40MB
- final_video.mp4: ~45MB
- **Total Storage:** ~85MB × $0.02/GB/mois = **$0.0017/mois**

**Cloud Functions (exécution):**
- Script agent: ~30s
- Audio agent: ~20s
- Video agent: ~10s (lancement parallèle)
- Monitor (polling): ~10min total
- Assembleur: ~120s
- **Total Compute:** ~$0.02

**Total Infrastructure:** **$0.03**

---

## 📊 V1 TOTAL PAR VIDÉO

| Composant | Coût |
|-----------|------|
| Script (Gemini 2.5 Pro) | $0.03 |
| Audio (TTS Gemini) | $0.07 |
| Vidéo (Veo 3.0 - 32s) | $6.40 |
| Assemblage (Whisper) | $0.01 |
| Infrastructure | $0.03 |
| **TOTAL V1** | **$6.54** |

### Breakdown Pourcentage
- **Veo 3.0:** 97.9% du coût
- **TTS:** 1.1%
- **Gemini:** 0.5%
- **Autres:** 0.5%

---

## 💸 V2 PLANIFIÉE (Veo 3.1) - COÛTS DÉTAILLÉS

### Scénario 1: Veo 3.1 Standard (Qualité Maximale)

#### 1. Agent Script (Gemini 2.5 Pro)
**Même coût que V1:** **$0.03**

#### 2. Agent Vidéo Veo 3.1 (Vidéo + Audio Natif)

**Configuration:**
- Bloc initial: 8 secondes
- Extensions: 4 blocs × 7 secondes = 28 secondes
- **Durée totale:** 36 secondes

**Note:** Extensions limitées à 720p selon documentation Veo.

**Coût Vidéo + Audio (1080p initial + 720p extensions):**
```
Bloc 1 (8s, 1080p avec audio): 8s × $0.40/s = $3.20
Blocs 2-5 (28s, 720p avec audio): 28s × $0.40/s = $11.20
```
**Total Veo 3.1:** **$14.40**

**Alternative (vidéo seule, extraction audio après):**
```
36 secondes × $0.20/s = $7.20
```
Mais on perd l'audio natif synchronisé !

#### 3. Agent Assembleur
**Simplifié:**
- Extraction audio: FFmpeg (gratuit)
- Whisper sous-titres: Gratuit
- Compute: ~$0.01

**Coût Assemblage:** **$0.01**

#### 4. Infrastructure
**Même que V1:** **$0.03**

### V2 Scénario 1 TOTAL

| Composant | Coût |
|-----------|------|
| Script (Gemini 2.5 Pro) | $0.03 |
| Audio (intégré Veo 3.1) | $0.00 |
| Vidéo + Audio (Veo 3.1 - 36s) | $14.40 |
| Assemblage (Whisper) | $0.01 |
| Infrastructure | $0.03 |
| **TOTAL V2 Standard** | **$14.47** |

---

### Scénario 2: Veo 3.1 Fast (Économique)

**Configuration:**
- Même structure: 36 secondes total
- Veo 3.1 Fast avec audio natif

**Coût Vidéo + Audio:**
```
36 secondes × $0.15/s = $5.40
```

### V2 Scénario 2 TOTAL

| Composant | Coût |
|-----------|------|
| Script (Gemini 2.5 Pro) | $0.03 |
| Audio (intégré Veo 3.1 Fast) | $0.00 |
| Vidéo + Audio (Veo 3.1 Fast - 36s) | $5.40 |
| Assemblage (Whisper) | $0.01 |
| Infrastructure | $0.03 |
| **TOTAL V2 Fast** | **$5.47** |

---

### Scénario 3: Vidéo Plus Longue (80 secondes)

**Pour atteindre 64-80s avec Veo 3.1:**

**Structure:**
- Bloc initial: 8s
- Extensions: 10 blocs × 7s = 70s
- **Total:** 78 secondes

**Coût Veo 3.1 Standard + Audio:**
```
78 secondes × $0.40/s = $31.20
```

**Coût Veo 3.1 Fast + Audio:**
```
78 secondes × $0.15/s = $11.70
```

### V2 Scénario 3 TOTAL (78s)

| Version | Script | Veo 3.1 | Assemblage | Infra | **TOTAL** |
|---------|--------|---------|------------|-------|-----------|
| **Standard** | $0.03 | $31.20 | $0.01 | $0.03 | **$31.27** |
| **Fast** | $0.03 | $11.70 | $0.01 | $0.03 | **$11.77** |

---

## 🔄 STRATÉGIE HYBRIDE (Recommandée)

### Optimisation Coût/Qualité

**Principe:** Utiliser Veo 3.0 (V1) pour clips courts, Veo 3.1 Fast pour vidéos longues

**Calcul pour vidéo 64s:**

#### Option A: Veo 3.0 (8 clips × 8s)
```
Vidéo: 64s × $0.20/s = $12.80
Audio TTS: $0.07
Total: $12.87 + overhead = $12.94
```

#### Option B: Veo 3.1 Fast (1 vidéo 64s)
```
Vidéo + Audio: 64s × $0.15/s = $9.60
Total: $9.60 + overhead = $9.67
```

**Économie Option B:** **$3.27/vidéo (25% moins cher)**

---

## 📈 COMPARAISON GLOBALE

### Tableau Récapitulatif (Vidéo ~36-40s)

| Version | Modèle | Durée | Coût Total | Qualité Audio | Sync |
|---------|--------|-------|------------|---------------|------|
| **V1 Actuelle** | Veo 3.0 + TTS | 32s | **$6.54** | 🤖 TTS | ⚠️ Approx |
| **V2 Standard** | Veo 3.1 | 36s | **$14.47** | 🎤 Natif | ✅ Parfait |
| **V2 Fast** | Veo 3.1 Fast | 36s | **$5.47** | 🎤 Natif | ✅ Parfait |

### Tableau Récapitulatif (Vidéo ~64-80s)

| Version | Modèle | Durée | Coût Total | Qualité Audio | Sync |
|---------|--------|-------|------------|---------------|------|
| **V1 Actuelle** | Veo 3.0 + TTS | 64s | **$12.94** | 🤖 TTS | ⚠️ Approx |
| **V2 Standard** | Veo 3.1 | 78s | **$31.27** | 🎤 Natif | ✅ Parfait |
| **V2 Fast** | Veo 3.1 Fast | 78s | **$11.77** | 🎤 Natif | ✅ Parfait |

---

## 💡 RECOMMANDATIONS

### 1. Court Terme (Maintenir V1)
- **Coût:** $6.54/vidéo (32s)
- **Avantages:** Prix attractif pour vidéos courtes
- **Inconvénients:** Audio TTS robotique, sync imparfait

### 2. Migration V2 Fast (Recommandé)
- **Coût:** $5.47/vidéo (36s) ou $11.77/vidéo (78s)
- **Avantages:**
  - **16% moins cher** que V1 pour durées équivalentes
  - Audio natif synchronisé
  - Qualité cinématographique
  - Dialogues réalistes
- **Inconvénients:** Légèrement plus long à générer

### 3. Migration V2 Standard (Premium)
- **Coût:** $14.47/vidéo (36s) ou $31.27/vidéo (78s)
- **Avantages:** Qualité maximale
- **Inconvénients:** **2.2x plus cher** que V1

---

## 🎯 STRATÉGIE OPTIMALE PAR CAS D'USAGE

### Cas 1: Budget Contraint
**Solution:** **V2 Fast (Veo 3.1 Fast)**
- Coût: $5.47 - $11.77 selon durée
- Qualité audio natif
- Meilleur ROI

### Cas 2: Qualité Maximale
**Solution:** **V2 Standard (Veo 3.1)**
- Coût: $14.47 - $31.27 selon durée
- Qualité cinématographique
- Pour contenus premium

### Cas 3: Volume Élevé (>100 vidéos/mois)
**Solution:** **Hybride**
```python
if video_duration <= 40:
    use_veo_31_fast()  # $5-6/vidéo
else:
    use_veo_30_multi_clips()  # $12-13/vidéo
```

---

## 📊 PROJECTIONS BUDGÉTAIRES

### Scénario: 100 vidéos/mois

| Version | Coût/vidéo | Coût/mois | Coût/an |
|---------|------------|-----------|---------|
| **V1 Actuelle (32s)** | $6.54 | $654 | $7,848 |
| **V2 Fast (36s)** | $5.47 | $547 | $6,564 |
| **V2 Fast (78s)** | $11.77 | $1,177 | $14,124 |
| **V2 Standard (36s)** | $14.47 | $1,447 | $17,364 |

**Économie annuelle V2 Fast vs V1:** **$1,284/an** (16%)

---

## 🚨 POINTS D'ATTENTION

### 1. Pricing Veo 3.1 Extensions
⚠️ **Les extensions successives (7s) sont limitées à 720p** selon la documentation.  
→ Impact sur qualité pour vidéos longues

### 2. Coût Variable selon Durée
📈 **Veo 3.1 facture à la seconde:** Plus la vidéo est longue, plus c'est cher  
→ Optimiser la longueur du script (5-6 blocs max = 36-43s)

### 3. Google TTS Pricing
⚠️ **Tarifs TTS non confirmés dans doc Vertex AI**  
→ Estimation conservatrice utilisée ($0.07/vidéo)

### 4. Compute Costs
✅ **Cloud Functions inclus dans calculs**  
→ Overhead infrastructure déjà comptabilisé

---

## ✅ CONCLUSION & RECOMMANDATION FINALE

### Migration Recommandée: **Veo 3.1 Fast**

**Pourquoi ?**
1. ✅ **16% moins cher** que V1 (durées équivalentes)
2. ✅ **Audio natif synchronisé** (fini les problèmes TTS)
3. ✅ **Qualité supérieure** (dialogues réalistes)
4. ✅ **Simplicité** (1 vidéo fluide vs 8 clips)
5. ✅ **Scalable** (coût prévisible par seconde)

**Pour qui ?**
- Utilisateurs avec quota 2 vidéos/mois → **Pas d'impact budget**
- Admins illimités → **Économie significative sur volume**
- Production régulière → **Meilleur ROI**

**Plan de migration:**
1. **Phase 1:** Tester Veo 3.1 Fast avec 10 vidéos pilotes
2. **Phase 2:** Comparer qualité/coût vs V1
3. **Phase 3:** Déployer si validation positive
4. **Phase 4:** Maintenir V1 en fallback pour cas edge

---

**Dernière mise à jour:** 31 Décembre 2025  
**Source:** Documentation officielle Vertex AI Pricing
