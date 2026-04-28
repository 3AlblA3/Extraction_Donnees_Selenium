# Westfield Scraper

Pipeline de scraping des boutiques des centres commerciaux Westfield France.

---

## Installation

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

---

## Pipeline

### Étape 1 – Télécharger les HTMLs

```powershell
.venv\Scripts\python fetch_htmls.py
```

Pour chaque centre commercial :
- Télécharge la page liste des boutiques avec Selenium (clique sur "Voir plus" jusqu'au bout)
- Extrait les URLs de chaque boutique
- Télécharge la page détail de chaque boutique avec `requests` (rendu SSR, pas de Selenium)

**Sorties :**
- `htmls/<mall>/` — dossier par centre contenant `_index_<date>.html` + un HTML par boutique
- `htmls/manifest.json` — mapping entre fichiers HTML et URLs d'origine

---

### Étape 2 – Extraire les boutiques en CSV

```powershell
.venv\Scripts\python parse_htmls.py
```

Lit le manifest, parse chaque HTML et produit un CSV enrichi par centre.

**Colonnes CSV :** `name`, `details`, `url`, `category`, `schedule`

**Nomenclature :** `shop-list/<nomCentre>_liste_<dateParssing>.csv`

---

### Étape 3 – Détecter les fermetures

```powershell
.venv\Scripts\python check_fermetures.py
```

Compare les CSVs par date pour chaque centre commercial.
Une boutique est considérée fermée si elle était présente dans un CSV passé mais absente du plus récent.

- Si des fermetures sont détectées → crée ou met à jour `shop-list/<nomCentre>_historique_fermeture.csv`
- Si aucune fermeture → log console "Aucune fermeture détectée"
- Si un seul CSV disponible pour un centre → log "pas de comparaison possible"

**Colonnes CSV fermeture :** `nom_boutique`, `date_fermeture_supposee`

---

## Structure des fichiers

```
htmls/
  manifest.json
  <mall>/
    _index_<date>.html         ← page liste complète
    <boutique>_<id>_<date>.html

shop-list/
  <mall>_liste_<date>.csv
  <mall>_historique_fermeture.csv   ← créé si fermetures détectées
```

---

## Centres couverts

- Forum des Halles
- Les 4 Temps
- La Part-Dieu
- Euralille
- Rosny 2
- Parly 2
- Vélizy 2
- Carrousel du Louvre
- Rennes Alma
