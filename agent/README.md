# Prototype CrewAI

Le fichier `legacy_crewai_agent.py` provient du script ajoute initialement a la
racine du depot.

Il ne s'agit pas d'un scraper de donnees structurees. Il definit plusieurs
agents CrewAI qui utilisent des outils de recherche et de lecture de pages web.

Les scrapers qui produisent les fichiers CSV et JSON se trouvent dans :

- `scraping/scrape_mubawab.py`
- `scraping/scrape_sarouty.py`

Ce prototype depend encore de `crewai`, `crewai-tools`, `langchain-openai`,
`IPython` et d'un module `utils` qui n'est pas present dans le script original.
Il devra etre adapte a Mistral et integre a `3sso-AI-Agent` avant son execution.
