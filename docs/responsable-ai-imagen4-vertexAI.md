Passer au contenu principal
docs.cloud.google.com utilise des cookies Google afin de fournir ses services, d'en améliorer la qualité et d'analyser le trafic. En savoir plus

J'ai compris
Google Cloud Documentation
Domaines technologiques

Plus
Recherche
/
Console



Language

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
Envoyer des commentairesIA responsable et consignes d'utilisation d'Imagen



Imagen sur Agent Platform fournit les fonctionnalités de pointe d'IA générative de Google aux développeurs d'applications. En tant que technologie précoce, les fonctionnalités et les utilisations en constante évolution d'Imagen sur Agent Platform peuvent être sujettes à une mauvaise application, une utilisation abusive et des conséquences imprévues ou inattendues. Par exemple, Imagen sur Agent Platform peut générer un résultat inattendu, comme des images choquantes, offensantes ou incorrectes.

Compte tenu de ces risques et de ces complexités, Imagen sur Agent Platform est conçu en appliquant les principes de l'IA de Google. Cependant, il est important que les développeurs comprennent et testent leurs modèles pour les déployer en toute sécurité et de manière responsable. Pour aider les développeurs, Imagen sur Agent Platform dispose de filtres de sécurité intégrés qui aident les clients à bloquer les sorties potentiellement dangereuses dans leur cas d'utilisation. Pour en savoir plus, consultez la section Filtres de sécurité.

Lorsque Imagen sur Agent Platform est intégré au cas d'utilisation et au contexte uniques d'un client, des considérations d'IA responsable supplémentaires et des limites de modèle peuvent être nécessaires. Nous encourageons les clients à adopter les pratiques recommandées d'équité, interprétabilité, de confidentialité et de sécurité recommandées.


Attention : Le tableau suivant décrit les points de terminaison de génération d'images obsolètes et leurs remplacements. Nous vous recommandons de mettre à jour les points de terminaison de votre modèle avant le 30 juin 2026 pour éviter toute interruption de service.
Points de terminaison abandonnés	Migration de point de terminaison recommandée
imagegeneration@002	gemini-2.5-flash-image
imagegeneration@003	gemini-2.5-flash-image
imagegeneration@004	gemini-2.5-flash-image
imagegeneration@005	gemini-2.5-flash-image
imagegeneration@006	gemini-2.5-flash-image
imagetext@001	gemini-2.5-flash-image
imagen-3.0-capability-001	gemini-2.5-flash-image
imagen-3.0-capability-002	gemini-2.5-flash-image
imagen-3.0-fast-generate-001	gemini-2.5-flash-image
imagen-3.0-generate-001	gemini-2.5-flash-image
imagen-3.0-generate-002	gemini-2.5-flash-image
imagen-4.0-fast-generate-001	gemini-2.5-flash-image
imagen-4.0-generate-001	gemini-2.5-flash-image
imagen-4.0-ultra-generate-001	gemini-2.5-flash-image
Afficher la fiche de modèle Imagen pour la génération d'images

Afficher la fiche de modèle Imagen pour la modification et la personnalisation

Consignes d'utilisation d'Imagen
Lisez les informations générales sur les attributs de produit et les considérations légales ci-dessous avant d'utiliser Imagen sur Agent Platform.

Filtres et sorties d'image et de texte : les images (générées ou importées) via Imagen sur Agent Platform sont évaluées par des filtres de sécurité. Imagen s'efforce de filtrer les images (générées ou importées) qui ne respectent pas notre Règlement sur l'utilisation acceptable (AUP) ou des restrictions produit supplémentaires de l'IA générative. De plus, nos modèles d'imagerie générative sont destinés à générer du contenu original et non à répliquer le contenu existant. Nous avons conçu nos systèmes de façon à réduire le risque que cela se produise, et nous continuerons à améliorer leur fonctionnement. Comme tous les fournisseurs de services cloud, Google applique un Règlement sur l'utilisation acceptable qui interdit aux clients d'utiliser nos services d'une manière qui enfreint les droits de propriété intellectuelle de tiers.
Seuils de filtre de sécurité configurables : Google bloque les réponses de modèle qui dépassent les scores de confiance désignés pour certains attributs de sécurité. Pour demander à pouvoir modifier un seuil de sécurité, contactez l'équipe chargée de votre Google Cloud compte.
Ajout de texte compatible avec certaines versions de modèle : Imagen ne permet pas d'ajouter de texte aux images (importées ou générées) à l'aide d'un prompt de texte lorsque vous utilisez la version de modèle imagegeneration@004 ou des versions antérieures.
Signaler une suspicion d'abus : vous pouvez signaler une utilisation abusive d'Imagen sur Agent Platform ou tout résultat généré contenant des informations inappropriées ou inexactes à l'aide du formulaire Signaler une utilisation abusive sur Google Cloud formulaire.
Désinscription du programme Testeurs de confiance : si vous avez précédemment accepté que Google utilise vos données pour améliorer les services d'IA/ML pré-DG dans le cadre des conditions du programme Testeurs de confiance, vous pouvez choisir de vous désinscrire en utilisant le formulaire programme Testeurs de confiance - Demande de désinscription.
Filtres de sécurité
Les requêtes de texte fournies en tant qu'entrées et images (générées ou importées) via Imagen sur Agent Platform sont évaluées par rapport à une liste de filtres de sécurité, qui incluent des "catégories dangereuses" (par exemple, violence, sexual, derogatory, et toxic). Ces filtres de sécurité visent à filtrer le contenu (généré ou importé) qui ne respecte pas notre Règlement sur l'utilisation acceptable, Règlement sur les utilisations interdites de l'IA générative ou nos principes concernant l'IA.

