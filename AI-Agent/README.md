# AI Agent

Agent conversationnel minimal utilisant Mistral pour le projet immobilier
marocain.

## Installation

Toutes les dependances sont gerees par le projet `uv` situe a la racine.

```powershell
cd ..
pip install uv
uv sync
Copy-Item .env.example .env
```

Ajouter une cle valide dans le fichier `.env` de la racine :

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

## Lancement

```powershell
uv run python AI-Agent/main.py
```

L'agent charge uniquement la configuration de la racine.

Commandes disponibles :

- `reset` reinitialise la conversation ;
- `quitter` ferme le programme.

## Test rapide

```powershell
uv run python AI-Agent/main.py
```
