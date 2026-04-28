"""
Étape 1 – Téléchargement des HTMLs
Pour chaque centre commercial :
  - Télécharge la page liste avec Selenium (JS requis pour "Voir plus")
  - Extrait les URLs de chaque boutique depuis le HTML obtenu
  - Télécharge chaque page boutique avec requests (SSR Next.js, pas de JS requis)

Structure des fichiers :
  htmls/<mall_slug>/_index_<date>.html       ← page liste
  htmls/<mall_slug>/<shop_slug>_<date>.html  ← page détail boutique
  htmls/manifest.json                        ← mapping fichiers ↔ URLs
"""

import json
import os
import time
import requests
from datetime import date
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from westfieldDetect import detect_westfield_shops

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

URLS = [
    "https://www.westfield.com/fr/france/forumdeshalles/boutiques",
    "https://www.westfield.com/fr/france/les4temps/boutiques",
    "https://www.westfield.com/fr/france/lapartdieu/boutiques",
    "https://www.westfield.com/fr/france/euralille/boutiques",
    "https://www.westfield.com/fr/france/rosny2/boutiques",
    "https://www.westfield.com/fr/france/parly2/boutiques",
    "https://www.westfield.com/fr/france/velizy2/boutiques",
    "https://www.westfield.com/fr/france/carrouseldulouvre/boutiques",
    "https://www.westfield.com/fr/france/rennesalma/boutiques",
]

MANIFEST_PATH = "htmls/manifest.json"
DATE_SUFFIX = date.today().strftime("%Y%m%d")


def fetch_listing_html(url: str, html_path: str) -> str:
    """Télécharge la page liste avec Selenium. Retourne le HTML sous forme de chaîne."""
    driver = webdriver.Chrome()
    driver.get(url)

    # Cliquer sur "Voir plus" / "Load more" jusqu'à disparition
    while True:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[normalize-space()='Voir plus' or normalize-space()='Load more' or normalize-space()='Show more']"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            btn.click()
            time.sleep(1.5)
        except (NoSuchElementException, TimeoutException):
            break

    html = BeautifulSoup(driver.page_source, "html.parser").prettify()
    driver.quit()

    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Index sauvegardé : {html_path}")
    return html


def fetch_shop_html(url: str, html_path: str, session: requests.Session) -> None:
    """Télécharge une page boutique avec requests (rendu SSR, pas de JS requis)."""
    try:
        response = session.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = BeautifulSoup(response.text, "html.parser").prettify()
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
    except requests.RequestException as e:
        print(f"  [ERREUR] {url} : {e}")


def shop_url_to_slug(shop_url: str) -> str:
    """Convertit une URL boutique en slug de fichier. ex: .../adidas/63178 → adidas_63178"""
    parts = shop_url.rstrip("/").split("/")
    return "_".join(parts[-2:])


manifest = {}

with requests.Session() as session:
    for url in URLS:
        mall_slug = urlparse(url).path.strip("/").split("/")[2]  # ex: "les4temps"
        mall_dir = f"htmls/{mall_slug}"
        index_path = f"{mall_dir}/_index_{DATE_SUFFIX}.html"

        print(f"\n=== {url} ===")
        listing_html = fetch_listing_html(url, index_path)

        # Extraire les URLs des boutiques depuis la page liste
        soup = BeautifulSoup(listing_html, "html.parser")
        shops = detect_westfield_shops(soup, url)
        print(f"  {len(shops)} boutiques trouvées, téléchargement des pages détail...")

        shop_manifest = {}
        for i, shop in enumerate(shops, 1):
            shop_url = shop["url"]
            slug = shop_url_to_slug(shop_url)
            shop_path = f"{mall_dir}/{slug}_{DATE_SUFFIX}.html"
            fetch_shop_html(shop_url, shop_path, session)
            shop_manifest[shop_path] = shop_url
            time.sleep(0.3)  # politesse envers le serveur
            if i % 20 == 0:
                print(f"  ... {i}/{len(shops)}")

        manifest[mall_slug] = {
            "url": url,
            "index": index_path,
            "shops": shop_manifest,
        }
        print(f"  Terminé : {len(shops)} boutiques.")

os.makedirs("htmls", exist_ok=True)
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\nManifest sauvegardé : {MANIFEST_PATH}")
