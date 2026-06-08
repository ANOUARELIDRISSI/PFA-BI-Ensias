# Explication des scrapers

Ce dossier contient les scripts de collecte des donnees immobilieres.

Objectif actuel :

- collecter des annonces d'appartements a vendre au Maroc ;
- produire un fichier CSV et un fichier JSON par source ;
- obtenir au moins 150 annonces uniques par site ;
- stocker les donnees dans `data/raw/`.

Les fichiers generes sont ignores par Git afin d'eviter de pousser des donnees
brutes volumineuses ou dupliquees.

## Structure

```text
scraping/
|-- scrape_mubawab.py    # Collecte des annonces Mubawab
|-- scrape_sarouty.py    # Collecte des annonces Sarouty
|-- __init__.py
`-- README.md
```

## Regles communes

Les deux scripts suivent les memes principes :

- utiliser un `User-Agent` explicite pour identifier le projet ;
- ajouter un delai entre les requetes quand plusieurs pages sont demandees ;
- dedupliquer les annonces avec leur URL ou leur identifiant source ;
- verifier que le nombre minimum d'annonces est atteint ;
- enregistrer les resultats en CSV et JSON ;
- utiliser `--overwrite` pour eviter les doublons de fichiers dans `data/raw/`.

Commande recommandee depuis la racine du projet :

```powershell
uv run python scraping/scrape_mubawab.py --overwrite
uv run python scraping/scrape_sarouty.py --overwrite
```

## Scraper Mubawab

Fichier :

```text
scraping/scrape_mubawab.py
```

Source cible :

```text
https://www.mubawab.ma/en/sc/apartments-for-sale
```

### Methode

Mubawab expose les annonces directement dans le HTML de la page de resultats.
Le script utilise donc :

- `requests` pour telecharger la page ;
- `BeautifulSoup` pour analyser le HTML ;
- des selecteurs CSS pour trouver les blocs d'annonces ;
- des expressions regulieres pour extraire les valeurs numeriques.

### Pagination

La premiere page utilise l'URL principale :

```text
https://www.mubawab.ma/en/sc/apartments-for-sale
```

Les pages suivantes utilisent le format :

```text
https://www.mubawab.ma/en/sc/apartments-for-sale:p:2
https://www.mubawab.ma/en/sc/apartments-for-sale:p:3
```

La fonction `page_url()` construit ces URLs automatiquement.

### Champs extraits

Le scraper Mubawab extrait :

- `source`
- `scraped_at`
- `page`
- `title`
- `price`
- `price_mad`
- `location`
- `surface_m2`
- `rooms`
- `bedrooms`
- `bathrooms`
- `description`
- `url`

### Deduplification

Les annonces sont dedupliquees avec leur champ `url`.

Si plusieurs pages contiennent la meme annonce, une seule ligne est conservee.

### Commandes utiles

Collecte standard, au moins 150 annonces :

```powershell
uv run python scraping/scrape_mubawab.py --overwrite
```

Collecte plus grande :

```powershell
uv run python scraping/scrape_mubawab.py --min-listings 250 --max-pages 15 --delay 2 --overwrite
```

### Sortie

Avec `--overwrite`, les fichiers sont :

```text
data/raw/mubawab_apartments_sale.csv
data/raw/mubawab_apartments_sale.json
```

Sans `--overwrite`, les fichiers ont un horodatage :

```text
data/raw/mubawab_apartments_sale_YYYYMMDD_HHMMSS.csv
data/raw/mubawab_apartments_sale_YYYYMMDD_HHMMSS.json
```

## Scraper Sarouty

Fichier :

```text
scraping/scrape_sarouty.py
```

Source cible :

```text
https://www.sarouty.ma/acheter/appartements-a-vendre/
```

Endpoint utilise par le script :

```text
https://b2c-be-prod.api.sarouty.ma/api/properties
```

### Methode

Sarouty charge ses annonces depuis une API JSON publique. Le script utilise
donc directement cette API au lieu de parser le HTML.

C'est plus stable pour ce site, car les donnees sont deja structurees.

Le script utilise :

- `requests` pour interroger l'API ;
- les parametres de filtre pour cibler les appartements a vendre ;
- une fonction `normalize()` pour transformer la reponse API en schema commun ;
- `csv` et `json` pour sauvegarder les resultats.

### Filtres API

Les parametres utilises sont :

```text
property_category_id=1
property_property_housing_id=1
page=<numero_de_page>
limit=<taille_de_page>
```

Interpretation :

- `property_category_id=1` cible les biens a acheter ;
- `property_property_housing_id=1` cible les appartements ;
- `page` controle la pagination ;
- `limit` controle le nombre de resultats par page.

### Pagination

Le script demande les pages API une par une jusqu'a atteindre le nombre minimum
d'annonces.

Par defaut :

- `page_size = 100`
- `min_listings = 150`

Donc deux pages suffisent generalement pour produire environ 200 annonces.

### Champs extraits

Le scraper Sarouty extrait :

- `source`
- `source_id`
- `scraped_at`
- `page`
- `title`
- `price`
- `price_mad`
- `location`
- `property_type`
- `surface_m2`
- `rooms`
- `bedrooms`
- `bathrooms`
- `furnished`
- `published_at`
- `url`

### Deduplification

Les annonces sont dedupliquees avec `source_id`, qui correspond a
`property_id` dans l'API Sarouty.

### Respect du site

Le fichier `robots.txt` de Sarouty indique un `Crawl-delay` de 10 secondes.
Le script utilise donc `--delay 10` par defaut.

### Commandes utiles

Collecte standard, au moins 150 annonces :

```powershell
uv run python scraping/scrape_sarouty.py --overwrite
```

Collecte plus grande :

```powershell
uv run python scraping/scrape_sarouty.py --min-listings 300 --delay 10 --overwrite
```

### Sortie

Avec `--overwrite`, les fichiers sont :

```text
data/raw/sarouty_apartments_sale.csv
data/raw/sarouty_apartments_sale.json
```

Sans `--overwrite`, les fichiers ont un horodatage :

```text
data/raw/sarouty_apartments_sale_YYYYMMDD_HHMMSS.csv
data/raw/sarouty_apartments_sale_YYYYMMDD_HHMMSS.json
```

## Verification des resultats

Apres execution, verifier le nombre de lignes avec PowerShell :

```powershell
(Import-Csv data/raw/mubawab_apartments_sale.csv).Count
(Import-Csv data/raw/sarouty_apartments_sale.csv).Count
```

Verifier les premieres lignes :

```powershell
Import-Csv data/raw/mubawab_apartments_sale.csv | Select-Object -First 3
Import-Csv data/raw/sarouty_apartments_sale.csv | Select-Object -First 3
```

## Evolution prevue

Les prochains scrapers devront suivre le meme modele :

1. creer un fichier `scrape_nomdusite.py` ;
2. respecter les regles du site cible ;
3. produire un schema proche des champs existants ;
4. dedupliquer les annonces ;
5. sauvegarder dans `data/raw/` ;
6. documenter la methode dans ce fichier.