Si le modèle répond à une requête avec un message d'erreur tel que "Impossible d'envoyer le prompt" ou "Elle peut ne pas respecter nos règles", cela signifie que l'entrée déclenche un filtre de sécurité. Si le nombre d'images renvoyées est inférieur à celui demandé, certains résultats générés sont bloqués pour non-respect des exigences de sécurité.

Vous pouvez choisir le degré de filtrage du contenu sensible en ajustant le paramètre safetySetting.

Attributs de sécurité
Les attributs de sécurité et les filtres de sécurité n'ont pas de relation de mappage "un à un". Les attributs de sécurité sont l'ensemble des attributs que nous renvoyons à l'utilisateur lorsque includeSafetyAttributes est défini. Les filtres de sécurité sont l'ensemble des filtres que nous utilisons pour filtrer le contenu. Nous n'appliquons pas de filtre sur toutes les catégories d'attributs de sécurité. Par exemple, pour la catégorie d'attribut de sécurité "Santé", nous ne filtrez pas le contenu en fonction du score de confiance de l'état de santé. De plus, nous n'exposons pas les scores de confiance de certains de nos filtres de sécurité sensibles internes.

Configurer des filtres de sécurité
Vous pouvez utiliser plusieurs paramètres de filtrage de sécurité avec les modèles de génération d'images. Par exemple, vous pouvez autoriser le modèle à signaler des codes de filtre de sécurité pour du contenu bloqué, à désactiver la génération de personnes ou de visages, à ajuster la sensibilité des filtres de contenu, ou à renvoyer les scores de sécurité arrondis des attributs de sécurité dans l'entrée et la sortie. Pour plus d'informations techniques sur les champs individuels, consultez la documentation de référence de l'API des modèles de génération d'images.

La réponse varie en fonction des paramètres que vous avez définis. Certains paramètres affectent le contenu généré, tandis que d'autres affectent le filtrage du contenu et la manière dont le filtrage vous est indiqué. De plus, le format de sortie varie si vous avez spécifié le filtrage sur les données d'entrée ou sur l'image générée.

Paramètres de filtrage de contenu
Les paramètres facultatifs suivants affectent le filtrage du contenu ou la manière dont le filtrage vous est indiqué :

safetySetting : permet de définir le niveau de filtrage du contenu potentiellement sensible généré.
includeRaiReason : fournit des informations plus détaillées sur la sortie filtrée.
personGeneration : paramètre vous permettant de mieux contrôler la génération de personnes, de visages et d'enfants.
disablePersonFace : obsolète La possibilité d'autoriser ou non la génération de personnes et de visages. Les utilisateurs doivent définir personGeneration à la place.
includeSafetyAttributes : fournit des informations complètes sur les attributs de sécurité pour le texte d'entrée, l'image d'entrée (image à modifier) et toutes les images générées. Ces informations incluent la catégorie de sécurité (par exemple, "Firearms & Weapons", "Illicit Drugs" ou "Violence") et les scores de confiance.
Entrée filtrée
Si votre texte ou votre image d'entrée (pour modification) sont filtrés, vous obtenez une réponse avec un code d'erreur 400. Une requête avec une entrée bloquée par un filtre d'IA responsable renvoie ce format de sortie si vous définissez includeRaiReason ou includeSafetyAttributes.

