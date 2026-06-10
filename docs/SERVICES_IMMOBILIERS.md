# Services immobiliers

La logique partagee se trouve dans `real_estate/services.py`. Elle est utilisee
par Streamlit et par les outils Mistral.

## Estimation

`predict_price` valide les caracteristiques, appelle le modele et retourne :

- le prix estime ;
- le prix estime au m2 ;
- une fourchette indicative basee sur les comparables ;
- le nombre de comparables ;
- un avertissement sur les limites du modele.

## Biens comparables

`find_comparables` recherche des annonces proches selon :

- la ville ;
- le quartier ;
- la surface ;
- les pieces et chambres ;
- le statut meuble.

Les resultats incluent le prix au m2 et l'URL source.

## Detection d'ecart

`detect_price_anomaly` compare un prix annonce au prix estime. Il classe
l'ecart comme faible, surevalue ou sous-evalue selon des seuils.

Ce resultat ne prouve ni une fraude ni une bonne affaire. Il sert uniquement
de signal pour poursuivre la verification.

## Resume du marche

`market_summary` fournit par ville ou quartier :

- nombre d'annonces ;
- prix moyen et median ;
- prix median au m2 ;
- surface moyenne ;
- prix minimal et maximal ;
- repartition des sources.

## Comparateur

`compare_properties` classe de deux a vingt biens avec :

- adequation au budget ;
- ecart au modele ;
- prix au m2 ;
- adequation aux preferences ;
- completude des informations ;
- explication du classement en francais.

## Recommandations locales

`recommend_properties` filtre les donnees collectees selon le budget, la ville,
le quartier, la surface et les chambres. Les resultats sont classes et
conservent leur URL source.

## Recherche recente

`real_estate/web_search.py` interroge DuckDuckGo avec une liste de domaines
autorises :

- Mubawab ;
- Sarouty ;
- Avito ;
- Agenz.

Les resultats sont dedupliques, leur domaine est controle et leur URL peut etre
verifiee par une requete HTTP. La date de consultation est toujours retournee.
