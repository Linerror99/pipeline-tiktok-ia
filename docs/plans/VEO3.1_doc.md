Passer au contenu principal
ai.google.dev utilise des cookies Google afin de fournir ses services, d'en améliorer la qualité et d'analyser le trafic. En savoir plus

J'ai compris
Gemini API
Recherche
/


Language
Obtenir une clé API
Liste de recettes
Communauté
Connexion
Docs
Documentation de référence de l'API

 Cette page a été traduite par l'API Cloud Translation.
Switch to English
Accueil
Gemini API
Docs
Générer des vidéos avec Veo 3.1 dans l'API Gemini

content_copy


Nous avons mis à jour nos Conditions d'utilisation.

Veo 3.1 est le modèle de pointe de Google pour générer des vidéos de huit secondes en 720p ou 1080p de haute fidélité, avec un réalisme époustouflant et un son généré de manière native. Vous pouvez accéder à ce modèle de manière programmatique à l'aide de l'API Gemini. Pour en savoir plus sur les variantes de modèles Veo disponibles, consultez la section Versions de modèle.

Veo 3.1 excelle dans un large éventail de styles visuels et cinématographiques, et propose plusieurs nouvelles fonctionnalités :

Extension de vidéo : étendez les vidéos qui ont été générées précédemment à l'aide de Veo.
Génération spécifique à une image : générez une vidéo en spécifiant la première et la dernière image.
Orientation basée sur des images : utilisez jusqu'à trois images de référence pour guider le contenu de votre vidéo générée.
Pour en savoir plus sur la rédaction de requêtes textuelles efficaces pour la génération de vidéos, consultez le guide des requêtes Veo.

Génération de vidéos à partir de texte
Choisissez un exemple pour découvrir comment générer une vidéo avec des dialogues, un réalisme cinématographique ou une animation créative :

Dialogues et effets sonores Réalisme cinématographique Animation créative

Python
JavaScript
Go
REST

import time
from google import genai
from google.genai import types

client = genai.Client()

prompt = """A close up of two people staring at a cryptic drawing on a wall, torchlight flickering.
A man murmurs, 'This must be it. That's the secret code.' The woman looks at him and whispering excitedly, 'What did you find?'"""

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the generated video.
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("dialogue_example.mp4")
print("Generated video saved to dialogue_example.mp4")


Génération de vidéos à partir d'images
Le code suivant montre comment générer une image à l'aide de Gemini 2.5 Flash Image (alias Nano Banana), puis comment utiliser cette image comme frame de départ pour générer une vidéo avec Veo 3.1.

Python
JavaScript
Go

import time
from google import genai

client = genai.Client()

prompt = "Panning wide shot of a calico kitten sleeping in the sunshine"

# Step 1: Generate an image with Nano Banana.
image = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=prompt,
    config={"response_modalities":['IMAGE']}
)

# Step 2: Generate video with Veo 3.1 using the image.
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    image=image.parts[0].as_image(),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3_with_image_input.mp4")
print("Generated video saved to veo3_with_image_input.mp4")
Utiliser des images de référence
Remarque : Cette fonctionnalité n'est disponible que pour les modèles Veo 3.1.
Veo 3.1 accepte désormais jusqu'à trois images de référence pour guider le contenu de votre vidéo générée. Fournissez des images d'une personne, d'un personnage ou d'un produit pour préserver l'apparence du sujet dans la vidéo générée.

Par exemple, l'utilisation de ces trois images générées avec Nano Banana comme références avec une requête bien rédigée crée la vidéo suivante :

`dress_image`	`woman_image`	`glasses_image`
Robe flamant rose haute couture avec des couches de plumes roses et fuchsia	Belle femme aux cheveux foncés et aux yeux brun chaud	Lunettes de soleil roses en forme de cœur
Python

import time
from google import genai

client = genai.Client()

