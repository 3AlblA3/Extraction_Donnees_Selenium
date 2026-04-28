"""
Étape 2 – Extraction des boutiques vers CSV
Lit htmls/manifest.json, parse le HTML de la page liste de chaque centre,
enrichit avec les données des pages boutiques individuelles (catégorie, horaires),
et produit un CSV par centre commercial dans shop-list/.
Nommage CSV : <nomCentre>_liste_<dateParssing>.csv
"""

import json
import os
from datetime import date
from westfiedGetList import get_westfield_shop_list
from westfieldShopDetect import detect_westfield_shop_details
from csvExporter import save_csv

MANIFEST_PATH = "htmls/manifest.json"
DATE_SUFFIX = date.today().strftime("%Y%m%d")

if not os.path.exists(MANIFEST_PATH):
    raise FileNotFoundError(
        f"Manifest introuvable : {MANIFEST_PATH}\n"
        "Lancez d'abord fetch_htmls.py pour télécharger les HTMLs."
    )

with open(MANIFEST_PATH, encoding="utf-8") as f:
    manifest = json.load(f)

for mall_slug, entry in manifest.items():
    mall_url   = entry["url"]
    index_path = entry["index"]
    shops_map  = entry["shops"]   # {html_path: shop_url}

    if not os.path.exists(index_path):
        print(f"[IGNORÉ] Fichier index manquant : {index_path}")
        continue

    print(f"\n=== {mall_slug} ===")

    # 1. Lire la liste des boutiques depuis la page index
    shops = get_westfield_shop_list(index_path, mall_url)

    # 2. Construire un index url → chemin HTML pour les pages détail
    url_to_html = {v: k for k, v in shops_map.items()}

    # 3. Enrichir chaque boutique avec catégorie + horaires
    for shop in shops:
        detail_path = url_to_html.get(shop["url"])
        if detail_path and os.path.exists(detail_path):
            details = detect_westfield_shop_details(detail_path)
            shop["category"] = details["category"]
            shop["schedule"] = details["schedule"]
        else:
            shop["category"] = ""
            shop["schedule"] = ""

    # 4. Sauvegarder le CSV — nomenclature : <nomCentre>_liste_<dateParssing>.csv
    csv_path = f"shop-list/{mall_slug}_liste_{DATE_SUFFIX}.csv"
    save_csv(shops, csv_path)

print(f"\nTerminé. {len(manifest)} centres traités.")
