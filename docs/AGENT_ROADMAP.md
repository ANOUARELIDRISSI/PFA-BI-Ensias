# Roadmap du super agent immobilier

L'agent ne doit pas seulement predire un prix. Il doit accompagner une personne
dans tout son parcours immobilier au Maroc, tout en distinguant clairement les
donnees observees, les estimations du modele et les conseils generaux.

## 1. Estimation du prix

- demander la ville, le quartier, la surface et les caracteristiques ;
- appeler le modele de prediction ;
- afficher une fourchette, pas seulement une valeur unique ;
- expliquer les principaux facteurs de l'estimation ;
- signaler lorsque le quartier est absent ou peu represente dans les donnees.

## 2. Recherche de biens a louer ou a acheter

- transformer la demande utilisateur en criteres structures ;
- chercher des annonces recentes avec DuckDuckGo ;
- cibler Mubawab, Sarouty, Avito, Agenz et d'autres sources autorisees ;
- retourner le titre, le prix, la ville, la surface, la source et l'URL ;
- supprimer les doublons entre les plateformes ;
- verifier la date et l'accessibilite de chaque annonce avant recommandation.

Exemple de recherche :

```text
site:mubawab.ma appartement location Agdal Rabat 2 chambres
```

DuckDuckGo sert a decouvrir les pages. Les donnees importantes doivent ensuite
etre confirmees sur la page source.

## 3. Recommandation de quartiers

L'agent doit demander :

- le budget mensuel ou d'achat ;
- la ville ou les villes possibles ;
- le lieu de travail ou d'etudes ;
- le nombre de chambres ;
- meuble ou non meuble ;
- voiture ou transports publics ;
- calme, vie nocturne, plage, ecoles ou commerces ;
- location longue duree ou courte duree.

Il peut ensuite classer les quartiers selon les besoins. Des quartiers souvent
mentionnes dans les guides recents incluent Maarif a Casablanca, Agdal a Rabat,
Gueliz a Marrakech et Malabata a Tanger. Ce ne sont pas des recommandations
universelles : le classement doit dependre du budget et des priorites.

## 4. Comparateur d'annonces

- comparer le prix total et le prix au m2 ;
- afficher l'ecart avec l'estimation du modele ;
- detecter une annonce potentiellement surevaluee ou anormalement basse ;
- comparer surface, chambres, equipements et emplacement ;
- produire un tableau de classement.

## 5. Budget et financement

- calculer une mensualite indicative ;
- estimer l'apport et les frais annexes ;
- comparer location et achat sur une duree choisie ;
- calculer le taux d'effort ;
- ne jamais presenter une simulation comme une offre bancaire.

## 6. Investissement locatif

- rendement brut et net ;
- cash-flow mensuel ;
- taux d'occupation necessaire ;
- comparaison location longue et courte duree ;
- scenarios optimiste, central et prudent ;
- estimation des charges, vacances locatives et frais de gestion.

## 7. Analyse de quartier

- transports et temps de trajet ;
- commerces, ecoles, hopitaux et espaces verts ;
- bruit et type d'environnement ;
- tendances de prix dans les donnees collectees ;
- nouvelles annonces et evolution de l'offre.

Les informations locales doivent etre datees et accompagnees de sources.

## 8. Alertes personnalisees

- memoriser les criteres de recherche ;
- detecter les nouvelles annonces ;
- notifier une baisse de prix ;
- alerter lorsqu'un bien passe sous un prix au m2 defini ;
- eviter d'envoyer plusieurs fois la meme annonce.

## 9. Controle des risques

- reperer les prix anormalement bas ;
- signaler les descriptions ou photos incoherentes ;
- rappeler de visiter le bien ;
- recommander de verifier le proprietaire, le mandat et les documents ;
- ne jamais conseiller de verser un acompte avant verification ;
- masquer les numeros, e-mails et donnees personnelles dans les journaux.

## 10. Architecture d'outils recommandee

L'agent Mistral devrait disposer d'outils limites et explicites :

- `predict_price` : appeler le modele ML ;
- `search_properties` : recherche DuckDuckGo avec domaines autorises ;
- `read_listing` : extraire une annonce precise ;
- `compare_properties` : classer plusieurs biens ;
- `recommend_neighborhoods` : appliquer les preferences utilisateur ;
- `calculate_mortgage` : simulation financiere ;
- `calculate_rental_yield` : rentabilite locative ;
- `save_search` : enregistrer des criteres ;
- `get_market_summary` : statistiques sur les donnees collectees.

Chaque resultat de recherche web doit contenir son URL et sa date de
consultation. Chaque prediction doit afficher les limites du modele.

## Priorites

1. Exposer le modele avec une fonction Python stable.
2. Ajouter la recherche DuckDuckGo avec filtrage des domaines.
3. Construire le comparateur d'annonces.
4. Ajouter les recommandations de quartiers selon le budget.
5. Ajouter les calculs de financement et de rendement.
6. Ajouter les alertes et la memoire utilisateur.
7. Connecter l'ensemble a l'interface web en francais.
