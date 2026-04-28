from bs4 import BeautifulSoup
from westfieldDetect import detect_westfield_shops


def get_westfield_shop_list(html_path: str, base_url: str) -> list[dict]:
    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    print("Détection automatique des boutiques...")
    shops = detect_westfield_shops(soup, base_url)
    print(f"{len(shops)} boutiques trouvées.")
    return shops
