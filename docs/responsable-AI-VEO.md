Passer au contenu principal
docs.cloud.google.com utilise des cookies Google afin de fournir ses services, d'en améliorer la qualité et d'analyser le trafic. En savoir plus

J'ai compris
Google Cloud Documentation
Domaines technologiques

Plus
Recherche
/
Console



Français

Vertex AI
Generative AI on Vertex AI
Guides
Documentation de référence de l'API
Vertex AI Cookbook
Galerie de requêtes
Ressources
Questions fréquentes
Tarifs
Filtrer

Home
Documentation
AI and ML
Vertex AI
Generative AI on Vertex AI
Guides
Ce contenu vous a-t-il été utile ?

Envoyer des commentairesGuide sur les prompts de génération de vidéos Veo sur Agent Platform



Veo offre une personnalisation infinie grâce aux requêtes textuelles. Ce guide explique comment modifier vos requêtes Veo pour obtenir différents résultats et effets.

Pour en savoir plus sur les bonnes pratiques, consultez Bonnes pratiques pour Veo sur la plate-forme Agent.

Filtres de sécurité
Veo applique des filtres de sécurité à l'ensemble de la plate-forme Agent pour s'assurer que les vidéos générées et les photos importées ne contiennent pas de contenu offensant. Par exemple, les requêtes qui ne respectent pas les Consignes relatives à l'IA responsable sont bloquées.

Si vous suspectez une utilisation abusive de Veo ou de tout résultat généré contenant du contenu inapproprié ou des informations inexactes, utilisez le formulaire Signaler une utilisation abusive sur Google Cloud.

Anatomie d'une requête Veo
Lorsque vous utilisez Veo pour générer des vidéos, l'utilisation des bons mots clés et de la bonne structure de requête aide le modèle à générer le contenu souhaité. Pour guider VEO vers le résultat souhaité, le plus efficace est de décomposer votre idée en éléments clés.

Les sections suivantes expliquent comment utiliser des éléments clés et des mots clés dans vos requêtes pour guider Veo lors de la génération de vidéos.

Vous n'avez pas besoin d'utiliser tous les éléments dans chaque requête, mais comprendre comment chacun d'eux fonctionne peut vous aider à les appliquer efficacement dans vos requêtes Veo.

Objet
Le sujet est le "qui" ou le "quoi" autour duquel tourne l'action de votre vidéo générée. La spécificité permet d'éviter les résultats génériques.

Voici quelques exemples de sujets que vous pouvez utiliser :

Personnes :

Descripteurs génériques : homme, femme, personne âgée

Professions spécifiques : "un détective chevronné", "un boulanger joyeux", "un astronaute futuriste"

Personnages historiques

Êtres mythiques : "une fée espiègle", "un chevalier stoïque"

Animaux ou créatures :

Races d'animaux spécifiques : "un chiot Golden Retriever joueur", "un aigle à tête blanche majestueux", "une panthère noire élégante"

Créatures fantastiques : "un dragon miniature aux écailles irisées", "un arbre parlant, sage et ancien"

Objets :

Objets du quotidien : "une machine à écrire vintage", "une tasse de café fumante", "un livre relié en cuir usé"

Véhicules : "une muscle car classique des années 1960", "un aéroglisseur futuriste", "un bateau pirate usé"

Formes abstraites : "sphères lumineuses", "structures cristallines"

Vous pouvez combiner des personnes, des animaux, des objets ou n'importe quelle combinaison de ces éléments dans une même vidéo (par exemple, "Un groupe d'amis diversifiés riant autour d'un feu de camp tandis qu'un renard curieux observe depuis l'ombre", "une scène de marché animée avec des vendeurs et des clients").

Exemple : La vidéo et la requête suivantes présentent des détails complexes avec plusieurs sujets :




"A hyper-realistic, cinematic portrait of a wise, androgynous shaman of
indeterminate age. Their weathered skin is etched with intricate, bioluminescent
circuit-like tattoos that pulse with a soft, cyan light. They are draped in
ceremonial robes woven from dark moss and shimmering, metallic fiber-optic
threads. In one hand, they hold a gnarled wooden staff entwined with glowing
energy conduits and topped with a floating, crystalline artifact. Perched on
their shoulder is a small, mechanical owl with holographic wings and camera-lens
eyes that blink with a soft, red light. Their expression is serene and ancient,
eyes holding a deep, knowing look"
Action
Les actions décrivent le "verbe" de votre vidéo, ou ce qui se passe. L'action donne vie au sujet, décrit les mouvements, les interactions et les expressions subtiles.

