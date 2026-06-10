# Documentation du projet

Ce dossier decrit les fonctionnalites reellement disponibles dans le projet.
Les fonctions futures sont separees des fonctions implementees afin de ne pas
presenter une idee comme un resultat deja livre.

## Fonctionnalites implementees

| Domaine | Fonctionnalite | Statut |
|---|---|---|
| Configuration | Un seul `.env` a la racine | Teste |
| Collecte | Ventes et locations Mubawab | Teste en conditions reelles |
| Collecte | Ventes et locations Sarouty | Teste en conditions reelles |
| Donnees | Schema commun enrichi | Teste |
| Machine Learning | Nettoyage et deduplication | Teste |
| Machine Learning | Comparaison de quatre modeles | Teste |
| Machine Learning | Prediction du prix de vente | Teste |
| Analyse | R2, MAE, RMSE, MAPE et erreurs par tranche | Teste |
| Services | Estimation, comparables et anomalies | Teste |
| Services | Marche, comparaison et recommandation | Teste |
| Recherche | Recherche DuckDuckGo sur domaines autorises | Teste |
| Agent | Agent Mistral avec sept outils immobiliers | Teste avec l'API reelle |
| Interface | Sept onglets Streamlit en francais | Teste |

## Pages

- [Demarrage rapide](../QUICK_RUN.md)
- [Demarrage des scrapers](DEMARRAGE_SCRAPERS.md)
- [Demarrage de l'agent IA](DEMARRAGE_AGENT.md)
- [Architecture et configuration](ARCHITECTURE.md)
- [Collecte et schema des donnees](COLLECTE_DONNEES.md)
- [Pipeline Machine Learning](MACHINE_LEARNING.md)
- [Services immobiliers](SERVICES_IMMOBILIERS.md)
- [Agent Mistral](AGENT_IA.md)
- [Interface Streamlit](INTERFACE_STREAMLIT.md)
- [Tests et verification](TESTS.md)
- [Fonctionnalites suivantes](ROADMAP.md)
- [Recherche immobiliere en ligne](RECHERCHE_EN_LIGNE.md)
- [Roadmap historique de l'agent](AGENT_ROADMAP.md)

## Demarrage rapide

```powershell
pip install uv
uv sync
Copy-Item .env.example .env
uv run streamlit run app.py
```

La cle `MISTRAL_API_KEY` est necessaire uniquement pour les fonctions qui
appellent Mistral. Les fonctions locales de scraping, ML et analyse restent
utilisables sans cette cle.
