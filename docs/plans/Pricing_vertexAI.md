.Passer au contenu principal
Google Cloud
Aperçu
Solutions
Produits
Tarifs
Ressources
Recherche
/

Docs
Assistance

Français
Console

 Cette page a été traduite par l'API Cloud Translation.
Switch to English
Tarifs
Coût de création et de déploiement de modèles d'IA dans Vertex AI
Modèles Google
Gemini 3
Gemini 2.5
Gemini 2.0
Tarification de Vertex AI Model Optimizer (expérimental)*
Autres modèles Gemini
Imagen
Veo
Lyria
Comprendre les coûts d'embedding pour vos applications d'IA
Tarifs de la complétion de code de Vertex AI
Traduction (texte)
Prix du stockage du cache de contexte pour la mise en cache explicite
Débit provisionné
Réglage des modèles
Comparer les tarifs des modèles partenaires sur Vertex AI
Modèles d'AI21 Labs
Modèles Claude d'Anthropic
Modèles de Deepseek
Modèles de MiniMax
Modèles de Moonshot
Modèles de Qwen
Modèles d'OpenAI
Modèles Llama de Meta
Modèles de Mistral AI
Coût de création et de déploiement de modèles d'IA dans Vertex AI
Les tarifs sont indiqués en dollars américains (USD). Si vous ne payez pas en USD, les tarifs indiqués dans votre devise sur la page des SKU de Cloud Platform s'appliquent.

Vous n'êtes facturé que pour les requêtes qui renvoient un code de réponse 200. Les requêtes renvoyant d'autres codes de réponse, tels que les codes 4xx et 5xx, ne sont pas facturées pour l'entrée ou la sortie.

Cette page présente les tarifs de l'IA générative sur Vertex AI. Pour tous les autres tarifs de Vertex AI, y compris les services ML Platform et MLOps, consultez la page des tarifs de Vertex AI.

Modèles Google
Gemini 3
Modèle	Type	Prix (pour 1 million de jetons) <= 200 000 jetons d'entrée	Prix (pour 1 million de jetons) > 200 000 jetons en entrée	Prix (pour 1 million de jetons) <= 200 000 jetons d'entrée mis en cache	Prix (par million de jetons) > 200 000 jetons d'entrée mis en cache	Prix (pour 1 million de jetons) <= 200 000 jetons d'entrée avec l'API par lots	Prix (pour 1 million de jetons) > 200 000 jetons d'entrée avec l'API par lot
Gemini 3 Pro (preview)
Entrée (texte, image, vidéo, audio)	2 $	4 $	0,2 $	0,4 $	1 $	2 $
Sortie textuelle (réponse et raisonnement)	12 $	18 $	N/A	N/A	6 $	9 $
Sortie d'image**	120 $	N/A	N/A	N/A	60 $	N/A
Aperçu de Gemini 3 Flash
Entrée (texte, image, vidéo)	0,5 $	0,5 $	0,05 $	0,05 $	0,25 $	0,25 $
Entrée (audio)	1 $	1 $	0,1 $	0,1 $	0,5 $	0,5 $
Sortie textuelle (réponse et raisonnement)	3 $	3 $	N/A	N/A	1,5 $	1,5 $
Ancrage avec la recherche Google et ancrage Web pour les entreprises	Inclut 5 000 requêtes de recherche par mois sans frais, agrégées sur tous les modèles Gemini 3.

Les requêtes de recherche qui dépassent ces limites sont facturées au tarif de 14$pour 1 000 requêtes de recherche. Une requête envoyée par un client à Gemini peut générer une ou plusieurs requêtes dans la recherche Google (ou Web Grounding pour Enterprise). Chaque requête de recherche individuelle effectuée vous sera facturée. La facturation commencera le 5 janvier 2026.

Les jetons d'entrée fournis par l'ancrage avec la recherche Google ou l'ancrage Web pour les entreprises ne sont pas facturés.

Veuillez contacter l'équipe de gestion de votre compte si vous avez besoin de plus d'un million de requêtes ancrées par jour.
Ancrage avec Google Maps	Inclut 5 000 requêtes de recherche par mois sans frais, agrégées sur tous les modèles Gemini 3.

Les requêtes Maps qui dépassent ces limites sont facturées 14$par tranche de 1 000 requêtes. Une requête envoyée par un client à Gemini peut générer une ou plusieurs requêtes à Google Maps. Chaque requête individuelle exécutée vous sera facturée. La facturation commencera le 5 janvier 2026

Les jetons d'entrée fournis par Google Maps ne sont pas facturés.
Ancrage basé sur vos données	2,50 $ par ensemble de 1 000 requêtes.
* Si le contexte d'entrée d'une requête dépasse 200 000 jetons, tous les jetons (entrée et sortie) sont facturés aux tarifs du contexte long.
** Une image de sortie 1K (1024 x 1024) et 2K (2048 x 2048) consomme 1 120 jetons de sortie d'image, soit l'équivalent de 0,134 $/image générée. Une image 4K (4096 x 4096) consomme 2 000 jetons de sortie d'image, soit l'équivalent de 0,24 $par image générée.

Gemini 2.5
Modèle	Type	Prix (pour 1 million de jetons) <= 200 000 jetons d'entrée	Prix (pour 1 million de jetons) > 200 000 jetons en entrée	Prix (pour 1 million de jetons) <= 200 000 jetons d'entrée mis en cache	Prix (par million de jetons) > 200 000 jetons d'entrée mis en cache	Prix (pour 1 million de jetons) <= 200 000 jetons d'entrée avec l'API par lots	Prix (pour 1 million de jetons) > 200 000 jetons d'entrée avec l'API par lot
Gemini 2.5 Pro
Entrée (texte, image, vidéo, audio)	1,25 $	2,5 $	0,125 $	0,250 $	0,625 $	1,25 $
Sortie textuelle (réponse et raisonnement)	10 $	15 $	N/A	N/A	5 $	7,5 $
Gemini 2.5 Pro
Utilisation sur ordinateur – Preview
Entrée (texte, image, vidéo, audio)	1,25 $	2,5 $	N/A	N/A	N/A	N/A
Sortie textuelle (réponse et raisonnement)	10 $	15 €	N/A	N/A	N/A	N/A


Gemini 2.5
Flash
Entrée (texte, image, vidéo)	0,30 $	0,30 $	0,030 $	0,030 $	0,15 $	0,15 $
Entrée audio	1 $	1 $	0,100 $	0,100 $	0,5 $	0,5 $
Sortie textuelle (réponse et raisonnement)	2,50 $	2,50 $	N/A	N/A	1,25 $	1,25 $
Sortie d'image***	30 $	30 $	N/A	N/A	15 $	15 $




