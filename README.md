# Plateforme intelligente d'analyse immobiliere au Maroc

## Presentation

Ce projet a pour objectif de construire une plateforme complete de collecte, d'analyse et de prediction des donnees immobilieres au Maroc.

La plateforme permettra de :

1. Scraper les annonces publiees sur au moins quatre sites immobiliers marocains.
2. Nettoyer, normaliser et centraliser les donnees collectees.
3. Explorer et visualiser le marche immobilier marocain.
4. Entrainer un modele de Machine Learning capable de predire le prix d'un bien immobilier.
5. Utiliser un agent IA pour orchestrer la collecte, les traitements, les predictions et les interactions avec l'utilisateur.
6. Proposer, dans une phase ulterieure, une interface web entierement en francais.

## Sources de donnees

Le projet devra collecter les donnees d'au moins quatre plateformes immobilieres marocaines. La liste exacte des sites sera definie apres verification de leurs conditions d'utilisation, de leur fichier `robots.txt` et de leurs contraintes techniques.

Les informations recherchees incluront notamment :

- le prix ;
- la ville et le quartier ;
- le type de bien ;
- la superficie ;
- le nombre de pieces et de chambres ;
- les equipements et caracteristiques ;
- le type de transaction, vente ou location ;
- la date de publication ;
- l'URL et la source de l'annonce.

La collecte devra respecter les conditions d'utilisation des plateformes, limiter la frequence des requetes et eviter de recueillir des donnees personnelles inutiles.

## Machine Learning

Le pipeline de Machine Learning couvrira :

- l'analyse exploratoire des donnees ;
- le traitement des valeurs manquantes et des doublons ;
- la detection des valeurs aberrantes ;
- la creation et la selection des variables ;
- l'entrainement de plusieurs modeles ;
- la comparaison des performances ;
- l'evaluation avec des metriques adaptees, comme `MAE`, `RMSE` et `R2` ;
- la sauvegarde et le versionnement du meilleur modele ;
- l'exposition du modele pour effectuer des predictions.

## Agent IA

L'agent sera adapte a partir du depot suivant :

[AI-Agent](AI-Agent), adapte depuis
[ANOUARELIDRISSI/3sso-AI-Agent](https://github.com/ANOUARELIDRISSI/3sso-AI-Agent.git)

Il sera modifie pour repondre aux besoins du domaine immobilier marocain. Il orchestrera notamment :

- le lancement et le suivi des scrapers ;
- la validation et la preparation des donnees ;
- l'execution du pipeline de prediction ;
- l'interrogation des resultats ;
- la generation de syntheses et d'explications en francais.

Le modele de langage utilise par l'agent sera **Mistral**.

## Environnement et outils

- **Langage principal :** Python
- **Gestion du projet et de l'environnement virtuel :** [`uv`](https://docs.astral.sh/uv/)
- **LLM :** Mistral
- **Collecte :** outils Python de scraping, a definir selon les sites
- **Traitement des donnees :** Pandas ou Polars
- **Machine Learning :** scikit-learn et autres bibliotheques selon les besoins
- **Interface web :** technologie a definir dans une phase ulterieure
- **Langue de l'application :** francais

## Organisation cible

Chaque responsabilite disposera de son propre dossier afin de conserver une architecture claire, testable et evolutive.

```text
PFA-BI-Ensias/
|-- agent/                 # Agent IA et orchestration
|-- api/                   # API de prediction et services metier
|-- config/                # Configuration de l'application
|-- data/
|   |-- raw/               # Donnees brutes collectees
|   |-- interim/           # Donnees intermediaires
|   `-- processed/         # Donnees pretes pour l'analyse et le ML
|-- docs/                  # Documentation technique et fonctionnelle
|-- frontend/              # Future interface web en francais
|-- models/                # Modeles entraines et metadonnees
|-- notebooks/             # Exploration et experimentation
|-- scraping/
|   |-- sources/           # Un module independant par site
|   |-- pipelines/         # Nettoyage et normalisation
|   `-- schemas/           # Schemas communs des annonces
|-- src/                   # Code partage et logique metier
|-- tests/                 # Tests unitaires et d'integration
|-- pyproject.toml         # Dependances et configuration Python
|-- uv.lock                # Verrouillage des dependances
`-- README.md
```

## Principes du projet

- Architecture modulaire avec un dossier par composant.
- Schema de donnees commun pour toutes les sources.
- Scraper independant et testable pour chaque site.
- Separation entre collecte, traitement, Machine Learning, agent et interface.
- Configuration centralisee, sans secrets dans le depot Git.
- Journalisation des traitements et gestion claire des erreurs.
- Tests automatises pour les composants critiques.
- Documentation en francais maintenue avec le projet.

## Feuille de route

1. Initialiser le projet Python avec `uv`.
2. Definir le schema commun des annonces immobilieres.
3. Selectionner et analyser au moins quatre sites marocains.
4. Developper et tester un scraper par source.
5. Construire le pipeline de nettoyage et de stockage.
6. Realiser l'analyse exploratoire.
7. Entrainer et evaluer les modeles de prediction.
8. Adapter le module `AI-Agent` et integrer Mistral.
9. Exposer les fonctionnalites par une API.
10. Developper l'interface web en francais.

## Statut

Le projet dispose maintenant de scrapers de vente et de location, d'un
pipeline ML de prix de vente, de services immobiliers, d'un agent Mistral et
d'une interface Streamlit en francais.

## Guides de demarrage

- [Demarrage des scrapers](DEMARRAGE_SCRAPERS.md)
- [Demarrage de l'agent IA](DEMARRAGE_AGENT.md)
- [Documentation complete](docs/README.md)

## Interface Streamlit

Apres `uv sync`, lancer depuis la racine :

```powershell
uv run streamlit run app.py
```

L'interface en francais propose l'estimation, les recommandations, le
comparateur, les statistiques du marche, la recherche en ligne et le chat avec
l'agent Mistral.

Documentation : [Recherche immobiliere en ligne](RECHERCHE_EN_LIGNE.md).

Le projet utilise un seul fichier `.env`, place a la racine. Les modules de
`AI-Agent/`, `scraping/`, `ml/` et l'interface partagent cette configuration.
