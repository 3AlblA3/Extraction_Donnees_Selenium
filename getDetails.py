import time
import requests
from utils import parse_detail

# Fetcher pour enrichir les données de chaque boutique avec les détails (téléphone, horaires)
# Prends en paramètre la liste des boutiques et modifie chaque boutique en place
def enrich_shops(shops: list[dict]) -> None:
    total = len(shops)
    for i, shop in enumerate(shops, 1):
        shop["phone"] = ""
        shop["hours"] = ""
        try:
            response = requests.get(shop["url"], timeout=10)
            shop.update(parse_detail(response.text))
            print(f"[{i}/{total}] OK : {shop['name']}")
        except Exception as e:
            print(f"[{i}/{total}] ERREUR {shop['name']} : {e}")
        time.sleep(0.3)
