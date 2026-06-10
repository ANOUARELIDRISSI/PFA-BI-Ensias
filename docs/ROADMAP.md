# Fonctionnalites suivantes

Cette page reprend `project.md` sans exposer ce fichier prive et ignore. Les
priorites tiennent compte de l'etat reel du code.

## Priorite 1 : modele de loyer

Les locations Mubawab et Sarouty sont maintenant collectees. La prochaine
etape logique est :

1. separer clairement ventes et locations dans le nettoyage ;
2. definir des bornes de loyer mensuel ;
3. entrainer et comparer les modeles de loyer ;
4. sauvegarder un pipeline distinct ;
5. ajouter une estimation de loyer dans les services, l'agent et Streamlit.

## Priorite 2 : calculs financiers

Avec les modeles de vente et de loyer :

- rendement locatif brut ;
- rendement net avec charges configurables ;
- cash-flow mensuel ;
- simulation de credit ;
- comparaison achat contre location ;
- scenarios prudent, central et optimiste.

Les hypotheses doivent toujours etre affichees.

## Priorite 3 : historique et alertes

- conserver un identifiant stable par annonce ;
- enregistrer chaque observation avec sa date ;
- detecter les nouvelles annonces ;
- detecter les baisses de prix ;
- sauvegarder les recherches ;
- eviter les notifications en double.

Cette fonctionnalite necessite une base de donnees, par exemple PostgreSQL.

## Priorite 4 : carte et quartiers

- geocoder les annonces sans coordonnees ;
- afficher une carte avec filtres ;
- calculer les prix par zone ;
- recommander des quartiers selon le budget et les preferences ;
- integrer les temps de trajet vers un lieu de travail ou d'etudes.

## Priorite 5 : nouvelles sources

Verifier puis implementer deux sources supplementaires, par exemple Agenz et
Avito. Chaque source doit respecter le schema commun et passer un test reel
d'au moins 150 annonces.

## Priorite 6 : qualite du modele

- atteindre au moins 5 000 annonces propres ;
- equilibrer les villes et tranches de prix ;
- collecter l'etat, l'etage, l'annee et les equipements ;
- mesurer les erreurs par ville et quartier ;
- ajouter un intervalle de prediction ;
- surveiller la derive des donnees et des performances.

## Priorite 7 : API et production

- exposer les services avec FastAPI ;
- ajouter authentification et limitation de debit ;
- journaliser les appels ;
- versionner les modeles ;
- automatiser les tests et deploiements ;
- planifier la collecte sans donner a l'agent des permissions illimitees.

## Ordre recommande

1. Modele de loyer.
2. Rendement et simulation financiere.
3. Base historique et alertes.
4. Carte et recommandation de quartiers.
5. Deux nouvelles sources.
6. API FastAPI et preparation de production.
