### Créer un .venv pour faire fonctionner notre environnement python.
```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### Lancer le pipeline global de récupération de la liste des boutiques 
```powershell
.venv\Scripts\python main.py "URL"
```
