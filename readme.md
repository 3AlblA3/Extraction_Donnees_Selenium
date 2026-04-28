### Créer un .venv pour faire fonctionner notre environnement python.
```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### Étape 1 – Télécharger les HTMLs des centres commerciaux
```powershell
.venv\Scripts\python fetch_htmls.py
```
Les HTMLs sont sauvegardés dans `htmls/` ainsi qu'un fichier `htmls/manifest.json`.

### Étape 2 – Extraire la liste des boutiques en CSV
```powershell
.venv\Scripts\python parse_htmls.py
```
Les fichiers CSV sont générés dans `shop-list/`, un par centre commercial.
