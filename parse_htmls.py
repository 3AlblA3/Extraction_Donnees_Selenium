"""
Étape 2 – Extraction des boutiques vers CSV
Lit htmls/manifest.json, parse chaque HTML sauvegardé et produit un CSV par centre commercial dans shop-list/.
"""

import json
import os
from westfiedGetList import get_westfield_shop_list
from csvExporter import save_csv

MANIFEST_PATH = "htmls/manifest.json"

if not os.path.exists(MANIFEST_PATH):
    raise FileNotFoundError(
        f"Manifest introuvable : {MANIFEST_PATH}\n"
        "Lancez d'abord fetch_htmls.py pour télécharger les HTMLs."
    )

with open(MANIFEST_PATH, encoding="utf-8") as f:
    manifest = json.load(f)

for html_path, url in manifest.items():
    if not os.path.exists(html_path):
        print(f"[IGNORÉ] Fichier HTML manquant : {html_path}")
        continue

    csv_name = os.path.basename(html_path).replace(".html", ".csv")
    csv_path = f"shop-list/{csv_name}"

    print(f"\n=== {html_path} ===")
    shops = get_westfield_shop_list(html_path, url)
    save_csv(shops, csv_path)

print(f"\nTerminé. {len(manifest)} centres traités.")