prompt = "The video opens with a medium, eye-level shot of a beautiful woman with dark hair and warm brown eyes. She wears a magnificent, high-fashion flamingo dress with layers of pink and fuchsia feathers, complemented by whimsical pink, heart-shaped sunglasses. She walks with serene confidence through the crystal-clear, shallow turquoise water of a sun-drenched lagoon. The camera slowly pulls back to a medium-wide shot, revealing the breathtaking scene as the dress's long train glides and floats gracefully on the water's surface behind her. The cinematic, dreamlike atmosphere is enhanced by the vibrant colors of the dress against the serene, minimalist landscape, capturing a moment of pure elegance and high-fashion fantasy."

dress_reference = types.VideoGenerationReferenceImage(
  image=dress_image, # Generated separately with Nano Banana
  reference_type="asset"
)

sunglasses_reference = types.VideoGenerationReferenceImage(
  image=glasses_image, # Generated separately with Nano Banana
  reference_type="asset"
)

woman_reference = types.VideoGenerationReferenceImage(
  image=woman_image, # Generated separately with Nano Banana
  reference_type="asset"
)

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    config=types.GenerateVideosConfig(
      reference_images=[dress_reference, glasses_reference, woman_reference],
    ),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3.1_with_reference_images.mp4")
print("Generated video saved to veo3.1_with_reference_images.mp4")


Utiliser les première et dernière images
Remarque : Cette fonctionnalité n'est disponible que pour les modèles Veo 3.1.
Veo 3.1 vous permet de créer des vidéos à l'aide de l'interpolation ou en spécifiant les première et dernière images de la vidéo. Pour savoir comment rédiger des requêtes textuelles efficaces pour la génération de vidéos, consultez le guide des requêtes Veo.

Python

import time
from google import genai

client = genai.Client()

prompt = "A cinematic, haunting video. A ghostly woman with long white hair and a flowing dress swings gently on a rope swing beneath a massive, gnarled tree in a foggy, moonlit clearing. The fog thickens and swirls around her, and she slowly fades away, vanishing completely. The empty swing is left swaying rhythmically on its own in the eerie silence."

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    image=first_image, # Generated separately with Nano Banana
    config=types.GenerateVideosConfig(
      last_frame=last_image # Generated separately with Nano Banana
    ),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3.1_with_interpolation.mp4")
print("Generated video saved to veo3.1_with_interpolation.mp4")
`first_image`	`last_image`	veo3.1_with_interpolation.mp4
Une femme fantomatique aux longs cheveux blancs et à la robe fluide se balance doucement sur une balançoire à corde.	La femme fantomatique disparaît de la balançoire	Vidéo cinématographique et envoûtante d&#39;une femme étrange disparaissant d&#39;une balançoire dans la brume
Prolonger des vidéos Veo
Remarque : Cette fonctionnalité n'est disponible que pour les modèles Veo 3.1.
Utilisez Veo 3.1 pour prolonger de sept secondes et jusqu'à 20 fois les vidéos que vous avez générées avec Veo.

Limites concernant les vidéos d'entrée :

Les vidéos générées par Veo ne peuvent pas durer plus de 141 secondes.
L'API Gemini n'accepte que les extensions vidéo pour les vidéos générées par Veo.
La vidéo doit provenir d'une génération précédente, comme operation.response.generated_videos[0].video.
Les vidéos d'entrée doivent avoir une certaine durée, un certain format et certaines dimensions :
Format : 9:16 ou 16:9
Résolution : 720p
Durée de la vidéo : 141 secondes ou moins
L'extension génère une seule vidéo combinant la vidéo fournie par l'utilisateur et la vidéo étendue générée (jusqu'à 148 secondes de vidéo).

Cet exemple prend une vidéo générée par Veo, présentée ici avec sa requête d'origine, et l'étend à l'aide du paramètre video et d'une nouvelle requête :

Prompt	Résultat : butterfly_video
Un papillon en origami bat des ailes et s'envole par la porte-fenêtre pour rejoindre le jardin.	Un papillon en origami bat des ailes et s&#39;envole par la porte-fenêtre dans le jardin.
Python

import time
from google import genai

client = genai.Client()

prompt = "Track the butterfly into the garden as it lands on an orange origami flower. A fluffy white puppy runs up and gently pats the flower."

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=operation.response.generated_videos[0].video, # This must be a video from a previous generation
    prompt=prompt,
    config=types.GenerateVideosConfig(
        number_of_videos=1,
        resolution="720p"
    ),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the video.
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("veo3.1_extension.mp4")
print("Generated video saved to veo3.1_extension.mp4")


Pour savoir comment rédiger des requêtes textuelles efficaces pour la génération de vidéos, consultez le guide des requêtes Veo.

Gérer les opérations asynchrones
La génération de vidéos est une tâche gourmande en ressources de calcul. Lorsque vous envoyez une requête à l'API, elle lance un job de longue durée et renvoie immédiatement un objet operation. Vous devez ensuite interroger l'API jusqu'à ce que la vidéo soit prête, ce qui est indiqué par l'état done défini sur "true".

Le cœur de ce processus est une boucle d'interrogation qui vérifie régulièrement l'état du job.

Python
JavaScript

import time
from google import genai
from google.genai import types

client = genai.Client()

# After starting the job, you get an operation object.
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="A cinematic shot of a majestic lion in the savannah.",
)

