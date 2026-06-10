# AI Agent

Agent conversationnel minimal utilisant Mistral pour le projet immobilier
marocain.

## Installation

Toutes les dependances sont gerees par le projet `uv` situe a la racine.

```powershell
cd ..
pip install uv
uv sync
cd AI-Agent
Copy-Item .env.example .env
```

Ajouter une cle valide dans `.env` :

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

## Lancement

```powershell
uv run python main.py
```

`uv` detecte automatiquement le projet racine depuis ce dossier.

Commandes disponibles :

- `reset` reinitialise la conversation ;
- `quitter` ferme le programme.

## Test rapide

```powershell
uv run python -c "from agent import RealEstateAgent; print(RealEstateAgent().chat('Presente-toi en une phrase.'))"
```
