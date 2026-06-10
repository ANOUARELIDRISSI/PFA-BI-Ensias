# Pipeline Machine Learning

## Objectif actuel

Le modele actuel estime le prix de vente d'un appartement en dirhams. Il ne
doit pas etre utilise pour predire un loyer mensuel.

## Nettoyage

Commande :

```powershell
uv run python -m ml.clean_data
```

Le pipeline :

- fusionne les CSV de vente ;
- harmonise les colonnes ;
- deduplique les annonces ;
- convertit les variables numeriques ;
- extrait la ville et le quartier si necessaire ;
- retire les lignes sans prix, surface ou ville ;
- applique des bornes de prix, surface et prix au m2 ;
- limite les valeurs aberrantes avec une regle IQR ;
- complete certaines valeurs manquantes par la mediane.

Sortie :

```text
data/processed/real_estate_clean.csv
```

## Entrainement

```powershell
uv run python -m ml.train
```

Modeles compares :

- Ridge ;
- Random Forest ;
- Extra Trees ;
- Gradient Boosting.

La cible est transformee avec `log1p`. Les variables numeriques sont imputees
et standardisees. Les variables categorielles utilisent un encodage one-hot.
Le meilleur modele est choisi avec la MAE moyenne en validation croisee.

## Metriques actuelles

Les valeurs courantes sont enregistrees dans `reports/model_metrics.json` et
affichees dans les onglets `Modele ML` et `Insights`. Elles changent apres
chaque nouvelle collecte et chaque entrainement.

Le dernier cycle reel verifie a nettoye 402 ventes et a selectionne Extra Trees
avec un R2 de 0,6499. Les autres metriques doivent etre lues directement dans
le rapport, car une amelioration du R2 peut coexister avec une MAPE plus elevee.

Ces valeurs sont mesurees sur le jeu de test. Elles ne doivent pas etre
remplacees par les valeurs d'une maquette visuelle.

## Artefacts

```text
models/best_price_model.joblib
reports/model_metrics.json
```

Le rapport contient les metriques de chaque modele, les erreurs les plus
importantes et les erreurs par tranche de prix.

## Prediction en ligne de commande

```powershell
uv run python -m ml.predict `
  --surface 100 `
  --rooms 3 `
  --bedrooms 2 `
  --bathrooms 2 `
  --city Casablanca `
  --neighborhood Gauthier `
  --furnished NO
```

## Limites

- Le volume de 317 lignes est faible.
- Les villes et quartiers ne sont pas encore equilibres.
- Beaucoup de sources ne publient pas l'etat, l'etage ou l'annee.
- Une MAPE globale ne constitue pas un intervalle de confiance pour chaque bien.
- Les prix bas disposent actuellement de peu d'exemples et produisent des
  erreurs relatives elevees.