Le résultat dépend de la version de modèle que vous utilisez. Voici un exemple de résultat lorsque l'entrée est filtrée pour différentes versions de modèle :

Modèle
Modèles
{
  "error": {
    "code": 400,
    "message": "Image generation failed with the following error: The prompt could not be submitted. This prompt contains sensitive words that violate Google's Responsible AI practices. Try rephrasing the prompt. If you think this was an error, send feedback."
    "status": "INVALID_ARGUMENT",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.DebugInfo",
        "detail": "[ORIGINAL ERROR] generic::invalid_argument: Image generation failed with the following error: The prompt could not be submitted. This prompt contains sensitive words that violate Google's Responsible AI practices. Try rephrasing the prompt. If you think this was an error, send feedback. [google.rpc.error_details_ext] { message: \"Image editing failed with the following error: The prompt could not be submitted. This prompt contains sensitive words that violate Google's Responsible AI practices. Try rephrasing the prompt. If you think this was an error, send feedback. Support codes: 42876398\" }"
      }
    ]
  }
}
Résultat filtré
Le contenu de la sortie filtrée varie en fonction du paramètre d'IA responsable que vous avez défini. Les exemples de sortie suivants montrent le résultat de l'utilisation des paramètres includeRaiReason et includeSafetyAttributes.

Résultat filtré à l'aide de includeRaiReason
Si vous n'ajoutez pas de paramètre includeRaiReason ou si vous définissez includeRaiReason: false, votre réponse n'inclut que les objets image générés qui n'ont pas été filtrés. Tous les objets image filtrés sont omis du tableau "predictions": []. Par exemple, voici une réponse à une requête comportant "sampleCount": 4, mais pour laquelle deux des images ont été filtrées, et sont par conséquent omises :

{
  "predictions": [
    {
      "bytesBase64Encoded": "/9j/4AAQSkZJRgABA[...]bdsdgD2PLbZQfW96HEFE/9k=",
      "mimeType": "image/png"
    },
    {
      "mimeType": "image/png",
      "bytesBase64Encoded": "/9j/4AAQSkZJRgABA[...]Ct+F+1SLLH/2+SJ4ZLdOvg//Z"
    }
  ],
  "deployedModelId": "MODEL_ID"
}
Si vous définissez includeRaiReason: true et que plusieurs images de sortie sont filtrées, votre réponse inclut les objets d'image générés et les objets raiFilteredReason pour toutes les images de sortie filtrées. Par exemple, voici une réponse à une requête comportant "sampleCount": 4 et includeRaiReason: true, mais pour laquelle deux des images ont été filtrées : Par conséquent, deux objets incluent des informations sur les images générées et l'autre objet inclut un message d'erreur.

Modèle
Modèles
{
  "predictions": [
    {
      "bytesBase64Encoded": "/9j/4AAQSkZJRgABA[...]bdsdgD2PLbZQfW96HEFE/9k=",
      "mimeType": "image/png"
    },
    {
      "mimeType": "image/png",
      "bytesBase64Encoded": "/9j/4AAQSkZJRgABA[...]Ct+F+1SLLH/2+SJ4ZLdOvg//Z"
    },
    {
      "raiFilteredReason": "Your current safety filter threshold filtered out 2 generated images. You will not be charged for blocked images. Try rephrasing the prompt. If you think this was an error, send feedback."
    },
  ],
  "deployedModelId": "MODEL_ID"
}
Résultat filtré à l'aide de includeSafetyAttributes
Si vous définissez "includeSafetyAttributes": true, le tableau de réponse "predictions": [] inclut les scores RAI (arrondis à une décimale) des attributs de sécurité du texte de la requête positive. Les attributs de sécurité de l'image sont également ajoutés à chaque sortie non filtrée. Si une image de sortie est filtrée, ses attributs de sécurité ne sont pas renvoyés. Par exemple, voici une réponse à une requête non filtrée, avec une image renvoyée :

{
  "predictions": [
    {
      "bytesBase64Encoded": "/9j/4AAQSkZJRgABA[...]bdsdgD2PLbZQfW96HEFE/9k=",
      "mimeType": "image/png", 
      "safetyAttributes": {
        "categories": [
          "Porn",
          "Violence"
        ],
        "scores": [
          0.1,
          0.2
        ]
      } 
    }, 
    {
      "contentType": "Positive Prompt",
      "safetyAttributes": {
        "categories": [
          "Death, Harm & Tragedy",
          "Firearms & Weapons",
          "Hate",
          "Health",
          "Illicit Drugs",
          "Politics",
          "Porn",
          "Religion & Belief",
          "Toxic",
          "Violence",
          "Vulgarity",
          "War & Conflict"
        ],
        "scores": [
          0,
          0,
          0,
          0,
          0,
          0,
          0.2,
          0,
          0.1,
          0,
          0.1,
          0
        ]
      }
    }, 
  ],
  "deployedModelId": "MODEL_ID"
}
Catégories de codes de filtre de sécurité
Selon les filtres de sécurité que vous configurez, la sortie peut contenir un code de motif de sécurité semblable à celui-ci :

    {
      "raiFilteredReason": "ERROR_MESSAGE. Support codes: 56562880""
    }
