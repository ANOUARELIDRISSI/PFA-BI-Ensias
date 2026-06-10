# Architecture et configuration

## Organisation

```text
PFA-BI-Ensias/
|-- AI-Agent/       # Agent Mistral et outils
|-- data/           # Donnees brutes et nettoyees
|-- docs/           # Documentation fonctionnelle et technique
|-- ml/             # Nettoyage, entrainement et prediction
|-- models/         # Modele genere localement
|-- real_estate/    # Services metier et recherche en ligne
|-- reports/        # Metriques generees localement
|-- scraping/       # Collecteurs et schema commun
|-- tests/          # Tests automatises
|-- app.py          # Interface Streamlit
|-- config.py       # Chargement de la configuration
|-- pyproject.toml  # Dependances du projet
`-- uv.lock         # Versions verrouillees
```

## Environnement Python unique

Toutes les dependances sont installees dans le `.venv` de la racine :

```powershell
uv sync
```

Les commandes doivent etre lancees avec `uv run`. Aucun environnement Python
separe n'est necessaire dans `AI-Agent/`, `ml/` ou `scraping/`.

## Fichier `.env` unique

Le seul fichier d'environnement accepte est :

```text
PFA-BI-Ensias/.env
```

Creation :

```powershell
Copy-Item .env.example .env
```

Contenu :

```env
MISTRAL_API_KEY=your_real_mistral_api_key
```

`config.py` charge explicitement ce fichier depuis la racine. Il ne depend
donc pas du dossier depuis lequel un module est execute.

Le fichier `.env` est ignore par Git. Il ne faut jamais placer une cle reelle
dans `.env.example`, un document ou un commit.

## Donnees et artefacts locaux

Les donnees brutes, donnees traitees, modeles, rapports et secrets sont
ignores par Git. Ils sont regeneres avec les commandes documentees dans les
pages de collecte et de Machine Learning.