Voici quelques exemples d'actions que vous pouvez utiliser :

Mouvements de base : marcher, courir, sauter, voler, nager, danser, tourner, tomber, rester immobile, s'asseoir

Interactions : parler, rire, se disputer, se faire un câlin, se battre, jouer à un jeu, cuisiner, construire, écrire, lire, observer

Expressions émotionnelles : sourire, froncer les sourcils, surprise, concentration intense, air pensif, excitation, pleurs

Actions subtiles : une légère brise qui ébouriffe les cheveux, des feuilles qui bruissent, un subtil hochement de tête, des doigts qui tapotent impatiemment, des yeux qui clignent lentement

Transformations ou processus : une fleur qui s'épanouit en accéléré, de la glace qui fond, une ville qui se développe au fil du temps (toutefois, gardez à l'esprit la durée de l'extrait pour les événements qui se produisent sur une période plus longue)

Exemple : la vidéo et la requête suivantes montrent comment diriger une histoire en séquençant les actions et les changements émotionnels :




"A gloved hand carefully slices open the spine of an ancient, leather-bound book
with a scalpel. The hand then delicately extracts a tiny, metallic data chip
hidden within the binding. The character's eyes, previously focused and calm,
widen in a flash of alarm as a floorboard creaks off-screen. They quickly palm
the chip, their head snapping up to scan the dimly lit room, their body tense
and listening for any other sound"
Scène ou contexte
La scène ou le contexte décrivent le "où" et le "quand" de votre vidéo. C'est-à-dire l'environnement qui ancre le sujet et établit l'humeur et l'atmosphère de la vidéo.

Voici des exemples de scènes ou de contextes que vous pouvez utiliser :

Lieu (intérieur) : un salon confortable avec une cheminée crépitante, un laboratoire futuriste stérile, un atelier d'artiste encombré, une grande salle de bal, un grenier poussiéreux

Lieu (extérieur) : plage tropicale baignée de soleil, forêt ancienne brumeuse, paysage urbain futuriste et animé la nuit, sommet montagneux paisible à l'aube, planète extraterrestre désolée

Heure de la journée : heure dorée, soleil de midi, crépuscule, nuit noire, avant l'aube

Météo : ciel bleu clair, ciel couvert et sombre, légère bruine, gros orage avec éclairs visibles, légère chute de neige, brouillard tourbillonnant

Période historique ou fantastique : cour d'un château médiéval, club de jazz rugissant des années 1920, ruelle cyberpunk, clairière enchantée

Détails atmosphériques : particules de poussière flottant dans un rayon de soleil, mirage de chaleur scintillante, reflets sur la chaussée mouillée, feuilles éparpillées par le vent

Exemple : la vidéo suivante montre comment créer un monde immersif :




"The scene is a rain-slicked, crumbling street in a forgotten city, shrouded in
perpetual twilight. Giant, bioluminescent mushrooms have sprouted from the
cracked asphalt, casting an eerie, pulsating green and purple glow onto the
decaying facades of skeletal skyscrapers. A gentle, constant rain creates
shimmering reflections in the puddles below, and the only sounds are the soft
patter of rain and a low, otherworldly hum from the glowing fungi"
Angles de caméra
Les angles de caméra définissent le point de vue de la prise de vue, ce qui influence directement la façon dont le public perçoit le sujet.

Important : Certains angles de caméras avancés ne sont pas officiellement pris en charge. Les résultats et la fiabilité peuvent varier en fonction de la requête globale et de votre cas d'utilisation spécifique.

Voici quelques exemples d'angles de caméra que vous pouvez utiliser :

Prise de vue à hauteur des yeux : offre une perspective neutre et courante, comme si la scène était vue à hauteur d'homme. Par exemple, "plan à hauteur des yeux d'une femme buvant du thé".

Plongée : la caméra est placée en dessous du sujet et pointe vers le haut, ce qui le fait paraître puissant ou imposant. Par exemple, "plan de suivi en contre-plongée d'un super-héros qui atterrit".

Plongée : la caméra est placée au-dessus du sujet et orientée vers le bas. Le sujet peut alors paraître petit, vulnérable ou faire partie d'un ensemble plus vaste. Par exemple, "vue en plongée d'un enfant perdu dans une foule".

