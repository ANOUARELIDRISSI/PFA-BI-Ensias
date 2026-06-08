# Pipeline Machine Learning

Ce dossier contient le pipeline de nettoyage, d'entrainement et de prediction
des prix de vente des appartements au Maroc.

## Etapes

1. Charger les fichiers CSV de `data/raw/`.
2. Uniformiser les schemas Mubawab et Sarouty.
3. Supprimer les doublons, lignes invalides et valeurs extremes.
4. Extraire la ville et le quartier depuis le champ `location`.
5. Imputer les valeurs manquantes.
6. Comparer plusieurs modeles avec une validation croisee a cinq plis.
7. Selectionner le modele avec la plus faible MAE moyenne.
8. Evaluer le modele gagnant sur un jeu de test separe.
9. Sauvegarder le pipeline complet avec `joblib`.

## Nettoyage

```powershell
uv run python -m ml.clean_data
```

Sortie :

```text
data/processed/real_estate_clean.csv
```

Le nettoyage conserve les appartements avec :

- un prix entre 100 000 et 20 000 000 MAD ;
- une surface entre 20 et 500 m2 ;
- un prix au m2 entre 2 000 et 80 000 MAD ;
- une ville, une surface et un prix disponibles.

Un filtre IQR est ensuite applique au prix et a la surface.

## Entrainement

```powershell
uv run python -m ml.train
```

Modeles compares :

- Ridge ;
- Random Forest ;
- Extra Trees ;
- Gradient Boosting.

Le prix est transforme avec `log1p` pendant l'entrainement. Les variables
numeriques sont standardisees et les variables categorielles sont encodees avec
`OneHotEncoder`.

Sorties :

```text
models/best_price_model.joblib
reports/model_metrics.json
```

## Prediction

```powershell
uv run python -m ml.predict `
  --surface 100 `
  --rooms 3 `
  --bedrooms 2 `
  --bathrooms 2 `
  --city Casablanca `
  --neighborhood Maarif `
  --furnished NO
```

## Resultat actuel

Le pipeline a nettoye 317 annonces sur 364 annonces brutes.

Le meilleur modele est `ExtraTreesRegressor` :

- MAE moyenne en validation croisee : 497 528 MAD ;
- MAE sur le jeu de test : 399 325 MAD ;
- RMSE sur le jeu de test : 578 580 MAD ;
- R2 sur le jeu de test : 0,61.

Ces performances constituent une base de travail, pas encore une estimation
professionnelle. Le modele doit etre ameliore avec davantage de donnees, plus de
villes, les coordonnees geographiques, l'etat du bien, l'etage, l'ascenseur, le
parking, l'age du logement et la proximite des services.
