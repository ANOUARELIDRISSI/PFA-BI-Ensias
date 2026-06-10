# Tests et verification

## Suite automatisee

```powershell
uv run pytest -q
```

La suite actuelle contient 17 tests couvrant :

- services immobiliers ;
- outils de l'agent ;
- recherche en ligne et filtrage des domaines ;
- chargement du `.env` racine ;
- schema commun des annonces ;
- normalisation des lieux Mubawab ;
- rendu de l'application Streamlit.

## Verification syntaxique

```powershell
uv run python -m py_compile `
  config.py `
  app.py `
  scraping/schema.py `
  scraping/scrape_mubawab.py `
  scraping/scrape_sarouty.py `
  ml/clean_data.py `
  ml/train.py `
  AI-Agent/agent.py
```

## Tests reels deja effectues

- collecte de 164 locations uniques sur Mubawab ;
- collecte de 200 locations uniques sur Sarouty ;
- entrainement du modele sur 317 ventes nettoyees ;
- requete reelle a Mistral avec le `.env` racine ;
- execution reelle du scraper Sarouty par le runner et par un appel Mistral ;
- nettoyage, entrainement et lecture des metriques via le runner ML ;
- lecture reelle des nouvelles metriques par un appel Mistral ;
- recherche DuckDuckGo reelle vers Mubawab et Sarouty ;
- rendu des sept onglets Streamlit sans exception.

## Difference entre tests automatises et tests reels

Les tests automatises isolent les appels reseau pour rester rapides et
reproductibles. Les tests reels doivent etre executes avant une livraison qui
modifie un scraper, une API externe ou l'integration Mistral.

Les fichiers generes et le `.env` restent ignores par Git.
