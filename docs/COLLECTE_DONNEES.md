# Collecte et schema des donnees

## Sources disponibles

Deux collecteurs sont implementes :

- Mubawab, par lecture des pages publiques ;
- Sarouty, par lecture de son endpoint public utilise par le site.

Chaque collecteur prend en charge les ventes et les locations.

## Commandes

Ventes :

```powershell
uv run python scraping/scrape_mubawab.py --transaction sale --overwrite
uv run python scraping/scrape_sarouty.py --transaction sale --overwrite
```

Locations :

```powershell
uv run python scraping/scrape_mubawab.py --transaction rent --overwrite
uv run python scraping/scrape_sarouty.py --transaction rent --overwrite
```

Le minimum par defaut est de 150 annonces uniques. Les essais reels les plus
recents ont produit 164 locations Mubawab et 200 locations Sarouty.

## Options

Mubawab :

```text
--transaction sale|rent
--min-listings N
--max-pages N
--delay SECONDES
--overwrite
```

Sarouty :

```text
--transaction sale|rent
--min-listings N
--delay SECONDES
--overwrite
```

`--overwrite` utilise un nom stable et evite la multiplication des exports
dates. Les annonces sont dedupliquees avec leur URL ou leur identifiant source.

## Schema commun

Le schema est defini dans `scraping/schema.py`. Il contient 31 champs :

- source, identifiant, URL et dates ;
- transaction et type de bien ;
- titre, description et prix ;
- ville, quartier, adresse textuelle et coordonnees ;
- surface, pieces, chambres et salles de bain ;
- etage et nombre total d'etages ;
- etat et annee de construction ;
- meuble, ascenseur, parking, terrasse, balcon et securite.

Une valeur reste vide lorsque la source ne publie pas l'information. Le
collecteur ne doit pas inventer une caracteristique.

## Qualite et limites

- Les selecteurs HTML peuvent changer.
- Les donnees sont des prix annonces, pas des prix de transaction notariale.
- Une annonce peut etre retiree ou modifiee apres la collecte.
- Les conditions d'utilisation et `robots.txt` doivent etre verifies avant
  chaque nouvelle source.
- Aucun CAPTCHA ou mecanisme de protection ne doit etre contourne.

## Ajouter une source

1. Verifier les regles du site et identifier une page ou API publique stable.
2. Creer `scraping/scrape_source.py`.
3. Normaliser chaque resultat avec `scraping.schema.Listing`.
4. Dedupliquer avec `source_id` ou `url`.
5. Ajouter des tests de normalisation.
6. Effectuer un essai reel d'au moins 150 annonces avant de declarer la source
   fonctionnelle.

Agenz et Avito sont des candidats, mais ne sont pas encore implementes.