Vue plongeante ou vue de dessus : plan filmé directement d'en haut, offrant une perspective de la scène semblable à celle d'une carte. Par exemple, "vue plongeante d'une intersection animée".

Vue en contre-plongée : prise de vue à très faible angle, directement vers le haut depuis le sol, qui met l'accent sur la hauteur et la grandeur. Par exemple, "vue en contre-plongée de gratte-ciel imposants".

Angle hollandais ou incliné : la caméra est inclinée sur le côté, ce qui crée une ligne d'horizon oblique. Cet angle est souvent utilisé pour transmettre un sentiment de malaise, de désorientation ou de dynamisme. Par exemple, "plan incliné d'un personnage courant dans un couloir".

Gros plan : cadre serré sur le sujet, généralement sur le visage, pour mettre en avant les émotions ou un détail spécifique. Par exemple, "gros plan sur les yeux déterminés d'un personnage".

Gros plan extrême : isole un très petit détail du sujet, comme un œil ou une goutte d'eau. Par exemple : "gros plan extrême d'une goutte d'eau tombant sur une feuille".

Plan moyen : montre le sujet à partir de la taille, en équilibrant les détails avec le contexte environnemental. Couramment utilisé pour les dialogues. Par exemple, "plan moyen de deux personnes en train de discuter".

Plan complet ou plan large : montre le sujet entier, de la tête aux pieds, avec une partie de l'environnement visible. Par exemple, "plan complet d'un danseur en pleine représentation".

Plan large ou plan d'ensemble : montre le sujet dans son environnement général. Il est souvent utilisé pour établir le lieu et le contexte au début d'une séquence. Par exemple, "plan large d'une cabane isolée dans un paysage enneigé".

Plan par-dessus l'épaule : le plan est cadré derrière une personne, par-dessus son épaule, et montre une autre personne ou un objet. Ce type de plan est courant dans les conversations. Par exemple, "plan par-dessus l'épaule lors d'une négociation tendue".

Plan subjectif : montre la scène du point de vue visuel direct d'un personnage, comme si le public voyait à travers ses yeux. Par exemple, "Point de vue d'une personne sur des montagnes russes".

Exemple : La vidéo et la requête suivantes montrent un angle de caméra en vue aérienne :




"A bird's-eye view of a vast, intricate maze made of high green hedges. A lone
figure in a red coat is visible, moving through the labyrinthine paths below"
Exemple : La vidéo et la requête suivantes illustrent un angle de caméra en gros plan extrême :




"An extreme close-up of a single, glistening drop of rain as it lands on the
petal of a vibrant red rose, causing the petal to tremble slightly"
Mouvements de caméra
Les mouvements de la caméra contribuent à dynamiser la prise de vue, créant ainsi une expérience plus cinématographique.

Voici quelques exemples de mouvements de caméra que vous pouvez utiliser :

Plan fixe : la caméra reste complètement immobile. Par exemple, "plan fixe d'un paysage serein".

Balayage (gauche/droite) : la caméra pivote horizontalement vers la gauche ou vers la droite à partir d'une position fixe. Par exemple, "panoramique lent vers la gauche sur la ligne d'horizon d'une ville au crépuscule".

Inclinaison (vers le haut/vers le bas) : la caméra pivote verticalement vers le haut ou vers le bas à partir d'une position fixe. Par exemple, "incline la caméra vers le bas, en partant du visage choqué du personnage pour arriver à la lettre révélatrice qu'il tient dans ses mains".

Dolly (avant/arrière) : la caméra se rapproche ou s'éloigne physiquement du sujet. Par exemple, "éloigne la caméra du personnage pour souligner son isolement".

Travelling latéral (gauche/droite) : la caméra se déplace physiquement à l'horizontale (sur le côté) vers la gauche ou la droite, souvent parallèlement au sujet ou à la scène. Par exemple, "caméra à droite, suivant un personnage qui marche sur un trottoir animé".

Socle (haut/bas) : la caméra se déplace physiquement vers le haut ou vers le bas tout en conservant une perspective horizontale. Par exemple : "Un socle se lève pour révéler toute la hauteur d'un arbre ancien et imposant."

Zoom (avant/arrière) : l'objectif de la caméra modifie sa distance focale pour agrandir ou réduire le sujet. Cela diffère d'un travelling, car la caméra elle-même ne bouge pas. Par exemple, "zoom lent sur un artefact mystérieux posé sur une table".

