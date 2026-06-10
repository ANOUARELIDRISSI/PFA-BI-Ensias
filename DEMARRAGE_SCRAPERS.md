# Demarrage et test des scrapers

Ce guide explique comment installer et lancer les scrapers apres un nouveau
clonage du depot.

Le projet utilise uniquement `PFA-BI-Ensias/.env`. Ne creez pas de fichier
`.env` dans `AI-Agent/`, `scraping/` ou `ml/`.

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

## 3. Installer toutes les dependances

Depuis la racine du projet :

```powershell
uv sync
```

Cette commande cree un seul dossier `.venv` a la racine et installe les
dependances des scrapers, du Machine Learning, des tests et de l'agent.

Il n'est pas necessaire d'activer manuellement l'environnement. `uv` retrouve
automatiquement le projet racine depuis les sous-dossiers.

## 4. Lancer le scraper Mubawab

Le scraper collecte par defaut au moins 150 annonces uniques d'appartements a vendre.

```powershell
uv run python scraping/scrape_mubawab.py --transaction sale --overwrite
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
uv run python scraping/scrape_sarouty.py --transaction sale --overwrite
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

Pour les locations :

```powershell
uv run python scraping/scrape_mubawab.py --transaction rent --overwrite
uv run python scraping/scrape_sarouty.py --transaction rent --overwrite
```

Les memes scripts peuvent etre lances depuis le dossier `scraping` :

```powershell
cd scraping
uv run python scrape_mubawab.py --overwrite
uv run python scrape_sarouty.py --overwrite
```

Ces commandes utilisent toujours le `.venv` unique situe a la racine.

## 7. Structure utile

```text
PFA-BI-Ensias/
|-- .venv/               # Environnement Python unique
|-- AI-Agent/
|-- data/
|   `-- raw/             # Donnees collectees
|-- ml/
|-- DEMARRAGE_SCRAPERS.md
|-- scraping/
|   |-- scrape_mubawab.py
|   `-- scrape_sarouty.py
|-- pyproject.toml
|-- uv.lock
`-- README.md
```

## 8. Mise a jour du projet

Pour recuperer les dernieres modifications :

```powershell
git pull
uv sync
```

## 9. Problemes courants

Verifier que les commandes sont executees depuis la racine `PFA-BI-Ensias`.

Si `uv` n'est pas reconnu, fermer puis rouvrir le terminal apres son installation.

Si un site refuse une requete, ne pas reduire agressivement le delai. Verifier d'abord sa disponibilite et ses regles de collecte.