Le code indiqué correspond à une catégorie de contenu nuisible spécifique. Les correspondances entre les codes et les catégories sont les suivantes :

Code d'erreur	Catégorie de sécurité	Description	Contenu filtré : entrée de prompt ou sortie d'image
58061214
17301594	Enfant	Détecte les contenus comportant des enfants s'ils ne sont pas autorisés dans les paramètres de la requête API ou dans la liste d'autorisation.	entrée (prompt): 58061214
sortie (image): 17301594
29310472
15236754	Célébrité	Détecte une représentation photoréaliste d'une célébrité dans la requête.	entrée (prompt) : 29310472
sortie (image) : 15236754
62263041	Contenu dangereux	Détecte les contenus potentiellement dangereux.	entrée (prompt)
57734940
22137204	Contenu haineux	Détecte les sujets ou les contenus incitant à la haine.	entrée (prompt) : 57734940
sortie (image) : 22137204
74803281
29578790
42876398	Autre	Détecte d'autres problèmes de sécurité liés à la requête.	entrée (prompt) : 42876398
sortie (image) : 29578790, 74803281
39322892	Personnes/Visages	Détecte les personnes ou les visages s'ils ne sont pas autorisés dans les paramètres de sécurité de la requête.	sortie (image)
92201652	Informations personnelles	Détecte les informations permettant d'identifier personnellement l'utilisateur dans le texte, telles que les numéros de carte de crédit, les adresses personnelles ou d'autres informations de ce type.	entrée (prompt)
89371032
49114662
72817394	Contenu interdit	Détecte les contenus interdits dans la requête.	Entrée (prompt) : 89371032
Sortie (image) : 49114662, 72817394
90789179
63429089
43188360	Contenu à caractère sexuel	Détecte les contenus à caractère sexuel.	entrée (prompt) : 90789179
sortie (image) : 63429089, 43188360
35561574
35561575	Contenus tiers	Mesures de protection liées aux contenus tiers.	entrée (prompt)
sortie (image)
78610348	Contenu toxique	Détecte les sujets ou contenus toxiques dans le texte.	entrée (prompt)
61493863
56562880	Violence	Détecte les contenus violents dans l'image ou le texte.	entrée (prompt) : 61493863
sortie (image) : 56562880
32635315	Grossier	Détecte les sujets ou contenus vulgaires dans le texte.	entrée (prompt)
64151117	Célébrité ou enfant	Détecte une représentation photoréaliste d'une célébrité ou d'un enfant qui ne respecte pas les règles de sécurité de Google.	entrée (prompt)
sortie (image)
Limites
Les limites suivantes s'appliquent aux différentes tâches :

