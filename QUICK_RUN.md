# Quick Run

Ce guide permet de lancer le projet sur un nouvel ordinateur apres un clonage.
Executer toutes les commandes depuis la racine `PFA-BI-Ensias`.

## 1. Prerequis

- Git
- Python 3.12 ou plus recent

```powershell
git --version
python --version
```

## 2. Cloner le projet

```powershell
git clone https://github.com/ANOUARELIDRISSI/PFA-BI-Ensias.git
cd PFA-BI-Ensias
```

## 3. Installer le projet

```powershell
python -m pip install uv
uv sync
```

`uv sync` cree l'environnement virtuel unique dans `.venv`.

## 4. Configurer Mistral

PowerShell :

```powershell
Copy-Item .env.example .env
```

Linux ou macOS :

```bash
cp .env.example .env
```

Modifier le `.env` de la racine :

```env
MISTRAL_API_KEY=your_real_mistral_api_key
```

Ne jamais pousser ce fichier.

## 5. Generer les donnees et le modele

Les donnees, modeles et rapports sont ignores par Git. Un nouveau clone doit
donc les generer avant d'utiliser toutes les fonctionnalites.

```powershell
uv run python scraping/scrape_mubawab.py --transaction sale --min-listings 150 --max-pages 20 --overwrite
uv run python scraping/scrape_sarouty.py --transaction sale --min-listings 150 --overwrite
uv run python -m ml.clean_data
uv run python -m ml.train
```

## 6. Verifier

```powershell
uv run pytest -q
```

Test Mistral reel :

```powershell
uv run python -c "import sys; sys.path.insert(0, 'AI-Agent'); from agent import RealEstateAgent; print(RealEstateAgent().chat('Presente-toi en une phrase.'))"
```

## 7. Lancer Streamlit

```powershell
uv run streamlit run app.py
```

Ouvrir `http://localhost:8501`.

## Commandes utiles

Agent en terminal :

```powershell
uv run python AI-Agent/main.py
```

Collecter les locations :

```powershell
uv run python scraping/scrape_mubawab.py --transaction rent --min-listings 150 --max-pages 20 --overwrite
uv run python scraping/scrape_sarouty.py --transaction rent --min-listings 150 --overwrite
```

Relancer le pipeline ML :

```powershell
uv run python -m ml.clean_data
uv run python -m ml.train
```

Mettre le projet a jour :

```powershell
git pull origin main
uv sync
```

Documentation detaillee : [docs/README.md](docs/README.md).