API Gemini 2.5 Flash en direct
1 million de jetons de texte en entrée	0,5 $	0,5 $	N/A	N/A	N/A	N/A
1 million de jetons audio en entrée	3 $	3 $	N/A	N/A	N/A	N/A
1 million de jetons d'entrée vidéo/image	3 $	3 $	N/A	N/A	N/A	N/A
1 million de jetons de texte en sortie	2 $	2 $	N/A	N/A	N/A	N/A
1 million de jetons audio en sortie	12 $	12 $	N/A	N/A	N/A	N/A



Gemini 2.5 Flash Lite
Entrée (texte, image, vidéo)	0,1 $	0,1 $	0,010 $	0,010 $	0,05 $	0,05 $
Entrée audio	0,3 $	0,3 $	0,030 $	0,030 $	0,15 $	0,15 $
Sortie textuelle (réponse et raisonnement)	0,4 $	0,4 $	N/A	N/A	0,2 $	0,2 $


Ancrage avec la recherche Google	Gemini 2.0 Flash, 2.5 Flash et 2.5 Flash-Lite incluent 1 500 requêtes ancrées combinées par jour sans frais supplémentaires. Gemini 2.5 Pro inclut 10 000 requêtes ancrées par jour sans frais supplémentaires.

Les requêtes ancrées qui dépassent ces limites sont facturées 35$par tranche de 1 000 requêtes ancrées.

Une requête ancrée est une demande envoyée à Gemini qui effectue une ou plusieurs requêtes dans la recherche Google&ast;&ast;. Même si plusieurs requêtes de recherche sont envoyées à la recherche Google, une seule requête ancrée vous sera facturée.

Veuillez contacter l'équipe de gestion de votre compte si vous avez besoin de plus d'un million de requêtes ancrées par jour.

Ancrage Web pour entreprise	45$pour 1 000 requêtes ancrées. Une requête ancrée est une demande envoyée à Gemini qui effectue une ou plusieurs requêtes à l'ancrage Web pour les entreprises**. Même si plusieurs requêtes de recherche sont envoyées à la recherche Google, une seule requête ancrée vous sera facturée.

Si vous avez besoin de plus d'un million de requêtes ancrées par jour, veuillez contacter l'équipe de gestion de votre compte.
Ancrage basé sur vos données	2,5 $ par tranche de 1 000 requêtes.
Ancrage avec Google Maps	25$pour 1 000 requêtes ancrées.

Un prompt ancré est une requête envoyée à Gemini qui effectue au moins une requête à Google Maps.
* Si le contexte d'entrée d'une requête dépasse 200 000 jetons, tous les jetons (entrée et sortie) sont facturés aux tarifs de contexte long.
** L'ancrage avec la recherche Google et l'ancrage Web pour les entreprises ne sont facturés que lorsqu'une requête renvoie des résultats Web (c'est-à-dire des résultats contenant au moins une URL d'ancrage issue du Web). Des frais d'utilisation des modèles Gemini s'appliquent séparément.
*** Une image de 1 024 x 1 024 consomme 1 290 jetons. Le nombre de jetons par image varie en fonction de la résolution de l'image. Pour en savoir plus sur le calcul des jetons, vous pouvez consulter notre documentation.
**** La facturation de Computer Use utilise le SKU Gemini 2.5 Pro. Pour séparer les coûts de Computer Use, appliquez des tags de facturation. Pour en savoir plus, cliquez ici.

Explication de la facturation de la fenêtre de contexte de session Live API : vous êtes facturé par tour pour tous les jetons présents dans la fenêtre de contexte de session. La fenêtre de contexte de la session inclut les nouveaux jetons (tour actuel) et tous les jetons accumulés lors des tours précédents. Cela signifie que les jetons des tours précédents sont retraités et pris en compte dans chaque nouveau tour, jusqu'à la taille de la fenêtre de contexte que vous avez configurée. Un "tour" correspond à une entrée utilisateur et à la réponse du modèle.
Mode audio proactif : lorsqu'il est activé, les jetons d'entrée sont facturés pendant que LiveAPI écoute. Les jetons de sortie ne sont facturés que lorsque l'API répond.
Lorsque la transcription audio en texte est activée, tous les jetons de texte générés pour la transcription sont facturés au tarif de sortie des jetons de texte.
Gemini 2.0
Gemini 2.0 est facturé en fonction des jetons. Pour calculer le nombre de jetons d'entrée dans votre requête avant de l'envoyer, vous pouvez utiliser le tokenizer du SDK ou l'API countTokens. Si votre requête échoue et renvoie une erreur 400 ou 500, les jetons utilisés ne vous seront pas facturés.

Utilisez le bouton bascule dans la grille tarifaire pour comparer la tarification basée sur les jetons et la tarification basée sur les modalités.

Tarification basée sur les jetons
Tarifs basés sur les modalités
Modèle	Type	Prix	Prix avec l'API Batch




Gemini 2.0 Flash
1 million de jetons en entrée	0,15 $	0,075 $
1 million de jetons audio en entrée	1,00 $	0,50 $
1 million de jetons de texte de sortie	0,60 $	0,30 $
Ajustement pour 1 million de jetons d'entraînement	3 $	




Génération d'images avec Gemini 2.0 Flash
1 million de jetons en entrée	0,15 $
1 million de jetons audio en entrée	1,00 $
1 million de jetons vidéo en entrée	3 $
1 million de jetons de texte en sortie	0,60 $
1 million de jetons d'image en sortie	$30.00




API Gemini 2.0 Flash Live
1 million de jetons de texte en entrée	0,5 $
1 million de jetons audio en entrée	3 $
1 million de jetons d'entrée vidéo/image	3 $
1 million de jetons de texte en sortie	2 $
1 million de jetons audio en sortie	12 $




Gemini 2.0 Flash-Lite
1 million de jetons en entrée	0,075 $	0,0375 $
1 million de jetons audio en entrée	0,075 $	0,0375 $
1 million de jetons de texte de sortie	0,30 $	0,15 $
Ajustement pour 1 million de jetons d'entraînement	1,00 $	


Ancrage avec la recherche Google	Gemini 2.0 Flash et 2.5 Flash incluent 1 500 requêtes ancrées par jour au total,sans frais supplémentaires.

Les requêtes ancrées qui dépassent ces limites sont facturées 35$par tranche de 1 000 requêtes ancrées.

Une requête ancrée est une demande envoyée à Gemini qui effectue une ou plusieurs requêtes dans la recherche Google*. Même si plusieurs requêtes de recherche sont envoyées à la recherche Google, une seule requête ancrée vous sera facturée.

Si vous avez besoin de plus d'un million de requêtes ancrées par jour, veuillez contacter l'équipe de gestion de votre compte.

