# Guide de demarrage

Ce guide explique comment installer et lancer le projet apres un nouveau clonage du depot.

## 1. Prerequis

Installer les outils suivants :

- Git
- Python 3.12 ou une version plus recente
- `uv`

Pour installer `uv` avec `pip` :

```powershell
pip install uv
```

Alternative officielle sous Windows avec PowerShell :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verifier les installations :

```powershell
git --version
python --version
uv --version
```

## 2. Cloner le projet

```powershell
git clone https://github.com/ANOUARELIDRISSI/PFA-BI-Ensias.git
cd PFA-BI-Ensias
```

Le dossier `AI-Agent` est configure comme un sous-module Git :

```powershell
git submodule update --init --recursive
```

## 3. Installer les dependances

Depuis la racine du projet :

```powershell
uv sync
```

Cette commande cree automatiquement le dossier `.venv` et installe les dependances declarees dans `pyproject.toml`.

Il n'est pas necessaire d'activer manuellement l'environnement pour utiliser `uv run`.

## 4. Lancer le scraper Mubawab

Le scraper collecte par defaut au moins 150 annonces uniques d'appartements a vendre.

```powershell
uv run python scraping/scrape_mubawab.py --overwrite
```

Les fichiers produits sont :

```text
data/raw/mubawab_apartments_sale.csv
data/raw/mubawab_apartments_sale.json
```

Options utiles :

```powershell
uv run python scraping/scrape_mubawab.py --min-listings 200 --max-pages 15 --delay 2 --overwrite
```

- `--min-listings` : nombre minimum d'annonces uniques ;
- `--max-pages` : nombre maximal de pages a parcourir ;
- `--delay` : pause en secondes entre les requetes ;
- `--overwrite` : remplace les fichiers precedents au lieu de creer des doublons dates.

## 5. Lancer le scraper Sarouty

```powershell
uv run python scraping/scrape_sarouty.py --overwrite
```

Les fichiers produits sont :

```text
data/raw/sarouty_apartments_sale.csv
data/raw/sarouty_apartments_sale.json
```

Pour modifier le nombre minimum d'annonces :

```powershell
uv run python scraping/scrape_sarouty.py --min-listings 200 --delay 10 --overwrite
```

Le delai de 10 secondes respecte la directive publiee dans le fichier `robots.txt` de Sarouty.

## 6. Lancer tous les scrapers

Depuis la racine du projet :

```powershell
uv run python scraping/scrape_mubawab.py --overwrite
uv run python scraping/scrape_sarouty.py --overwrite
```

Chaque source produit son propre fichier CSV et JSON dans `data/raw`.

## 7. Utiliser l'agent IA

L'agent possede actuellement son propre environnement Python.

```powershell
cd AI-Agent
uv sync
```

Creer ensuite le fichier local `.env` a partir de l'exemple :

```powershell
Copy-Item .env.example .env
```

Ajouter les cles API necessaires dans `.env`, puis lancer l'agent :

```powershell
uv run python main.py
```

Ne jamais enregistrer le fichier `.env` ou les cles API dans Git.

## 8. Nettoyer les donnees et entrainer le modele

Depuis la racine du projet :

```powershell
uv sync
uv run python -m ml.clean_data
uv run python -m ml.train
```

Tester une prediction :

```powershell
uv run python -m ml.predict --surface 100 --rooms 3 --bedrooms 2 --bathrooms 2 --city Casablanca --neighborhood Maarif --furnished NO
```

## 9. Structure utile

```text
PFA-BI-Ensias/
|-- AI-Agent/            # Agent IA
|-- data/
|   `-- raw/             # Donnees collectees
|-- DEMARRAGE.md         # Ce guide
|-- ml/                  # Nettoyage, entrainement et prediction
|-- models/              # Modele entraine
|-- reports/             # Metriques d'evaluation
|-- scraping/
|   |-- scrape_mubawab.py
|   `-- scrape_sarouty.py
|-- pyproject.toml
|-- uv.lock
`-- README.md
```

## 10. Mise a jour du projet

Pour recuperer les dernieres modifications :

```powershell
git pull
uv sync
```

Si les dependances de l'agent ont egalement change :

```powershell
cd AI-Agent
uv sync
```

## 11. Problemes courants

Verifier que les commandes sont executees depuis la racine `PFA-BI-Ensias`.

Si `uv` n'est pas reconnu, fermer puis rouvrir le terminal apres son installation.

Si un site refuse une requete, ne pas reduire agressivement le delai. Verifier d'abord sa disponibilite et ses regles de collecte.
