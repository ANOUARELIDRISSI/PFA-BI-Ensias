# Recherche immobiliere en ligne

Cette fonctionnalite utilise la bibliotheque Python `ddgs` pour decouvrir des
annonces immobilieres recentes sans cle API supplementaire.

## Sources autorisees

La recherche est limitee aux domaines suivants :

- `mubawab.ma`
- `sarouty.ma`
- `avito.ma`
- `agenz.ma`

Un resultat provenant d'un autre domaine est ignore.

## Fonctionnement

1. Le systeme construit une requete par domaine avec la ville, le quartier, le
   type de bien et le type de transaction.
2. `DDGS.text()` retourne les pages trouvees.
3. Les URLs sont normalisees et dedupliquees.
4. Chaque page est ouverte avec une requete HTTP limitee dans le temps.
5. Le resultat est marque `verified=true` uniquement si la page repond avec un
   statut HTTP 200 et reste sur un domaine autorise.
6. Le titre, la source, l'URL, le resume, le prix detecte et la date de
   consultation sont retournes.

## Utilisation dans Streamlit

```powershell
uv run streamlit run app.py
```

Ouvrir ensuite l'onglet `Recherche en ligne`.

## Utilisation dans l'agent

L'agent Mistral dispose de l'outil `search_live_properties`.

Exemple :

```text
Trouve des appartements a louer a Agdal, Rabat, avec les liens sources.
```

L'agent doit indiquer si chaque resultat a ete verifie et ne doit jamais
inventer une annonce ou un prix manquant.

## Limites

- La disponibilite de DuckDuckGo et des sites cibles peut varier.
- Certains sites peuvent refuser les requetes automatisees.
- Un resultat non verifie peut etre affiche, mais il doit etre clairement
  identifie comme tel.
- La verification HTTP confirme seulement que la page est accessible. Elle ne
  confirme pas que l'annonce est encore disponible ou juridiquement fiable.
- Les prix sont extraits depuis le texte lorsqu'un format `MAD`, `DH` ou `DHS`
  est detecte. Ils peuvent rester absents.

## Tests

Les tests automatises remplacent DDGS et les requetes de verification par des
reponses controlees. Cela permet de verifier le filtrage, la deduplication et le
format des resultats sans dependre du reseau.

```powershell
uv run pytest -q
```

Une verification live courte peut etre lancee manuellement :

```powershell
uv run python -c "from real_estate.web_search import search_properties; print(search_properties('Casablanca', max_results=4, verify=False))"
```