Plan grue : la caméra est montée sur une grue et se déplace verticalement (vers le haut ou vers le bas) ou en arcs de cercle amples. Il est souvent utilisé pour des révélations spectaculaires ou des perspectives en plongée. Par exemple, "plan grue révélant un vaste champ de bataille médiéval".

Prise de vue aérienne ou prise de vue par drone : prise de vue effectuée à haute altitude, généralement à l'aide d'un avion ou d'un drone, souvent avec des mouvements fluides et aériens. "Vue aérienne panoramique d'un drone survolant une chaîne d'îles tropicales."

Caméra à l'épaule ou tremblante : la caméra est tenue par l'opérateur, ce qui entraîne des mouvements moins stables, souvent saccadés, qui peuvent transmettre un sentiment de réalisme, d'immédiateté ou de malaise. Par exemple, "prise de vue à la caméra à l'épaule lors d'une course-poursuite chaotique sur un marché".

Panoramique rapide : panoramique extrêmement rapide qui floute l'image, souvent utilisé comme transition ou pour transmettre un mouvement rapide ou une désorientation. Par exemple, "panoramique rapide d'un personnage qui se dispute à un autre".

Prise de vue en arc de cercle : la caméra se déplace en formant un cercle ou un demi-cercle autour du sujet. Par exemple, "plan en arc de cercle autour d'un couple qui s'embrasse sous la pluie".

Exemple : La vidéo et la requête suivantes illustrent un mouvement de caméra en zoom avant :




"A slow, dramatic zoom in on a mysterious, ancient compass lying on a dusty map.
The camera starts wide, showing the map and a flickering candle, then smoothly
zooms in until the intricate, glowing symbols on the compass face fill the
entire frame"

Exemple : La vidéo et la requête suivantes montrent une prise de vue aérienne par drone :




"Sweeping aerial drone shot flying over a tropical island chain"
Objectif et effets optiques
Les objectifs et les effets optiques modifient la façon dont la caméra "voit" le monde. L'utilisation d'objectifs et d'effets optiques permet d'ajouter une touche professionnelle et stylistique.

Important : Certains objectifs de caméras avancés ne sont pas officiellement compatibles. Les résultats et la fiabilité peuvent varier en fonction de la requête globale et de votre cas d'utilisation spécifique.

Voici quelques exemples d'effets optiques et d'objectif que vous pouvez utiliser :

Objectif grand-angle : capture un champ de vision plus large qu'un objectif standard. Elle peut exagérer la perspective, en agrandissant les éléments au premier plan et en créant une impression de grandeur ou, à des distances plus proches, de distorsion. Par exemple : "Prise de vue grand-angle de l'intérieur d'une grande cathédrale, mettant en valeur ses arches imposantes."

Téléobjectif : réduit le champ de vision et comprime la perspective, ce qui permet de rapprocher les sujets éloignés et souvent de les isoler en créant une faible profondeur de champ. Par exemple, "photo au téléobjectif d'un aigle en vol au loin devant une chaîne de montagnes".

Faible profondeur de champ : effet optique dans lequel seul un plan étroit de l'image est net, tandis que l'avant-plan ou l'arrière-plan sont flous. La qualité esthétique de ce flou est appelée "bokeh". Par exemple, "portrait d'un homme avec une faible profondeur de champ, son visage net sur un arrière-plan de parc légèrement flouté avec un magnifique bokeh".

Forte profondeur de champ : la majeure partie ou la totalité de l'image, du premier plan à l'arrière-plan, est nette. Par exemple, "paysage avec une grande profondeur de champ, montrant des détails nets depuis les fleurs sauvages au premier plan immédiat jusqu'aux montagnes au loin".

Reflets : effet créé lorsqu'une source de lumière vive frappe directement l'objectif de la caméra, ce qui provoque l'apparition de traînées, d'étoiles ou de cercles lumineux sur l'image. Souvent utilisé pour un effet dramatique ou cinématographique. Par exemple, "un reflet de lumière cinématographique alors que le soleil se couche derrière un couple en contre-jour".

Mise au point sélective : technique qui consiste à déplacer la mise au point de l'objectif d'un sujet ou d'un plan de profondeur à un autre dans un seul plan continu. Par exemple : "Fais la mise au point du visage pensif d'un personnage au premier plan à une photo importante sur le mur derrière lui."

