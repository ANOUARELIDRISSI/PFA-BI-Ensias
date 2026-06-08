# AI Agent

Agent conversationnel minimal utilisant Mistral pour le projet immobilier
marocain.

## Installation

```powershell
pip install uv
uv sync
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

Commandes disponibles :

- `reset` reinitialise la conversation ;
- `quitter` ferme le programme.

## Test rapide

```powershell
uv run python -c "from agent import RealEstateAgent; print(RealEstateAgent().chat('Presente-toi en une phrase.'))"
```
