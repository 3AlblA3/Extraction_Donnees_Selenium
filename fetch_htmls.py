"""
Étape 1 – Téléchargement des HTMLs
Parcourt toutes les URLs et sauvegarde le HTML de chaque page dans htmls/.
Produit aussi htmls/manifest.json qui associe chaque fichier HTML à son URL d'origine.
"""

import json
import os
import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def fetch_html(url: str, html_path: str) -> None:
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
    print(f"HTML sauvegardé : {html_path}")


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

manifest = {}

for url in URLS:
    stripped = url.split("://", 1)[-1].rstrip("/")
    mall_name = stripped.replace(".", "_").replace("/", "_")
    html_path = f"htmls/{mall_name}_{DATE_SUFFIX}.html"

    print(f"\n=== {url} ===")
    fetch_html(url, html_path)
    manifest[html_path] = url

os.makedirs("htmls", exist_ok=True)
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"\nManifest sauvegardé : {MANIFEST_PATH} ({len(manifest)} entrées)")