Effet fisheye : objectif ultra grand angle qui produit une distorsion en barillet extrême, créant une image panoramique circulaire ou fortement convexe et large. Par exemple : "Vue en fisheye depuis l'intérieur d'une voiture, montrant le conducteur, le tableau de bord incurvé et le pare-brise dans leur intégralité."

Effet Vertigo (dolly zoom) : effet de caméra obtenu en déplaçant la caméra vers l'avant ou vers l'arrière d'un sujet tout en zoomant simultanément l'objectif dans la direction opposée. Le sujet reste à peu près de la même taille dans le cadre, mais la perspective de l'arrière-plan change radicalement, ce qui donne souvent une impression de désorientation ou de malaise. Par exemple, "effet vertige (zoom avant/arrière) sur un personnage debout au bord d'une falaise, l'arrière-plan s'éloignant rapidement".

Exemple : La vidéo et la requête suivantes illustrent un effet optique de faible profondeur de champ :




A cinematic close-up portrait of a woman sitting in a café at night, with a very
shallow depth of field. Her face is in sharp focus, while the city lights
outside the window behind her are transformed into soft, beautiful bokeh circles
Exemple : La vidéo et la requête suivantes illustrent un effet de mise au point sélective :




"A medium shot of a detective's hand in the foreground, holding a single, spent
bullet casing. The camera then performs a slow rack focus, shifting from the
casing to reveal the anxious face of a witness in the background, now in sharp
focus"
Style et esthétique visuels
Le style visuel et l'esthétique décrivent l'atmosphère artistique globale de votre vidéo. C'est l'un des éléments les plus importants pour créer un style unique.

Cette catégorie générale peut être divisée en quatre composantes clés :

Éclairage
Ton ou humeur
Style artistique
Ambiance
Éclairage
Les effets de lumière modifient la façon dont le sujet et les zones environnantes sont capturés par la caméra. Les effets de lumière peuvent vous aider à définir un style particulier.

Voici quelques exemples d'effets de lumière que vous pouvez utiliser :

Lumière naturelle : "douce lumière du matin entrant par une fenêtre", "lumière du jour par temps nuageux", "clair de lune"

Lumière artificielle : "lueur chaleureuse d'une cheminée", "lumière vacillante d'une bougie", "éclairage fluorescent agressif d'un bureau", "néons clignotants"

Éclairage cinématographique : "éclairage Rembrandt pour un portrait", "style film noir avec des ombres profondes et des lumières vives", "éclairage high-key pour une scène lumineuse et joyeuse", "éclairage low-key pour une ambiance sombre et mystérieuse"

Effets spécifiques : "éclairage volumétrique créant des rayons lumineux visibles", "rétroéclairage pour créer une silhouette", "éclat de l'heure dorée", "éclairage latéral spectaculaire"

Ton ou humeur
Les effets de ton et d'ambiance décrivent l'atmosphère ou l'impression générale de la vidéo.

Voici quelques exemples d'effets de ton ou d'humeur que vous pouvez utiliser :

Joyeux : gai, vif, joyeux, entraînant, fantaisiste

Triste/Mélancolique : sombre, couleurs douces, rythme lent, poignant, nostalgique.

Suspense/Tension : sombre, ombragé, coupes rapides (si cela implique un montage), sentiment de malaise, palpitant.

Paisible/serein : calme, tranquille, doux, méditatif.

Épique/grandiloquent : grandiose, majestueux, spectaculaire, impressionnant.

Futuriste/Science-fiction : épuré, métallique, néon, technologique, dystopique, utopique.

Vintage/Rétro : ton sépia, film granuleux, esthétique d'une époque spécifique (par exemple, "années 1950, style américain", "années 1980, vaporwave").

Romantique : flou artistique, couleurs chaudes, intimité.

Horreur : sombre, troublant, étrange, sanglant (mais attention aux filtres de contenu).

Style artistique
Vous pouvez décrire un style artistique dont la vidéo doit s'inspirer lors de sa génération.

Voici quelques exemples d'effets de style artistique que vous pouvez utiliser :

Photoréalisme : "rendu ultra-réaliste", "tourné avec une caméra 8K"

Cinématique : "style cinématographique", "tourné sur pellicule 35 mm", "grand écran anamorphique"

