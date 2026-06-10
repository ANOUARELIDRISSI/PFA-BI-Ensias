# Demarrage et test de l'agent IA

Ce guide explique comment configurer et tester l'agent immobilier utilisant
Mistral.

## 1. Installer `uv`

Si `uv` n'est pas encore installe :

```powershell
pip install uv
```

Verifier l'installation :

```powershell
uv --version
```

## 2. Installer toutes les dependances

Depuis la racine `PFA-BI-Ensias`, executer une seule fois :

```powershell
uv sync
```

Un seul environnement `.venv` est cree a la racine. Il contient les
dependances des scrapers, du Machine Learning, des tests et de l'agent.

Il n'est pas necessaire d'activer manuellement cet environnement.

## 3. Ouvrir le dossier de l'agent

```powershell
cd AI-Agent
```

Les commandes `uv run` executees dans ce dossier utilisent automatiquement le
`pyproject.toml`, le `uv.lock` et le `.venv` situes a la racine.

## 4. Creer le fichier `.env`

Copier le fichier d'exemple :

```powershell
Copy-Item .env.example .env
```

Ouvrir ensuite `.env` et remplacer la valeur d'exemple :

```env
MISTRAL_API_KEY=your_real_mistral_api_key
```

Ne jamais enregistrer ou pousser le fichier `.env` dans Git.

## 5. Lancer le chat interactif

```powershell
uv run python main.py
```

Il est egalement possible de lancer l'agent depuis la racine :

```powershell
uv run python AI-Agent/main.py
```

Exemple de message :

```text
Bonjour, presente-toi en une phrase.
```

Commandes disponibles :

- `reset` : reinitialiser la conversation ;
- `quitter` : fermer l'agent.

## 6. Effectuer un test rapide

Pour tester l'agent avec un seul message :

```powershell
uv run python -c "from agent import RealEstateAgent; print(RealEstateAgent().chat('Bonjour, presente-toi en une phrase.'))"
```

Le test est reussi si Mistral retourne une reponse en francais sans erreur.

## 7. Verifier la configuration sans afficher la cle

```powershell
uv run python -c "import os; from dotenv import load_dotenv; load_dotenv(); assert os.getenv('MISTRAL_API_KEY'); print('Configuration Mistral valide')"
```

Cette commande confirme que la cle est chargee sans afficher sa valeur.

## 8. Problemes courants

### `MISTRAL_API_KEY est absente`

Verifier que :

- le fichier s'appelle exactement `.env` ;
- il se trouve dans `AI-Agent/` ;
- la variable s'appelle exactement `MISTRAL_API_KEY`.

### `uv` n'est pas reconnu

Fermer et rouvrir PowerShell apres l'installation, puis executer :

```powershell
uv --version
```

### Erreur d'authentification

La cle est absente, invalide, expiree ou revoquee. Creer une nouvelle cle
Mistral et mettre a jour uniquement le fichier local `.env`.

### Erreur reseau ou limite API

Verifier la connexion Internet, patienter quelques instants, puis relancer le
test. Consulter egalement le quota du compte Mistral.
