from autoDetect import detect_shops
from getHtml import fetch_html


def get_shop_list(url: str, html_path: str) -> list[dict]:
    fetch_html(url, html_path)

    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    print("Détection automatique des boutiques...")
    shops = detect_shops(html, url)
    print(f"{len(shops)} boutiques trouvées.")
    return shops