Styles d'animation : "style anime japonais", "style animation Disney classique", "animation 3D façon Pixar", "style animation en pâte à modeler", "animation en stop-motion", "animation en cel-shading"

Mouvements artistiques/artistes : "dans le style de Van Gogh", "peinture surréaliste", "impressionniste", "design Art déco", "esthétique Bauhaus"

Styles spécifiques : "illustration de roman graphique réaliste", "aquarelle prenant vie", "animation de croquis au fusain", "schéma de plan".

Exemple : La vidéo et la requête suivantes illustrent un style d'animation d'anime japonais :




"A dynamic scene in a vibrant Japanese anime style. A magical girl with silver
hair and glowing blue eyes walks in a forest. The style features sharp lines,
bright, saturated colors, and expressive"
Exemple : la vidéo et la requête suivantes illustrent un style artistique vintage :




"A vintage 1920s street scene, sepia toned, film grain, with characters in
period attire"
Ambiance
L'ambiance décrit le caractère d'un lieu ou d'un environnement dans lequel se déroule la vidéo.

Voici quelques exemples d'effets d'ambiance que vous pouvez utiliser :

Palettes de couleurs : "noir et blanc monochromes", "couleurs tropicales vives et saturées", "tons terreux et neutres", "palette futuriste bleue et argentée", "tons chauds d'orange et de marron automnaux"

Effets atmosphériques : "brouillard épais sur une lande", "tourbillons de sable dans le désert", "douce neige tombant et formant un manteau moelleux", "mirage de chaleur au-dessus de l'asphalte", "particules lumineuses magiques dans l'air", "diffusion sous-cutanée sur un objet translucide"

Qualités texturées : "murs en pierre brute", "surfaces chromées lisses et brillantes", "tissu doux et velouté", "gouttes de rosée accrochées à une toile d'araignée"

Éléments temporels
Les éléments temporels affectent le déroulement du temps dans une vidéo. Vous pouvez les utiliser pour mettre en évidence des changements, même dans de courts extraits.

Voici quelques exemples d'éléments temporels que vous pouvez utiliser :

Rythme : "ralenti", "action rapide", "time-lapse"

Évolution (subtile pour les clips courts) : "un bouton de fleur qui s'ouvre lentement", "une bougie qui se consume légèrement", "l'aube qui se lève, le ciel qui s'éclaircit progressivement"

Rythme : "lumière pulsée", "mouvement rythmique"

Exemple : La vidéo et la requête suivantes illustrent un effet temporel d'évolution :




"A close-up of a single red rose bud, its petals tightly closed. The camera
remains static as the flower slowly and gracefully unfurls over the course of
the shot, revealing its vibrant inner layers. The evolution is subtle, showing a
clear but gradual change"
Exemple : La vidéo et la requête suivantes illustrent un effet temporel de type "time-lapse" :




"A time-lapse of a bustling city skyline as day transitions to night. The camera
is static. Watch as the sun sets, casting long shadows, and the city lights
begin to twinkle on, with streaks of car headlights moving along the streets
below"
Audio
Les suggestions audio aident à guider les éléments visuels de la vidéo par rapport au son. La direction audio peut avoir un impact considérable sur l'action, le rythme et l'ambiance de la vidéo.

L'audio est compatible avec veo-3.0-generate-001 en version preview.

Indiquez clairement si vous souhaitez obtenir un contenu audio. Nous vous recommandons d'utiliser des phrases distinctes dans votre requête pour décrire l'audio. Voici des exemples d'éléments audio courants que vous pouvez utiliser :

Effets sonores : sons individuels et distincts qui se produisent dans la scène. Par exemple, "le son d'un téléphone qui sonne", "de l'eau qui éclabousse en arrière-plan", "des sons doux de maison, le grincement d'une porte de placard et le tic-tac d'une horloge".

Bruit ambiant : bruit de fond général qui donne l'impression que le lieu est réel. Par exemple, "les sons de la circulation urbaine et des sirènes au loin", "les vagues s'écrasant sur le rivage", "le léger bourdonnement d'un bureau".

Dialogue : paroles prononcées par des personnages ou un narrateur. Par exemple, "l'homme au chapeau rouge dit : Où est le lapin ?", "une voix off avec un accent britannique soigné parle d'un ton sérieux et urgent", "deux personnes discutent d'un film".

Exemple : la vidéo et l'invite suivantes montrent comment utiliser le dialogue :