# Alternatively, you can use operation.name to get the operation.
operation = types.GenerateVideosOperation(name=operation.name)

# This loop checks the job status every 10 seconds.
while not operation.done:
    time.sleep(10)
    # Refresh the operation object to get the latest status.
    operation = client.operations.get(operation)

# Once done, the result is in operation.response.
# ... process and download your video ...
Paramètres et spécifications de l'API Veo
Voici les paramètres que vous pouvez définir dans votre requête API pour contrôler le processus de génération de vidéos.

Paramètre	Description	Veo 3.1 et Veo 3.1 Fast	Veo 3 et Veo 3 Fast	Veo 2
prompt	Description textuelle de la vidéo. Compatible avec les repères audio.	string	string	string
negativePrompt	Texte décrivant ce qu'il ne faut pas inclure dans la vidéo.	string	string	string
image	Image initiale à animer.	Objet Image	Objet Image	Objet Image
lastFrame	Image finale pour une vidéo d'interpolation à la transition. Doit être utilisé avec le paramètre image.	Objet Image	Objet Image	Objet Image
referenceImages	Jusqu'à trois images à utiliser comme références de style et de contenu.	Objet VideoGenerationReferenceImage (Veo 3.1 uniquement)	n/a	n/a
video	Vidéo à utiliser pour l'extension vidéo.	Objet Video	n/a	n/a
aspectRatio	Format de la vidéo.	"16:9" (par défaut, 720p et 1080p),
"9:16"(720p et 1080p)

"16:9" (par défaut, 720p et 1080p),
"9:16" (720p et 1080p)	"16:9" (par défaut, 720p),
"9:16" (720p)
resolution	Format de la vidéo.	"720p" (par défaut),
"1080p" (ne prend en charge que les durées de 8 s)

"720p" uniquement pour l'extension	"720p" (par défaut),
"1080p" (16:9 uniquement)	Non compatible
durationSeconds	Durée de la vidéo générée.	"4", "6", "8".

doit être défini sur "8" lorsque vous utilisez une extension ou une interpolation (formats 16:9 et 9:16 pris en charge), et lorsque vous utilisez referenceImages (format 16:9 uniquement pris en charge).	"4", "6", "8"	"5", "6", "8"
personGeneration	Contrôle la génération de personnes.
(Consultez la section Limites pour connaître les restrictions régionales.)	Texte vers vidéo et extension :
"allow_all" uniquement
Image vers vidéo, interpolation et images de référence :
"allow_adult" uniquement	Texte-vers-vidéo :
"allow_all" uniquement
Image-vers-vidéo :
"allow_adult" uniquement	Texte-vers-vidéo :
"allow_all", "allow_adult", "dont_allow"
Image-vers-vidéo :
"allow_adult" et "dont_allow"
Notez que le paramètre seed est également disponible pour les modèles Veo 3. Cela ne garantit pas le déterminisme, mais l'améliore légèrement.

Vous pouvez personnaliser la génération de vos vidéos en définissant des paramètres dans votre requête. Par exemple, vous pouvez spécifier negativePrompt pour guider le modèle.