Limites relatives à la génération et à la modification d'images
Amplification des biais : bien qu'Imagen sur Agent Platform puisse générer des images de haute qualité, il peut y avoir des biais potentiels dans le contenu généré. Les images générées s'appuient sur les données d'entraînement du produit, qui peuvent inclure involontairement des biais susceptibles de perpétuer les stéréotypes ou de discriminer certains groupes. Une surveillance et une évaluation minutieuses sont nécessaires pour vous assurer que les résultats respectent la politique d'utilisation autorisée de Google et votre cas d'utilisation.
Transparence et divulgation: il peut être difficile pour les utilisateurs de différencier les images générées par l'IA des images non générées par l'IA. Lorsque vous utilisez des images générées par l'IA dans votre cas d'utilisation, il est important d'indiquer clairement aux utilisateurs que les images ont été générées par un système d'IA afin de garantir la transparence et de maintenir la confiance dans le processus. Nous avons appliqué des étiquettes de métadonnées aux images générées par l'IA pour réduire le risque de désinformation et dans le cadre de notre approche responsable de l'IA.
Contexte insuffisant : Imagen sur Agent Platform peut ne pas disposer de la compréhension contextuelle requise pour générer des images adaptées à toutes les situations ou audiences dans votre cas d'utilisation. Assurez-vous que vos images générées sont conformes au contexte, à l'objectif et à l'audience souhaités.
Déclarations trompeuses ou déceptives et authenticité : la modification d'images à l'aide d' Imagen sur Agent Platform peut entraîner la falsification ou la manipulation des images, ce qui peut entraîner la création de contenus trompeurs. Il est important de s'assurer que le processus de modification est utilisé de manière responsable, sans compromettre l'authenticité et la véracité des images modifiées. Nous avons appliqué des étiquettes de métadonnées aux images modifiées par l'IA pour réduire le risque de désinformation et dans le cadre de notre approche responsable de l'IA.
Déclarations trompeuses ou déceptives et authenticité : soyez prudent lorsque vous modifiez des images d' adultes ou d'enfants, car la modification d'images à l'aide d'Imagen sur Agent Platform peut entraîner la falsification ou la manipulation des images. Cela peut entraîner la création de contenus trompeurs. Il est important de s'assurer que le processus de modification est utilisé de manière responsable, sans compromettre l'authenticité et la véracité des images modifiées. Nous avons appliqué des étiquettes de métadonnées aux images modifiées par l'IA pour réduire le risque de désinformation et dans le cadre de notre approche responsable de l'IA.
Limites de Visual Captioning
Précision et sensibilité au contexte : Visual Captioning peut poser problème lors de la description précise d'images complexes ou ambiguës. Les descriptions générées peuvent ne pas toujours capturer le contexte complet ou les nuances du contenu visuel. Il est important de comprendre que les systèmes de sous-titrage automatique sont limités pour comprendre les images avec différents niveaux de complexité, et que leurs descriptions doivent être utilisées avec prudence, en particulier dans les contextes critiques ou sensibles.
Ambiguité et interprétations subjectives: les images peuvent souvent être ouvertes à plusieurs interprétations, et les sous-titres générés peuvent ne pas toujours correspondre à la compréhension ou aux attentes humaines. Différentes personnes peuvent voir et décrire des images différemment en fonction de leur expérience subjective et de leur parcours culturel. Il est essentiel de prendre en compte le risque d'ambiguïté et de subjectivité dans les descriptions d'images, et de fournir du contexte ou des interprétations supplémentaires si nécessaire.
Considérations relatives à l'accessibilité: bien que les sous-titres d'images automatisés permettent d'assurer l'accessibilité en fournissant des descriptions aux personnes malentendantes, il est important de savoir qu'elles ne peuvent pas remplacer entièrement les versions générées par l'humain ou des descriptions adaptées à des besoins spécifiques. Les sous-titres automatiques peuvent ne pas inclure le niveau de détail ou de compréhension contextuelle nécessaire pour certains cas d'utilisation d'accessibilité.
Limites de Visual Question Answering (VQA)
Confiance et incertitude: les modèles VQA peuvent parfois fournir des réponses avec une confiance non justifiée, même lorsque la bonne réponse est incertaine ou ambiguë. Il est essentiel de communiquer l'incertitude du modèle et de fournir des scores de confiance appropriés ou des réponses alternatives en cas d'ambiguïté, plutôt que de transmettre un faux sentiment de certitude.
Pratiques recommandées
Pour utiliser cette technologie de manière sécurisée et responsable, il est également important de prendre en compte d'autres risques spécifiques à votre cas d'utilisation, aux utilisateurs et au contexte commercial en plus des protections techniques intégrées.

Nous vous recommandons de suivre les étapes ci-dessous :

Évaluez les risques de sécurité de votre application.
Pensez à apporter des ajustements pour limiter les risques de sécurité.
Effectuez des tests de sécurité adaptés à votre cas d'utilisation.
Encouragez les utilisateurs à envoyer des commentaires et surveillez le contenu.
Autres ressources sur l'IA responsable
Découvrez l'IA responsable pour les grands modèles de langage (Large Language Models, LLM).
Découvrez les recommandations de Google pour les pratiques d'IA responsables.
Consultez notre blog, Un programme partagé pour la IA responsableIA.
Envoyer des commentaires sur Imagen sur Agent Platform
Si vous recevez un résultat ou une réponse inexact, ou si vous pensez que cela n'est pas fiable, vous pouvez nous le signaler en envoyant des commentaires. Vos commentaires peuvent nous aider à améliorer Imagen sur Agent Platform et l'avancé de Google au sens large dans le monde de l'IA.

Les commentaires pouvant être lisibles par un humain, veuillez ne pas soumettre de données contenant des informations personnelles, confidentielles ou sensibles.

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

Language
