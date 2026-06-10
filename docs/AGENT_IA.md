# Agent IA Mistral

## Fonctionnement

L'agent se trouve dans `AI-Agent/agent.py`. Il utilise Mistral et conserve
l'historique de la conversation pendant la session.

Le seul secret utilise est `MISTRAL_API_KEY`, charge depuis le `.env` de la
racine par `config.py`.

## Outils disponibles

L'agent dispose de sept outils dans `AI-Agent/tools.py` :

1. `predict_property_price`
2. `find_comparable_properties`
3. `detect_listing_price_anomaly`
4. `get_market_summary`
5. `compare_properties`
6. `recommend_properties`
7. `search_live_properties`

Le prompt impose l'utilisation des outils pour les chiffres immobiliers. Le
modele ne doit pas inventer un prix, une annonce ou une statistique.

## Lancement

```powershell
uv run python AI-Agent/main.py
```

Commandes interactives :

- `reset` efface l'historique ;
- `quitter` ferme le programme.

## Verification reelle

Une requete reelle a l'API Mistral a ete executee avec succes depuis le `.env`
de la racine. Les tests automatises des outils utilisent des doubles pour ne
pas consommer le quota API a chaque execution.

## Comportement attendu

- repondre en francais ;
- distinguer donnees observees et estimations ;
- citer les URLs des annonces ;
- signaler si une page recente a ete verifiee ;
- conserver les avertissements des services ;
- demander les caracteristiques manquantes plutot que les inventer.

## Limites

L'agent ne lance pas encore automatiquement les scrapers, l'entrainement ou
les alertes planifiees. Ces actions necessitent une couche d'orchestration avec
permissions, journalisation et controle explicite.
