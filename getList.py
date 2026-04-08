from bs4 import BeautifulSoup
from autoDetect import detect_shops


def get_shop_list(html_path: str) -> list[dict]:
    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    print("Détection automatique des boutiques...")
    shops = detect_shops(soup)
    print(f"{len(shops)} boutiques trouvées.")
    return shops