Ancrage Web pour entreprise	45$pour 1 000 requêtes ancrées. Un prompt ancré est une requête envoyée à Gemini qui effectue une ou plusieurs requêtes à l'ancrage Web pour les entreprises*. Même si plusieurs requêtes de recherche sont envoyées à la recherche Google, une seule requête ancrée vous sera facturée.

Si vous avez besoin de plus d'un million de requêtes ancrées par jour, veuillez contacter l'équipe de gestion de votre compte.
Ancrage basé sur vos données	2,5 $ pour 1 000 requêtes à partir du 16 juin 2025.


Ancrage avec Google Maps	Les modèles Gemini incluent un certain nombre de requêtes ancrées quotidiennes sans frais supplémentaires :
Gemini Flash et Flash-Lite : 1 500 requêtes ancrées par jour au total.
Gemini Pro : 10 000 requêtes ancrées par jour.

Les requêtes ancrées qui dépassent ces limites sont facturées 25$par tranche de 1 000 requêtes ancrées.

Un prompt ancré est une requête envoyée à Gemini qui effectue au moins une requête à Google Maps.

Si vous avez besoin de plus d'un million de requêtes ancrées par jour, veuillez contacter l'équipe de gestion de votre compte.
* Les tarifs sont indiqués en dollars américains (USD). Si vous ne payez pas en USD, les tarifs indiqués dans votre devise sur la page des SKU de Cloud Platform s'appliquent.
* Les jetons d'entraînement sont calculés en multipliant le nombre total de jetons dans votre ensemble de données d'entraînement par le nombre d'époques.
* Les PDF sont facturés comme des entrées d'image, une page de PDF équivalant à une image.
* Le point de terminaison du modèle réglé a le même prix de prédiction que le modèle de base.
* L'ancrage avec la recherche Google et l'ancrage Web pour les entreprises ne sont facturés que lorsqu'une requête renvoie des résultats Web (c'est-à-dire des résultats contenant au moins une URL d'ancrage issue du Web). Des frais d'utilisation des modèles Gemini s'appliquent séparément.
* API Gemini 2.0 Flash Live : 25 jetons par seconde d'audio (entrée/sortie), 258 jetons par seconde de vidéo (entrée). L'ancrage avec la recherche Google reste gratuit tant que l'API Gemini 2.0 Flash Live est en preview.

Explication de la facturation de la fenêtre de contexte de session Live API : vous êtes facturé par tour pour tous les jetons présents dans la fenêtre de contexte de session. La fenêtre de contexte de la session inclut les nouveaux jetons (tour actuel) et tous les jetons accumulés lors des tours précédents. Cela signifie que les jetons des tours précédents sont retraités et pris en compte dans chaque nouveau tour, jusqu'à la taille de la fenêtre de contexte que vous avez configurée. Un "tour" correspond à une entrée utilisateur et à la réponse du modèle.
Lorsque la transcription audio en texte est activée, tous les jetons de texte générés pour la transcription sont facturés au tarif de sortie des jetons de texte.
Tarification de Vertex AI Model Optimizer (expérimental)*
L'optimiseur de modèle Vertex AI simplifie l'utilisation de Gemini pour les entreprises en fournissant un seul méta-point de terminaison pour les requêtes de modèle Gemini. Les clients qui utilisent ce service n'ont pas à spécifier s'ils souhaitent utiliser Flash, Pro ou une version spécifique. Au lieu de cela, ils fournissent simplement un paramètre configurable (coût, qualité ou équilibre) pour indiquer leurs préférences, et Model Optimizer applique le niveau d'intelligence approprié à la tâche en envoyant chaque requête au modèle le plus adapté.

L'optimiseur de modèle Vertex AI applique une tarification dynamique. Cela signifie que le prix moyen par jeton dépend du niveau d'intelligence du modèle appliqué pour effectuer la tâche. C'est pourquoi nous fournissons ci-dessous des exemples de tarification pour illustrer des scénarios probables en fonction de votre paramètre de configuration (voir les tableaux ci-dessous). Les SKU Model Optimizer sont des SKU à 1 $qui servent d'unité d'achat pour votre facturation. Vous êtes toujours facturé en fonction de votre consommation après avoir utilisé les modèles.

Rapport E/S de 5:1	Exemple 1
Chatbot	REMARQUE : Ces fourchettes ne sont pas garanties, et les résultats individuels des clients peuvent varier.
Préférence du client	Jetons d'entrée du client envoyés au modèle	Jetons de sortie client envoyés au MO	Prix d'entrée moyen par million de jetons (fourchette haute)	Prix de sortie moyen par million de jetons (fourchette haute)	Prix d'entrée moyen par million de jetons (fourchette basse)	Prix de sortie moyen par million de jetons (fourchette basse)
Coût	10 000 000	2 000 000	0,63 $	2,50 $	0,16 $	0,63 $
Équilibré	10 000 000	2 000 000	1,26 $	5 $	0,63 $	2,50 $
Qualité	10 000 000	2 000 000	1,89 $	7,50 $	1,26 $	5 $	
1:20 Ratio E/S	Exemple 2 : Génération de contenu	
Préférence du client	Jetons d'entrée du client envoyés au modèle	Jetons de sortie client envoyés au MO	Prix d'entrée moyen par million de jetons (fourchette haute)	Prix de sortie moyen par million de jetons (fourchette haute)	Prix d'entrée moyen par million de jetons (fourchette basse)	Prix de sortie moyen par million de jetons (fourchette basse)
Coût	1 000 000	20 000 000	0,63 $	2,50 $	0,16 $	0,63 $
Équilibré	1 000 000	20 000 000	1,26 $	5 $	0,63 $	2,50 $
Qualité	1 000 000	20 000 000	1,89 $	7,50 $	1,26 $	5 $	
* Model Optimizer est une offre expérimentale payante qui peut acheminer les requêtes vers des versions expérimentales de Gemini sur Vertex.

Autres modèles Gemini
Tous les modèles Gemini autres que Gemini 2.0 ou Gemini 2.5 sont facturés en fonction des modalités, comme le nombre de caractères, d'images ou de secondes de vidéo/d'audio. Les entrées de type texte sont facturées pour chaque tranche de 1 000 caractères d'entrée (requête) et pour chaque tranche de 1 000 caractères de sortie (réponse). Les caractères sont comptabilisés par points de code UTF-8, et les espaces sont exclus du décompte, ce qui donne environ quatre caractères par jeton. Les requêtes de prédiction qui aboutissent à des réponses filtrées ne sont facturées que pour l'entrée. À la fin de chaque cycle de facturation, les fractions de centime (0,01 $) sont arrondies à un centime. Les entrées de type média sont facturées par image ou par seconde (vidéo). Si votre requête échoue et renvoie une erreur 400 ou 500, les jetons utilisés ne vous seront pas facturés.