Python
JavaScript
Go
REST

import time
from google import genai
from google.genai import types

client = genai.Client()

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="A cinematic shot of a majestic lion in the savannah.",
    config=types.GenerateVideosConfig(negative_prompt="cartoon, drawing, low quality"),
)

# Poll the operation status until the video is ready.
while not operation.done:
    print("Waiting for video generation to complete...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download the generated video.
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("parameters_example.mp4")
print("Generated video saved to parameters_example.mp4")
Guide sur les requêtes Veo
Cette section contient des exemples de vidéos que vous pouvez créer à l'aide de Veo. Elle vous montre également comment modifier les requêtes pour obtenir des résultats différents.

Filtres de sécurité
Veo applique des filtres de sécurité à Gemini pour s'assurer que les vidéos générées et les photos importées ne contiennent pas de contenu offensant. Les requêtes qui ne respectent pas nos conditions d'utilisation et nos consignes sont bloquées.

Principes de base concernant l'écriture de requêtes
Les bons prompts sont descriptifs et clairs. Pour exploiter tout le potentiel de Veo, commencez par identifier votre idée principale, affinez-la en ajoutant des mots clés et des modificateurs, et intégrez une terminologie spécifique aux vidéos dans vos requêtes.

Les éléments suivants doivent figurer dans votre requête :

Objet : l'objet, la personne, l'animal ou le paysage que vous souhaitez voir dans votre vidéo, par exemple paysage urbain, nature, véhicules ou chiots.
Action : ce que fait le sujet (par exemple, marcher, courir ou tourner la tête).
Style : spécifiez l'orientation créative à l'aide de mots clés spécifiques au style de film, comme science-fiction, film d'horreur, film noir ou des styles d'animation comme dessin animé.
Positionnement et mouvement de la caméra : [Facultatif] Contrôlez l'emplacement et le mouvement de la caméra à l'aide de termes tels que vue aérienne, à hauteur des yeux, vue de dessus, travelling ou vue de dessous.
Composition : [facultatif] cadrage du plan, par exemple plan large, plan rapproché, plan séquence ou plan à deux.
Effets de mise au point et d'objectif : [facultatif] utilisez des termes tels que faible profondeur de champ, forte profondeur de champ, flou artistique, objectif macro et objectif grand-angle pour obtenir des effets visuels spécifiques.
Ambiance : [facultatif] comment la couleur et la lumière contribuent-elles à la scène (par exemple, tons bleus, nuit ou tons chauds) ?
Autres conseils pour rédiger des requêtes
Utilisez un langage descriptif : utilisez des adjectifs et des adverbes pour donner une image claire à Veo.
Améliorer les détails du visage : spécifiez que les détails du visage doivent être au centre de la photo, par exemple en utilisant le mot portrait dans la requête.
Pour des stratégies de requête plus complètes, consultez Présentation de la conception des requêtes.

Demande de contenu audio
Avec Veo 3, vous pouvez fournir des indications pour les effets sonores, les bruits ambiants et les dialogues. Le modèle capture la nuance de ces signaux pour générer une bande-son synchronisée.

Dialogue : utilisez des guillemets pour les paroles spécifiques. (Exemple : "Ce doit être la clé", murmura-t-il.)
Effets sonores : décrivez explicitement les sons. (Exemple : pneus qui crissent fortement, moteur qui rugit.)
Bruit ambiant : décrivez l'environnement sonore. (Exemple : Un léger bourdonnement étrange résonne en arrière-plan.)
Ces vidéos montrent comment demander à Veo 3 de générer de l'audio avec des niveaux de détail croissants.

Prompt (Requête)	Résultat généré
Plus de détails (dialogues et ambiance)
Plan large d'une forêt brumeuse du nord-ouest du Pacifique. Deux randonneurs épuisés, un homme et une femme, se frayent un chemin à travers les fougères. L'homme s'arrête brusquement et fixe un arbre. Gros plan : des griffures profondes et récentes sont visibles sur l'écorce de l'arbre. Homme : (Main sur son couteau de chasse) "Ce n'est pas un ours ordinaire." Femme : (Voix serrée par la peur, scrutant les bois) "Alors, qu'est-ce que c'est ?" Une écorce rugueuse, des brindilles qui craquent, des pas sur la terre humide. Un oiseau solitaire gazouille.	Deux personnes dans les bois rencontrent des traces d&#39;ours.
Moins de détails (dialogues)
Animation en papier découpé. Nouveau bibliothécaire : "Où rangez-vous les livres interdits ?" Ancien conservateur : "Non. Ils nous gardent."	Bibliothécaires animés discutant de livres interdits
Essayez ces requêtes pour écouter l'audio ! Essayer Veo 3

Utiliser des images de référence dans les requêtes
Vous pouvez utiliser une ou plusieurs images comme entrées pour guider vos vidéos générées, à l'aide des fonctionnalités image-to-video de Veo. Veo utilise l'image d'entrée comme frame initiale. Sélectionnez une image qui se rapproche le plus de ce que vous imaginez comme première scène de votre vidéo pour animer des objets du quotidien, donner vie à des dessins et peintures, et ajouter du mouvement et du son à des scènes de nature.

Prompt (Requête)	Résultat généré
Image d'entrée (générée par Nano Banana)
Macrophotographie hyperréaliste de minuscules surfeurs miniatures chevauchant les vagues de l'océan dans un lavabo rustique en pierre. Un robinet en laiton ancien est ouvert, créant ainsi la vague perpétuelle. Surréaliste, fantaisiste, éclairage naturel lumineux.	Minuscules surfeurs miniatures chevauchant les vagues de l&#39;océan dans un lavabo rustique en pierre.
Vidéo générée par Veo 3.1
Vidéo macro surréaliste et cinématographique. De minuscules surfeurs chevauchent des vagues perpétuelles et ondulantes dans un lavabo en pierre. Un robinet en laiton vintage ouvert génère des vagues infinies. La caméra effectue un lent panoramique sur la scène fantaisiste et ensoleillée, tandis que les figurines miniatures sculptent l'eau turquoise avec expertise.	Minuscules surfeurs faisant le tour des vagues dans un lavabo.
Veo 3.1 vous permet de faire référence à des images ou à des ingrédients pour orienter le contenu de votre vidéo générée. Fournissez jusqu'à trois images de composants d'une même personne, d'un même personnage ou d'un même produit. Veo préserve l'apparence du sujet dans la vidéo générée.

Prompt (Requête)	Résultat généré
Image de référence (générée par Nano Banana)
Une baudroie des abysses se cache dans les eaux profondes et sombres, les dents à découvert et l'appât lumineux.	Une baudroie sombre et lumineuse
Image de référence (générée par Nano Banana)
Un costume de princesse rose pour enfant avec une baguette et une tiare, sur un fond uni.	Costume de princesse rose pour enfant
Vidéo générée par Veo 3.1
Crée une version dessin animé amusante du poisson portant le costume, en train de nager et d'agiter la baguette.	Un poisson-pêcheur portant un costume de princesse
Avec Veo 3.1, vous pouvez également générer des vidéos en spécifiant la première et la dernière image.

Prompt (Requête)	Résultat généré
Première image (générée par Nano Banana)
Image photoréaliste de haute qualité montrant un chat roux au volant d'une voiture de course décapotable rouge sur la Côte d'Azur.	Un chat roux conduisant une voiture de course décapotable rouge
Dernière image (générée par Nano Banana)
Montre ce qui se passe lorsque la voiture décolle d'une falaise.	Un chat roux au volant d&#39;une décapotable rouge tombe d&#39;une falaise
Vidéo générée (par Veo 3.1)
Facultatif	Un chat saute d&#39;une falaise et s&#39;envole
Cette fonctionnalité vous permet de contrôler précisément la composition de votre plan en définissant l'image de début et de fin. Importez une image ou utilisez un frame d'une vidéo générée précédemment pour vous assurer que votre scène commence et se termine exactement comme vous l'imaginez.

Requêtes pour l'extension
Pour étendre une vidéo générée par Veo avec Veo 3.1, utilisez la vidéo comme entrée, avec un prompt textuel facultatif. L'option "Prolonger" finalise la dernière seconde ou les 24 dernières images de votre vidéo et poursuit l'action.

Notez que la voix ne peut pas être étendue efficacement si elle n'est pas présente dans la dernière seconde de la vidéo.

Prompt (Requête)	Résultat généré
Vidéo d'entrée (générée par Veo 3.1)
Le parapentiste décolle du sommet de la montagne et commence à planer au-dessus des vallées fleuries en contrebas.	Parapentiste décollant du sommet d&#39;une montagne
Vidéo de sortie (générée par Veo 3.1)
Étend cette vidéo avec le parapentiste qui descend lentement.	Un parapentiste décolle du sommet d&#39;une montagne, puis descend lentement
Exemples de requêtes et de résultats
Cette section présente plusieurs requêtes, en soulignant comment les détails descriptifs peuvent améliorer le résultat de chaque vidéo.

Glaçons
Cette vidéo vous montre comment utiliser les éléments des principes de base de la rédaction de requêtes dans votre requête.

Prompt (Requête)	Résultat généré
Gros plan (composition) de stalactites de glace (sujet) en train de fondre sur une paroi rocheuse gelée (contexte) avec des tons bleus froids (ambiance), zoom avant (mouvement de caméra) en conservant les détails des gouttes d'eau (action).	Des stalactites qui fondent sur un fond bleu.
Un homme au téléphone
Ces vidéos montrent comment réviser votre requête en ajoutant des détails de plus en plus spécifiques pour que Veo affine le résultat à votre guise.

Prompt (Requête)	Résultat généré
Moins de détails
La caméra effectue un travelling pour montrer un gros plan d'un homme désespéré portant un trench vert. Il passe un appel sur un téléphone mural à cadran avec un néon vert. Il ressemble à une scène de film.	Homme parlant au téléphone.
Plus de détails
Un gros plan cinématographique suit un homme désespéré portant un trench-coat vert usé alors qu'il compose un numéro sur un téléphone à cadran fixé sur un mur de briques rugueux, baigné dans la lueur étrange d'un néon vert. La caméra se rapproche, révélant la tension dans sa mâchoire et le désespoir gravé sur son visage alors qu'il s'efforce de passer l'appel. La faible profondeur de champ se concentre sur ses sourcils froncés et le téléphone noir à cadran, floutant l'arrière-plan en une mer de couleurs néon et d'ombres indistinctes, créant un sentiment d'urgence et d'isolement.	Homme parlant au téléphone
Léopard des neiges
Prompt (Requête)	Résultat généré
Requête simple :
Une créature mignonne avec une fourrure de léopard des neiges marche dans une forêt hivernale, rendu de style dessin animé 3D.	Le léopard des neiges est léthargique.
Requête détaillée :
Crée une courte scène animée en 3D dans un style cartoon joyeux. Une créature mignonne avec une fourrure semblable à celle d'un léopard des neiges, de grands yeux expressifs et une forme arrondie et amicale gambade joyeusement dans une forêt hivernale fantaisiste. La scène doit représenter des arbres arrondis et enneigés, de doux flocons de neige qui tombent et une lumière chaude du soleil qui filtre à travers les branches. Les mouvements rebondissants de la créature et son large sourire doivent exprimer une joie pure. Opte pour un ton optimiste et chaleureux, avec des couleurs vives et gaies, et des animations ludiques.	Le léopard des neiges court plus vite.
Exemples par éléments de rédaction
Ces exemples vous montrent comment affiner vos requêtes en fonction de chaque élément de base.

Objet et contexte
Spécifiez le point focal principal (sujet) et l'arrière-plan ou l'environnement (contexte).

Prompt (Requête)	Résultat généré
Rendu architectural d'un immeuble d'appartements en béton blanc avec des formes organiques fluides, se fondant parfaitement dans une végétation luxuriante et des éléments futuristes	Espace réservé.
Un satellite flottant dans l'espace, avec la lune et quelques étoiles en arrière-plan.	Satellite flottant dans l&#39;atmosphère.
Action
Spécifiez ce que fait le sujet (par exemple, marcher, courir ou tourner la tête).

Prompt (Requête)	Résultat généré
Plan large d'une femme marchant le long de la plage, l'air satisfait et détendu, vers l'horizon au coucher du soleil.	Le coucher de soleil est absolument magnifique.
Style
Ajoutez des mots clés pour orienter la génération vers une esthétique spécifique (par exemple, surréaliste, vintage, futuriste, film noir).

Prompt (Requête)	Résultat généré
Style film noir, homme et femme marchant dans la rue, mystère, cinématographique, noir et blanc.	Le style film noir est absolument magnifique.
Mouvement de la caméra et composition
Précisez comment la caméra se déplace (vue subjective, vue aérienne, vue de drone en suivi) et comment le plan est cadré (plan large, gros plan, contre-plongée).

Prompt (Requête)	Résultat généré
Point de vue depuis une voiture ancienne roulant sous la pluie, Canada de nuit, style cinématographique.	Le coucher de soleil est absolument magnifique.
Gros plan sur un œil avec la ville reflétée dedans.	Le coucher de soleil est absolument magnifique.
Ambiance
Les palettes de couleurs et l'éclairage influencent l'ambiance. Essayez des termes comme "tons chauds orange sourd", "lumière naturelle", "lever du soleil" ou "tons bleus froids".

Prompt (Requête)	Résultat généré
Gros plan sur une fille tenant un adorable chiot golden retriever dans le parc, en plein soleil.	Un chiot dans les bras d&#39;une jeune fille.
Gros plan cinématographique d'une femme triste qui prend le bus sous la pluie, tons bleus froids, ambiance triste.	Une femme assise dans un bus a l&#39;air triste.
Requêtes négatives
Les requêtes négatives spécifient les éléments que vous ne souhaitez pas voir dans la vidéo.

❌ N'utilisez pas de mots ou d'expressions instructives comme pas de ou ne pas. (par exemple, "No walls" (Sans murs).
✅ Décrivez ce que vous ne souhaitez pas voir. (par exemple, "wall, frame").
Prompt (Requête)	Résultat généré
Sans prompt négatif :
Génère une courte animation stylisée d'un grand chêne solitaire dont les feuilles sont emportées par un vent violent… [tronqué]	Arbre avec des mots.
Avec une invite négative :
[Même invite]

Invite négative : arrière-plan urbain, structures artificielles, atmosphère sombre, orageuse ou menaçante.	Arbre sans mots négatifs.
Formats
Veo vous permet de spécifier le format de votre vidéo.

Prompt (Requête)	Résultat généré
Grand écran (16:9)
Crée une vidéo avec une vue de drone suivant un homme conduisant une décapotable rouge à Palm Springs dans les années 1970, avec une lumière chaude et de longues ombres.	Un homme conduit une décapotable rouge à Palm Springs, dans le style des années 1970.
Portrait (9:16)
Crée une vidéo mettant en avant le mouvement fluide d'une majestueuse cascade hawaïenne dans une forêt tropicale luxuriante. Mettez l'accent sur un débit d'eau réaliste, un feuillage détaillé et un éclairage naturel pour transmettre la tranquillité. Capturez l'eau vive, l'atmosphère brumeuse et la lumière du soleil filtrant à travers la canopée dense. Utilisez des mouvements de caméra fluides et cinématographiques pour mettre en valeur la cascade et ses environs. Adopte un ton paisible et réaliste, et transporte le spectateur dans la beauté sereine de la forêt tropicale hawaïenne.	Majestueuse cascade hawaïenne dans une forêt tropicale luxuriante
Limites
Latence des requêtes : min. 11 secondes, max. 6 minutes (pendant les heures de pointe).
Limites régionales : dans les régions de l'UE, du Royaume-Uni, de la Suisse et du Moyen-Orient et Afrique du Nord, les valeurs autorisées pour personGeneration sont les suivantes :
Veo 3 : allow_adult uniquement.
Veo 2 : dont_allow et allow_adult. La valeur par défaut est dont_allow.
Conservation des vidéos : les vidéos générées sont stockées sur le serveur pendant deux jours, après quoi elles sont supprimées. Pour enregistrer une copie locale, vous devez télécharger votre vidéo dans les deux jours suivant sa génération. Les vidéos étendues sont traitées comme des vidéos nouvellement générées.
Filigranes : les vidéos créées par Veo sont marquées par un filigrane à l'aide de SynthID, notre outil permettant d'ajouter un filigrane et d'identifier les contenus générés par IA. Les vidéos peuvent être validées à l'aide de la plate-forme de validation SynthID.
Sécurité : les vidéos générées sont soumises à des filtres de sécurité et à des processus de vérification de la mémorisation qui permettent d'atténuer les risques liés à la confidentialité, aux droits d'auteur et aux biais.
Erreur audio : il arrive que Veo 3.1 bloque la génération d'une vidéo en raison de filtres de sécurité ou d'autres problèmes de traitement de l'audio. Vous ne serez pas facturé si la génération de votre vidéo est bloquée.
Fonctionnalités du modèle
Fonctionnalité	Description	Veo 3.1 et Veo 3.1 Fast	Veo 3 et Veo 3 Fast	Veo 2
Audio	Génère l'audio avec la vidéo de manière native.	Génère l'audio avec la vidéo de manière native.	✔️ Toujours activé	❌ Mode silencieux uniquement
Modalités d'entrée	Type d'entrée utilisé pour la génération.	Texte-vers-vidéo, image-vers-vidéo, vidéo-vers-vidéo	Texte vers vidéo, image vers vidéo	Texte vers vidéo, image vers vidéo
Solution	Résolution de sortie de la vidéo.	720p et 1080p (8 s uniquement)

720p uniquement lorsque vous utilisez une extension vidéo.	720p et 1080p (16:9 uniquement)	720p
Fréquence d'images	Fréquence d'images de sortie de la vidéo.	24 ips	24 ips	24 ips
Durée de la vidéo	Durée de la vidéo générée.	8 secondes, 6 secondes, 4 secondes
8 secondes uniquement lorsque vous utilisez des images de référence	8 secondes	5 à 8 secondes
Vidéos par demande	Nombre de vidéos générées par requête.	1	1	1 ou 2
État et détails	Disponibilité des modèles et autres informations	Aperçu	Stable	Stable
Versions de modèle
Pour en savoir plus sur l'utilisation spécifique aux modèles Veo, consultez les pages Tarifs et Limites de débit.

Les versions Veo Fast permettent aux développeurs de créer des vidéos avec du son tout en conservant une qualité élevée et en optimisant la vitesse et les cas d'utilisation professionnels. Elles sont idéales pour les services de backend qui génèrent des annonces de manière programmatique, les outils de tests A/B rapides des concepts de création ou les applications qui doivent produire rapidement du contenu pour les réseaux sociaux.

Veo 3.1 (preview)
Veo 3.1 Fast (preview)
Veo 3
Veo 3 Fast
Veo 2
Propriété	Description
Code du modèle 
API Gemini

veo-3.1-generate-preview

Types de données acceptés
Entrée

Texte, image

Résultat

Vidéo avec audio

Limites de 
Saisie de texte

1 024 jetons

Vidéo de sortie

1

Dernière mise à jour	Septembre 2025
Étape suivante
Faites vos premiers pas avec l'API Veo 3.1 en faisant des tests dans le notebook Colab de démarrage rapide Veo et l'applet Veo 3.1.
Découvrez comment rédiger des requêtes encore plus efficaces grâce à notre présentation de la conception des requêtes.
Ce contenu vous a-t-il été utile ?

Envoyer des commentaires
Sauf indication contraire, le contenu de cette page est régi par une licence Creative Commons Attribution 4.0, et les échantillons de code sont régis par une licence Apache 2.0. Pour en savoir plus, consultez les Règles du site Google Developers. Java est une marque déposée d'Oracle et/ou de ses sociétés affiliées.

Dernière mise à jour le 2025/12/18 (UTC).

Conditions d'utilisation
Règles de confidentialité

Language