"A medium shot in a dimly lit interrogation room. The seasoned detective says:
Your story has holes. The nervous informant, sweating under a single bare bulb,
replies: I'm telling you everything I know. The only other sounds are the slow,
rhythmic ticking of a wall clock and the faint sound of rain against the window"
Termes cinématographiques
Vous pouvez utiliser des termes cinématographiques pour décrire le style de montage et des techniques spécifiques. Par exemple, "raccord cut", "jump cut", "séquence de plan d'ensemble", "montage", "effet de dioptrie partagée".

Exemple : La vidéo et le prompt suivants montrent comment utiliser la technique du jump cut :




"A person sitting in the same position but wearing different outfits, with sharp
jump cuts between each outfit change. The background should stay static and the
person should reappear instantly in the new outfit, creating a fast-paced,
rhythmic jump cut effect. The lighting and framing should remain consistent to
emphasize the sudden changes"
Requêtes négatives
Les requêtes négatives sont un outil qui vous aide à spécifier les éléments que vous ne souhaitez pas voir générés dans votre vidéo. Lorsque vous utilisez une requête négative, vous décrivez les éléments que le modèle ne doit pas inclure lors de la génération de la vidéo.

Nous vous recommandons de suivre les conseils suivants :

Déconseillé : utiliser des mots ou des expressions instructives comme "pas de" ou "ne pas". Par exemple, évitez les requêtes telles que "pas de murs" ou "ne pas afficher les murs".

Recommandé : Décrivez ce que vous ne souhaitez pas voir. Par exemple, "mur, cadre" signifie que vous ne voulez pas de mur ni de cadre dans la vidéo.

Prompt (Requête)	Résultat généré
Génère une courte animation stylisée d'un grand chêne solitaire dont les feuilles sont emportées par un vent fort. L'arbre doit avoir une forme fantaisiste légèrement exagérée, avec des branches dynamiques et fluides. Les feuilles doivent afficher une variété de couleurs automnales, tourbillonnant et dansant dans le vent. L'animation doit être accompagnée d'une bande-son douce et atmosphérique, et utiliser une palette de couleurs chaudes et accueillantes.	Arbre avec des mots.
Génère une courte animation stylisée d'un grand chêne solitaire dont les feuilles sont emportées par un vent violent. L'arbre doit avoir une forme fantaisiste légèrement exagérée, avec des branches dynamiques et fluides. Les feuilles doivent afficher une variété de couleurs automnales, tourbillonnant et dansant dans le vent. L'animation doit comporter une bande-son douce et atmosphérique, et utiliser une palette de couleurs chaudes et accueillantes.

Avec une invite négative : arrière-plan urbain, structures artificielles, atmosphère sombre, orageuse ou menaçante.

Arbre sans mots négatifs.
Étapes suivantes
Bonnes pratiques pour Veo sur Agent Platform

Générer des vidéos avec Veo sur Agent Platform à partir de requêtes textuelles

Générer des vidéos avec Veo sur Agent Platform à partir d'une image

Générer des vidéos avec Veo sur Agent Platform à l'aide des première et dernière images

Étendre Veo sur Agent Platform : générer des vidéos

Comprendre l'IA responsable et les consignes d'utilisation de Veo sur Agent Platform

Ce contenu vous a-t-il été utile ?

Envoyer des commentaires
Sauf indication contraire, le contenu de cette page est régi par une licence Creative Commons Attribution 4.0, et les échantillons de code sont régis par une licence Apache 2.0. Pour en savoir plus, consultez les Règles du site Google Developers. Java est une marque déposée d'Oracle et/ou de ses sociétés affiliées.

Dernière mise à jour le 2026/04/23 (UTC).

Produits et tarification
Voir tous les produits
Tarifs de Google Cloud
Google Cloud Marketplace
Contacter le service commercial
Support
Forums de la communauté
Support
Notes de version
État du système
Resources
GitHub
Premiers pas avec Google Cloud
Exemples de code
Centre d'architecture cloud
Formations et certifications
Échanger
Blog
Événements
X (Twitter)
Google Cloud sur YouTube
Google Cloud Tech sur YouTube
À propos de Google
Règles de confidentialité
Conditions d'utilisation du site
Conditions d'utilisation de Google Cloud
Troisième décennie d'action pour le climat : rejoignez-nous
S'inscrire à la newsletter Google Cloud
S’abonner

Français