Modèle	Caractéristique	Type	Prix
( =< 128 000 jetons d'entrée)	Prix
(plus de 128 000 jetons d'entrée)
Gemini 1.5 Flash	Multimodal	Entrée image
Entrée vidéo
Entrée textuelle
Entrée audio
0,00002 $ par image
0,00002$par seconde
0,00001875$pour 1 000 caractères
0,000002$par seconde
0,00004 $ par image
0,00004$par seconde
0,0000375$pour 1 000 caractères
0,000004$par seconde
Sortie textuelle	0,000075 $ pour 1 000 caractères	0,00015 $ pour 1 000 caractères
Réglage*	Jeton de formation	8 $ / M de jetons
Gemini 1.5 Pro	Multimodal	Entrée image
Entrée vidéo
Entrée textuelle
Entrée audio
0,00032875 $ par image
0,00032875$par seconde
0,0003125$pour 1 000 caractères
0,00003125$par seconde
0,0006575 $ par image
0,0006575$par seconde
0,000625$pour 1 000 caractères
0,0000625$par seconde
Sortie textuelle	0,00125 $ pour 1 000 caractères	0,0025 $ pour 1 000 caractères
Réglage*	Jeton de formation	80 $ / M de jetons
Gemini 1.0 Pro	Multimodal	Entrée image
Entrée vidéo
Entrée textuelle
0,0025 $ par image
0,002 $ par seconde
0,000125 $ pour 1 000 caractères
Sortie textuelle	0,000375 $ pour 1 000 caractères
Ancrage avec la recherche Google	Texte	35$pour 1 000 requêtes ancrées.

Une requête ancrée est une demande envoyée à Gemini qui effectue une ou plusieurs requêtes dans la recherche Google*. Même si plusieurs requêtes de recherche sont envoyées à la recherche Google, une seule requête ancrée vous sera facturée.

Veuillez contacter l'équipe de gestion de votre compte si vous avez besoin de plus d'un million de requêtes ancrées par jour.
Ancrage Web pour les entreprises	Texte	45$pour 1 000 requêtes ancrées.

Une requête ancrée est une demande envoyée à Gemini qui effectue une ou plusieurs requêtes à l'ancrage Web pour les entreprises*. Même si plusieurs requêtes de recherche sont envoyées à la recherche Google, une seule requête ancrée vous sera facturée.

Veuillez contacter l'équipe de gestion de votre compte si vous avez besoin de plus d'un million de requêtes ancrées par jour.
Ancrage basé sur vos données	Texte	2,5 $ par tranche de 1 000 requêtes à partir du 16 juin 2025.
* Les tarifs sont indiqués en dollars américains (USD). Si vous ne payez pas en USD, les tarifs indiqués dans votre devise sur la page des SKU de Cloud Platform s'appliquent.
* Si le contexte d'une requête dépasse 128 000 jetons, tous les jetons sont facturés au tarif du contexte long.
* Les modèles Gemini sont disponibles en mode par lot avec une remise de 50 %.
* Gemini 1.0 Pro ne prend en charge qu'une fenêtre de contexte de 32 000 jetons maximum.
* Les PDF sont facturés comme des entrées d'image, une page de PDF équivalant à une image.
* Le point de terminaison du modèle réglé a le même prix de prédiction que le modèle de base.
* L'ancrage avec la recherche Google et l'ancrage Web pour les entreprises ne sont facturés que lorsqu'une requête renvoie des résultats Web (c'est-à-dire des résultats contenant au moins une URL d'ancrage issue du Web). Des frais d'utilisation des modèles Gemini s'appliquent séparément.

Imagen
Avec Imagen sur Vertex AI, vous pouvez générer de nouvelles images ou modifier des images existantes sur la base de requêtes de texte que vous fournissez, modifier partiellement des images à l'aide d'une zone de masquage que vous définissez, et bien d'autres fonctionnalités encore.

Modèle	Fonctionnalité	Description	Entrée	Sortie	Prix
Imagen 4 Ultra	Génération d'images	Générer une image	Requête textuelle	Image	0,06 $ par image
Imagen 4	Augmentation de la résolution	Augmenter la résolution d'une image générée à 2K, 3K ou 4K	Image	Image	0,06 $ par image
Imagen 4	Génération d'images	Générer une image	Requête textuelle	Image	0,04 $ par image
Imagen 4 Fast	Génération d'images	Générer une image	Requête textuelle	Image	0,02 $ par image
Imagen 3	Génération d'images	Générer une image
Modifier une image
Personnaliser une image	Requête textuelle	Image	0,04 $ par image
Imagen 3 Fast	Génération d'images	Générer une image	Requête textuelle	Image	0,02 $ par image
Imagen 2, Imagen 1	Génération d'images	Générer une image	Requête textuelle	Images	0,020 $ par image
Imagen 2, Imagen 1	Édition d'images	Modifier une image par une approche avec masque ou sans masque	Image/Requête textuelle	Images	0,020 $ par image
Imagen 1	Augmentation de la résolution	Augmenter la résolution d'une image générée à 2k ou 4k	Images	Images	0,003 $ par image
Imagen 1	Affinage	Permettre l'utilisation d'un "sujet" fourni par l'utilisateur dans les requêtes Imagen (entraînement "few-shot")	Sujet(s) avec identifiant textuel et 4 à 8 images par sujet	Modèle affiné (après l'entraînement avec des sujets fournis par l'utilisateur)	$ par heure-nœud (tarifs d'entraînement personnalisé Vertex AI)
Imagen	Visual Captioning	Générer une légende textuelle courte ou longue pour une image	Images	Légende textuelle	0,0015 $ par image
Imagen	Questions/réponses visuelles	Fournir une réponse basée sur une question faisant référence à une image	Image/Requête textuelle	Réponse textuelle	0,0015 $ par image
Imagen	Product Recontext	Réinventez des produits dans une nouvelle scène	1 à 3 images du même produit et un prompt textuel décrivant la scène souhaitée	Image	0,12 $ par image
Vertex Virtual Try-On	Créez des images de personnes portant différents vêtements	1 image d'une personne et 1 image de vêtements	Image	0,06 $ par image
Les tarifs sont indiqués en dollars américains (USD). Si vous ne payez pas en USD, les tarifs indiqués dans votre devise sur la page des codes SKU Cloud Platform s'appliquent.

Veo
Veo crée des vidéos d'une qualité incroyable dans un large éventail de sujets et de styles, avec une meilleure compréhension des lois de la physique réelle et des nuances des mouvements et expressions humains.

Modèle	Fonctionnalité	Description	Entrée	Sortie	Résolution de sortie	Prix
Veo 3.1	Génération de vidéos et d'audio	Générez des vidéos de haute qualité avec des effets sonores/vocaux synchronisés à partir d'un prompt textuel ou d'une image de référence.	Requête textuelle/image	Vidéo et audio	720p, 1080p	0,40 $/seconde
Veo 3.1	Génération de vidéos	Générez des vidéos de haute qualité à partir d'un prompt textuel ou d'une image de référence.	Requête textuelle/image	Vidéo	720p, 1080p	0,20 $/seconde
Veo 3.1 Fast	Génération de vidéos et d'audio	Générez plus rapidement des vidéos avec des effets sonores/vocaux synchronisés à partir d'un prompt textuel ou d'une image de référence	Requête textuelle/image	Vidéo et audio	720p, 1080p	0,15 $/seconde
Veo 3.1 Fast	Génération de vidéos	Générez plus rapidement des vidéos à partir d'un prompt textuel ou d'une image de référence	Requête textuelle/image	Vidéo	720p, 1080p	0,10 $/seconde
Veo 3	Génération de vidéos et d'audio	Générez des vidéos de haute qualité avec des effets sonores/vocaux synchronisés à partir d'un prompt textuel ou d'une image de référence.	Requête textuelle/image	Vidéo et audio	720p, 1080p	0,40 $/seconde
Veo 3	Génération de vidéos	Générez des vidéos de haute qualité à partir d'un prompt textuel ou d'une image de référence.	Requête textuelle/image	Vidéo	720p, 1080p	0,20 $/seconde
Veo 3 Fast	Génération de vidéos et d'audio	Générez plus rapidement des vidéos avec des effets sonores/vocaux synchronisés à partir d'un prompt textuel ou d'une image de référence	Requête textuelle/image	Vidéo et audio	720p, 1080p	0,15 $/seconde
Veo 3 Fast	Génération de vidéos	Générez plus rapidement des vidéos à partir d'un prompt textuel ou d'une image de référence	Requête textuelle/image	Vidéo	720p, 1080p	0,10 $/seconde
Veo 2	Génération de vidéos	Générez des vidéos à partir d'un prompt textuel ou d'une image de référence	Requête textuelle/image	Vidéo	720p	0,50 $/seconde
Veo 2	Contrôles avancés	Générez des vidéos par interpolation des images de début et de fin, prolongez les vidéos générées et appliquez des commandes de caméra.	Requête textuelle/image/vidéo	Vidéo	720p	0,50 $/seconde
Lyria
Lyria 2 génère de la musique instrumentale de haute qualité, idéale pour les compositions sophistiquées et l'exploration créative détaillée où la nuance est essentielle.

Modèle	Fonctionnalité	Description	Entrée	Sortie	Prix
Lyria 2	Génération de musique	Générer de la musique à partir d'un prompt textuel	Requête textuelle	Musique	0,06 $ par tranche de 30 secondes
Comprendre les coûts d'embedding pour vos applications d'IA
Modèle	Type	Région	Prix par tranche de 1 000 tokens d'entrée
Gemini Embedding	Entrée	Monde	
Requêtes en ligne : 0,00015 $
Requêtes par lot : 0,00012 $
Sortie	Monde	
Requêtes en ligne : sans frais
Requêtes par lot : sans frais
Modèle	Type	Région	Prix par tranche de 1000 caractères
Embeddings pour le texte
(à l'exclusion de Gemini Embedding)	Entrée	Globaux	
Requêtes en ligne : 0,000025 $
Requêtes par lot : 0,00002 $
Sortie	Monde	
Requêtes en ligne : sans frais
Requêtes par lot : sans frais
Modèle	Fonctionnalité	Description	Entrée	Sortie	Prix
multimodalembedding	Embeddings multimodaux : texte	Générer des représentations vectorielles continues en utilisant du texte comme entrée	Texte	Embeddings	0,0002 $ pour 1000 caractères d'entrée
Embeddings multimodaux : image	Générer des représentations vectorielles continues en utilisant une image comme entrée	Images	Embeddings	0,0001 $ par image d'entrée
Embeddings multimodaux : vidéo et plus	Vidéo Plus	Vidéo	Représentations vectorielles continues (jusqu'à 15 représentations vectorielles continues par minute de vidéo)	0,0020 $ par seconde de vidéo
Embeddings multimodaux : vidéo Standard	Vidéo Standard	Vidéo	Représentations vectorielles continues (jusqu'à 8 représentations vectorielles continues par minute de vidéo)	0,0010 $ par seconde de vidéo
Embeddings multimodaux : vidéo (essentiel)	Vidéo Essentiel	Vidéo	Représentations vectorielles continues (jusqu'à 4 représentations vectorielles continues par minute de vidéo)	0,0005 $ par seconde de vidéo
Modèle Open Source	Type	Prix par tranche de 1 000 tokens d'entrée
multilingual-e5-small	Entrée :
Sortie :

Entrée par lot :
Sortie par lot :	Requêtes en ligne : 0,000015 $
Requêtes en ligne : sans frais

Requêtes par lot : 0,0000075 $
Requêtes par lot : sans frais
multilingual-e5-large	Entrée :
Sortie :

Entrée par lot :
Sortie par lot :	Requêtes en ligne : 0,000025 $
Requêtes en ligne : sans frais

Requêtes par lot : 0,0000125 $
Requêtes par lot : sans frais
Les tarifs sont indiqués en dollars américains (USD). Si vous ne payez pas en USD, les tarifs indiqués dans votre devise sur la page des codes SKU Cloud Platform s'appliquent.

Tarifs de la complétion de code de Vertex AI
La prise en charge de l'IA générative sur Vertex AI est facturée pour chaque tranche de 1000 caractères d'entrée (requête) et pour chaque tranche de 1000 caractères de sortie (réponse). Les caractères sont comptabilisés avec les points de code UTF-8, et les espaces sont exclus du décompte. Pendant la phase de bêta, les frais sont réduits de 100 %. Les requêtes de prédiction qui aboutissent à des réponses filtrées ne sont facturées que pour l'entrée. À la fin de chaque cycle de facturation, les fractions de centime (0,01 $) sont arrondies à un centime.

Note: Prediction pricing for tuned model endpoints are the same as for the base foundation model.
Modèle	Type	Région	Prix par tranche de 1000 caractères
Codey pour la saisie de code	Entrée	Global	
Requêtes en ligne : 0,00025 $
Sortie	Global	
Requêtes en ligne : 0,0005 $
Les tarifs sont indiqués en dollars américains (USD). Si vous ne payez pas en USD, les tarifs indiqués dans votre devise sur la page des codes SKU Cloud Platform s'appliquent.

Traduction (texte)
Utilisez l'API Vertex AI et le LLM de traduction pour traduire du texte. Les traductions LLM ont tendance à être plus fluides et à sonner plus naturelles que celles des modèles de traduction classiques, mais elles sont disponibles dans moins de langues (en savoir plus).

Modèle	Méthode	Utilisation	Prix par million de caractères
LLM	Texte traduction*	Nombre de caractères d'entrée par mois	
10 $ par million de caractères*

Nombre de caractères de sortie par mois	
10 $ par million de caractères*

Les tarifs sont indiqués en dollars américains (USD). Si vous ne payez pas en USD, les tarifs indiqués dans votre devise sur la page des SKU de Cloud Platform s'appliquent.
* Le prix est calculé en fonction du nombre de caractères traités par le modèle. Pour en savoir plus sur le comptage de caractères, consultez la section Caractères facturés.

Prix du stockage du cache de contexte pour la mise en cache explicite
Modèle	Caractéristique	Type	Prix (pour 1 million de jetons)
<= 200 000 jetons en entrée	Prix (pour 1 million de jetons)
> 200 000 jetons d'entrée
Gemini 3 Pro	Stockage du cache de contexte	Entrée (texte, image, vidéo, audio)	4,5 $ (par million de jetons/heure)	4,5 $ (par million de jetons/heure)
Gemini 2.5 Pro	Stockage du cache de contexte	Entrée (texte, image, vidéo, audio)	4,5 $ (par million de jetons/heure)	4,5 $ (par million de jetons/heure)
Gemini 2.0 Flash	Stockage du cache de contexte	Entrée (texte, image, vidéo, audio)	1 $ (/M jetons/h)	1 $ (/M jetons/h)
Gemini 2.5 Flash Lite	Stockage du cache de contexte	Entrée (texte, image, vidéo, audio)	1 $ (/M jetons/h)	1 $ (/M jetons/h)
Modèles Gemini 2.0
Tarification basée sur les jetons
Tarifs basés sur les modalités

Modèle	
Type	Stockage
(M tok-heure)	Prix




Gemini 2.0 Flash
1 million de jetons en entrée	1,00 $	0,0375 $
1 million de jetons audio en entrée	1,00 $	0,25 $
1 million de jetons de texte de sortie	N/A	N/A


Gemini 2.0 Flash-Lite
1 million de jetons en entrée	1,00 $	0,01875 $
1 million de jetons audio en entrée	1,00 $	0,01875 $
1 million de jetons de texte de sortie	N/A	N/A
* Les tarifs sont indiqués en dollars américains (USD). Si vous ne payez pas en USD, les tarifs indiqués dans votre devise sur la page des SKU de Cloud Platform s'appliquent.
* Les PDF sont facturés comme des entrées d'image, une page de PDF équivalant à une image.
* Le point de terminaison du modèle réglé a le même prix de prédiction que le modèle de base.
* L'ancrage avec la recherche Google n'est facturé que pour les requêtes qui renvoient des résultats contenant au moins une URL d'ancrage issue du Web. Les frais d'utilisation standards du modèle Gemini s'appliquent également.

Débit provisionné
Le débit provisionné assure un débit pour vos besoins en IA générative et est facturé en unités de scaling pour l'IA générative, ou GSU. Pour en savoir plus sur le débit fourni par chaque GSU, cliquez ici. Vous pouvez également utiliser notre outil d'estimation en ligne ici.

Durée	Prix par GSU	Par
Engagement d'une semaine	1 200 $	Semaine
Engagement d'un mois	2 700 $	Mois
Engagement de 3 mois	2 400 $	Mois
Engagement sur un an	2 000 $	Mois
Exemple de calcul des coûts
Un utilisateur doit s'assurer qu'il peut gérer 10 requêtes par seconde (RPS) avec une entrée de 1 000 jetons de texte et 500 jetons audio,et recevoir une sortie de 300 jetons de texte en utilisant gemini-2.0-flash.

En utilisant le tableau des débits et des taux d'utilisation, nous savons que pour gemini-2.0-flash, le taux d'utilisation d'un jeton de texte en entrée est de 1 jeton, celui d'un jeton audio en entrée est de 7 jetons et celui d'un jeton de texte en sortie est de 4 jetons.

Le nombre total de jetons d'entrée de l'utilisateur est de 1 000* (1 jeton par jeton de texte d'entrée) + 500* (7 jetons par jeton audio d'entrée) = 4 500 jetons d'entrée ajustés par épuisement. Le nombre total de jetons de sortie de l'utilisateur est de 300 x 4 jetons par jeton de texte de sortie = 1 200 jetons de sortie ajustés par épuisement. En les additionnant, nous obtenons 4 500 jetons d'entrée ajustés pour la réduction + 1 200 jetons de sortie ajustés pour la réduction = 5 700 jetons au total par requête.

En multipliant le nombre total de jetons par requête par le nombre de RPS, nous obtenons 5 700 jetons au total par requête × 10 RPS = 57 000 jetons au total par seconde.

En divisant ce nombre par le débit total par seconde par GSU,nous obtenons 57 000 jetons au total par seconde ÷ 3 360 jetons par seconde par GSU = 16,96 GSU. L'incrément minimal d'achat de GSU pour ce modèle est de 1. L'utilisateur aurait donc besoin de 17 GSU.

Si l'utilisateur souhaitait maintenir ce débit pendant une semaine, cela lui coûterait 1 200 $ * 17 GSU = 20 400 $par semaine. S'ils souhaitaient maintenir ce débit pendant un mois, cela leur coûterait 2 700 $ * 17 GSU = 45 900 $par mois. S'ils souhaitaient maintenir ce débit pendant trois mois, cela leur coûterait 2 400 $ * 17 GSU = 40 800 $par mois. Enfin, s'ils souhaitaient maintenir ce débit pendant un an, cela leur coûterait 2 000 $ * 17 GSU = 34 000 $par mois.

Réglage des modèles
Le réglage de modèle est un moyen efficace de personnaliser les modèles volumineux pour vos tâches. Il s'agit d'une étape clé pour améliorer la qualité et l'efficacité du modèle. Le réglage du modèle offre les avantages suivants :

Une qualité supérieure pour vos tâches spécifiques
Robustesse accrue du modèle
Réduction de la latence et du coût d'inférence grâce à des requêtes plus courtes
Le réglage est facturé par million de jetons d'entraînement. Les jetons d'entraînement sont calculés en multipliant le nombre total de jetons dans votre ensemble de données d'entraînement par le nombre d'époques. Pour l'inférence de modèle, le point de terminaison du modèle Gemini réglé a le même prix de prédiction que le modèle de base.

Modèle	Type	Prix (par million de jetons d'entraînement)
Gemini 2.5 Pro	Réglage supervisé	25 $
Gemini 2.0 Flash	Affinage supervisé
Réglage des préférences	5 $
Gemini 2.5 Flash Lite	Affinage supervisé
Réglage des préférences	1,5 $
Gemma 3 27B IT	Réglage supervisé	6,83 $
Llama 3.1 8B	Réglage supervisé	0,67 $
Llama 3.2 1B	Réglage supervisé	0,28 $
Llama 3.2 3B	Réglage supervisé	0,61 $
Llama 3.3 70B	Réglage supervisé	6,72 $
Llama 4 Scout 17B 16E	Réglage supervisé	5,77 $
Qwen 3 32B	Réglage supervisé	6,57 $
* Les jetons d'entraînement sont calculés en multipliant le nombre total de jetons dans votre ensemble de données d'entraînement par le nombre d'époques.
* Le prix des prédictions pour un point de terminaison de modèle Gemini réglé est le même que pour le modèle de base.

Comparer les tarifs des modèles partenaires sur Vertex AI
Les modèles partenaires sont une liste organisée de modèles d'IA générative développés par les partenaires de Google. Les modèles partenaires sont proposés en tant qu'API gérées. Pour en savoir plus, consultez la présentation des modèles partenaires. Les sections suivantes présentent les détails de tarification des modèles de partenaires Google.

Modèles d'AI21 Labs
Modèle	Tarifs
Jamba 1.5 Large (obsolète)	Entrée : 2 $ par million de jetons
Sortie : 8 $ par million de jetons
Jamba 1.5 Mini (obsolète)	Entrée : 0,20 $ par million de jetons
Sortie : 0,40 $ par million de jetons
Modèles Claude d'Anthropic
Modèles avec des tarifs régionaux
Monde
us-east5
europe-west1
asia-southeast1
asia-east1
Modèle	Prix (pour 1 million de jetons) < 200 000 jetons en entrée	Prix (pour 1 million de jetons) >= 200 000 jetons d'entrée
Claude Opus 4.5	Entrée : 5 $
Sortie : 25 $

Entrée par lot : 2,50 $
Sortie par lot : 12,50 $

Écriture dans le cache (5 min) : 6,25 $
Écriture dans le cache (1 h) : 10 $

Accès au cache : 0,50 $

Écriture dans le cache par lot (5 min) : 3,125 $
Écriture dans le cache par lot (1 h) : 5 $
Accès au cache par lot : 0,25 $
Claude Sonnet 4.5	Entrée : 3 $
Sortie : 15 $

Entrée par lot : 1,50 $
Sortie par lot : 7,50 $

Écriture dans le cache (5 min) : 3,75 $
Écriture dans le cache (1 h) : 6 $

Accès au cache : 0,30 $

Écriture dans le cache par lot : 1,88 $
Accès au cache par lot : 0,15 $	Entrée : 6 $
Sortie : 22,50 $

Entrée par lot : 3 $
Sortie par lot : 11,25 $

Écriture dans le cache (5 min) : 7,50 $
Écriture dans le cache (1 h) : 12 $

Accès au cache : 0,60 $


Écriture dans le cache par lot : 3,75 $

Accès au cache par lot : 0,30 $
Claude Haiku 4.5	Entrée : 1 $
Sortie : 5 $

Entrée par lot : 0,50 $
Sortie par lot : 2,50 $

Écriture dans le cache (5 min) : 1,25 $
Écriture dans le cache (1 h) : 2 $

Accès au cache : 0,10 $

Écriture dans le cache par lot : 0,625 $
Accès au cache par lot : 0,05 $
* Si le contexte d'entrée d'une requête est supérieur ou égal à 200 000 jetons, tous les jetons (entrée et sortie) sont facturés aux tarifs du contexte long.

Modèles avec des prix uniformes dans toutes les régions
Modèle	Prix (pour 1 million de jetons) < 200 000 jetons en entrée	Prix (pour 1 million de jetons) >= 200 000 jetons d'entrée
Claude Opus 4.1	Entrée : 15 $
Sortie : 75 $

Entrée par lot : 7,50 $
Sortie par lot : 37,50 $

Écriture dans le cache (5 min) : 18,75 $
Écriture dans le cache (1 h) : 30 $

Accès au cache : 1,50 $

Écriture dans le cache par lot : 9,375 $
Accès au cache par lot : 0,75 $	N/A
Claude Opus 4	Entrée : 15 $
Sortie : 75 $

Entrée par lot : 7,50 $
Sortie par lot : 37,50 $

Écriture dans le cache (5 min) : 18,75 $
Écriture dans le cache (1 h) : 30 $

Accès au cache : 1,50 $

Écriture dans le cache par lot : 9,375 $
Accès au cache par lot : 0,75 $	N/A
Claude Sonnet 4	Entrée : 3 $
Sortie : 15 $

Entrée par lot : 1,50 $
Sortie par lot : 7,50 $

Écriture dans le cache pendant 5 min : 3,75 $
Écriture dans le cache pendant 1 h : 6 $

Accès au cache : 0,30 $

Écriture dans le cache par lot : 1,875 $
Accès au cache par lot : 0,15 $	Entrée : 6 $
Sortie : 22,50 $

Entrée par lot : 3 $
Sortie par lot : 11,25 $

Écriture dans le cache (5 min) : 7,50 $
Écriture dans le cache (1 h) : 12 $

Accès au cache : 0,60 $

Écriture dans le cache par lot : 3,75 $
Accès au cache par lot : 0,30 $
Claude 3.5 Haiku	Entrée : 0,80 $
Sortie : 4 $

Entrée par lot : 0,40 $
Sortie par lot : 2 $

Écriture dans le cache (5 min) : 1 $
Écriture dans le cache (1 h) : 1,60 $

Accès au cache : 0,08 $

Écriture dans le cache par lot : 0,50 $
Accès au cache par lot : 0,04 $	N/A
Claude 3 Haiku	Entrée : 0,25 $
Sortie : 1,25 $

Écriture dans le cache pendant 5 min : 0,30 $
Écriture dans le cache pendant 1 h : 0,50 $

Accès au cache : 0,03 $	N/A
Claude 3.7 Sonnet (obsolète)	Entrée : 3 $
Sortie : 15 $

Entrée par lot : 1,50 $
Sortie par lot : 7,50 $

Écriture dans le cache : 3,75 $
Accès au cache : 0,30 $

Écriture dans le cache par lot : 1,875 $
Accès au cache par lot : 0,15 $	N/A
Claude 3.5 Sonnet v2 (obsolète)	Entrée : 3 $
Sortie : 15 $

Entrée par lot : 1,50 $
Sortie par lot : 7,50 $

Écriture dans le cache : 3,75 $
Accès au cache : 0,30 $

Écriture dans le cache par lot : 1,875 $
Accès au cache par lot : 0,15 $	N/A
Claude 3.5 Sonnet (obsolète)	Entrée : 3 $
Sortie : 15 $

Écriture dans le cache : 3,75 $
Lecture dans le cache : 0,30 $	N/A
Claude 3 Opus (obsolète)	Entrée : 15 $
Sortie : 75 $

Écriture dans le cache : 18,75 $
Lecture dans le cache : 1,50 $	N/A
* Si le contexte d'entrée d'une requête est supérieur ou égal à 200 000 jetons, tous les jetons (entrée et sortie) sont facturés aux tarifs du contexte long.

Tarifs des outils
Outil	Prix
Demande de recherche sur le Web	10$par tranche de 1 000 recherches
Modèles compatibles : Claude Haiku 4.5, Claude Sonnet 4.5, Claude Sonnet 4, Claude Opus 4.1 et Claude Opus 4.
* Si le contexte d'entrée d'une requête est supérieur ou égal à 200 000 jetons, tous les jetons (entrée et sortie) sont facturés aux tarifs du contexte long.

Modèles de Deepseek
Modèle	Tarifs
DeepSeek-V3.1	Entrée : 0,60 $ par million de jetons
Sortie : 1,70 $ par million de jetons

Entrée par lot : 0,30 $ par million de jetons
Sortie par lot : 0,85 $ par million de jetons
DeepSeek-V3.2 *	Entrée : 0,56 $ par million de jetons
Sortie : 1,68 $ par million de jetons

Entrée par lot : 0,28 $ par million de jetons
Sortie par lot : 0,84 $ par million de jetons
DeepSeek-R1 (0528)	Entrée : 1,35 $ par million de jetons
Sortie : 5,40 $ par million de jetons

Entrée par lot : 0,675 $ par million de jetons
Sortie par lot : 2,70 $ par million de jetons
DeepSeek-OCR	Entrée : 0,30 $ par million de jetons (ou 0,0003 $par page)
Sortie : 1,20 $ par million de jetons (ou 0,00012 $par page)
Disponible sans frais jusqu'au 17 décembre 2025.
Modèles de MiniMax
Modèle	Tarifs
MiniMax-M2	Entrée : 0,30 $ par million de jetons
Sortie : 1,20 $ par million de jetons
Modèles de Moonshot
Modèle	Tarifs
Kimi-K2-Thinking	Entrée : 0,60 $ par million de jetons
Sortie : 2,50 $ par million de jetons
Modèles de Qwen
Modèle	Tarifs
Qwen3-Next-80B-Thinking	Entrée : 0,15 $ par million de jetons
Sortie : 1,20 $ par million de jetons
Qwen3-Next-80B-Instruct	Entrée : 0,15 $ par million de jetons
Sortie : 1,20 $ par million de jetons
Qwen3-Coder-480B-A35B-Instruct	Entrée : 0,22 $ par million de jetons
Sortie : 1,80 $ par million de jetons

Entrée par lot : 0,11 $ par million de jetons
Sortie par lot : 0,90 $ par million de jetons
Qwen3-235B-A22B-Instruct-2507	Entrée : 0,22 $ par million de jetons
Sortie : 0,88 $ par million de jetons

Entrée par lot : 0,11 $ par million de jetons
Sortie par lot : 0,44 $ par million de jetons
Modèles d'OpenAI
Modèle	Tarifs
gpt-oss-120b	Entrée : 0,09 $ par million de jetons
Sortie : 0,36 $ par million de jetons

Entrée par lot : 0,045 $ par million de jetons
Sortie par lot : 0,18 $ par million de jetons
gpt-oss-20b	Entrée : 0,07 $ par million de jetons
Sortie : 0,25 $ par million de jetons

Entrée par lot : 0,035 $ par million de jetons
Sortie par lot : 0,125 $ par million de jetons
Modèles Llama de Meta
Modèle	Tarifs
Llama 3.1 405B	Entrée : 5 $ / million de jetons
Sortie : 16 $ / million de jetons
Llama 3.3 70B	Entrée : 0,72 $ par million de jetons
Sortie : 0,72 $ par million de jetons

Entrée par lot : 0,36 $ par million de jetons
Sortie par lot : 0,36 $ par million de jetons
Llama 4 Scout	Entrée : 0,25 $ par million de jetons
Sortie : 0,70 $ par million de jetons

Entrée par lot : 0,125 $ par million de jetons
Sortie par lot : 0,35 $ par million de jetons
Llama 4 Maverick	Entrée : 0,35 $ par million de jetons
Sortie : 1,15 $ par million de jetons

Entrée par lot : 0,175 $ par million de jetons
Sortie par lot : 0,575 $ par million de jetons
Modèles de Mistral AI
Modèle	Tarifs
Mistral OCR (25.05)	Entrée : 0,0005 $ par million de jetons (ou 0,0005 $par page)
Sortie : 0,0005 $ par million de jetons (ou 0,0005 $par page)
Mistral Medium 3	Entrée : 0,40 $ par million de jetons
Sortie : 2 $ par million de jetons
Mistral Small 3.1 (25.03)	Entrée : 0,10 $ par million de jetons
Sortie : 0,30 $ par million de jetons
Mistral Large (24.11) (obsolète)	Entrée : 2 $ / million de jetons
Sortie : 6 $ / million de jetons
Codestral 2	Entrée : 0,30 $ par million de jetons
Sortie : 0,90 $ par million de jetons
Codestral (25.01) (obsolète)	Entrée : 0,30 $ par million de jetons
Sortie : 0,90 $ par million de jetons
Demander un devis personnalisé
Avec le paiement à l'usage de Google Cloud, vous ne payez que pour les services que vous utilisez. Contactez notre équipe commerciale pour obtenir un devis personnalisé pour votre entreprise.
Contacter le service commercial
Pourquoi choisir Google
Choisir Google Cloud
Confiance et sécurité
Cloud d'infrastructure moderne
Multicloud
Infrastructure mondiale
Clients et études de cas
Rapports d'analystes
Livres blancs
Produits et tarification
Voir tous les produits
Voir toutes les solutions
Google Cloud for Startups
Google Cloud Marketplace
Tarifs de Google Cloud
Contacter le service commercial
Support
Forums de la communauté
Support
Notes de version
État du système
Resources
GitHub
Premiers pas avec Google Cloud
Documentation Google Cloud
Exemples de code
Centre d'architecture cloud
Formations et certifications
Developer Center
Échanger
Blog
Événements
X (Twitter)
Google Cloud sur YouTube
Google Cloud Tech sur YouTube
Devenir partenaire
Google Cloud Affiliate Program
Coin Presse
À propos de Google
Règles de confidentialité
Conditions d'utilisation du site
Conditions d'utilisation de Google Cloud
Troisième décennie d'action pour le climat : rejoignez-nous
S'inscrire à la newsletter Google Cloud
S’abonner

Français
