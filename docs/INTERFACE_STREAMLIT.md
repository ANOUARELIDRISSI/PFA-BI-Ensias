# Interface Streamlit

## Lancement

```powershell
uv run streamlit run app.py
```

L'interface est en francais et utilise des icones SVG integrees, sans emoji.
Son design reprend les conventions d'un tableau de bord React moderne :

- en-tete de produit et statut des services ;
- hero avec indicateurs reels du projet ;
- navigation compacte par fonctionnalite ;
- cartes, formulaires et tableaux harmonises ;
- mise en page responsive pour ordinateur et mobile ;
- palette, typographie et etats interactifs coherents.

## Onglets

### Estimation

Saisie de la ville, du quartier, de la surface, des pieces, chambres, salles de
bain et du statut meuble. Affiche prix, prix au m2, fourchette et comparables.

### Recommandations

Filtre les annonces locales par budget, ville, quartier, surface et chambres.
Affiche le score, les caracteristiques et le lien source.

### Comparateur

Compare plusieurs biens, calcule leur ecart au modele, leur prix au m2, leur
completude et un classement selon le budget.

### Marche

Affiche les statistiques d'une ville ou d'un quartier et un graphique des prix
medians par quartier.

### Modele ML

Lit `reports/model_metrics.json` et affiche :

- R2, MAE, RMSE et MAPE ;
- interpretation indicative de la MAPE ;
- comparaison des quatre modeles ;
- erreurs par tranche de prix ;
- donnees prioritaires a collecter.

### Collecte

Lance les scrapers Mubawab ou Sarouty directement depuis l'interface :

- choix de la vente ou de la location ;
- objectif de nombre d'annonces ;
- limite de pages pour Mubawab ;
- affichage du succes, du code de sortie et du fichier produit ;
- journal d'execution consultable.

L'interface utilise une liste stricte de scripts autorises et ne permet pas
d'executer une commande systeme libre.

### Recherche en ligne

Recherche des annonces recentes de vente ou location sur les domaines
autorises. Affiche la source, le prix detecte, l'URL, le statut de verification
et la date de consultation.

### Agent IA

Expose le chat Mistral et ses outils immobiliers. Cet onglet necessite une cle
API valide dans le `.env` de la racine.

## Donnees requises

Les onglets locaux utilisent :

```text
data/processed/real_estate_clean.csv
models/best_price_model.joblib
reports/model_metrics.json
```

Regeneration :

```powershell
uv run python -m ml.clean_data
uv run python -m ml.train
```
