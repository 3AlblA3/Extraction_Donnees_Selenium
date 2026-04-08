from collections import Counter
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def detect_shops(html: str, base_url: str, min_count: int = 10) -> list[dict]:
    """
    Détecte automatiquement les cartes boutiques en cherchant
    la classe CSS la plus répétée sur des balises <a> pointant vers des sous-pages.
    """
    soup = BeautifulSoup(html, "html.parser")
    parsed_base = urlparse(base_url)
    base_path = parsed_base.path.rstrip("/")

    # Compte les classes sur les <a> qui pointent vers des sous-chemins de l'URL de base
    class_counter = Counter()
    candidates = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        # Ne retenir que les liens vers des sous-pages (profondeur +1)
        if href.startswith(base_path + "/") or href.startswith("http") and base_path in href:
            for cls in a.get("class", []):
                class_counter[cls] += 1
            candidates.append(a)

    if not class_counter:
        return []

    # La classe la plus répétée est très probablement celle des cartes
    dominant_class = class_counter.most_common(1)[0][0]
    count = class_counter[dominant_class]

    if count < min_count:
        return []

    print(f"Classe dominante détectée : '{dominant_class}' ({count} occurrences)")

    # Extraire nom, catégorie, URL pour chaque carte
    shops = []
    seen_urls = set()
    for a in candidates:
        if dominant_class not in a.get("class", []):
            continue

        href = a.get("href", "")
        # Reconstruire l'URL absolue si relative
        if href.startswith("/"):
            href = f"{parsed_base.scheme}://{parsed_base.netloc}{href}"

        if href in seen_urls:
            continue
        seen_urls.add(href)

        # Nom : le texte le plus court parmi les enfants directs significatifs
        texts = [t.strip() for t in a.stripped_strings if len(t.strip()) > 1]
        name = min(texts, key=len) if texts else ""

        # Catégorie : le texte le plus long (souvent la description)
        category = max(texts, key=len) if len(texts) > 1 else ""
        if category == name:
            category = ""

        if name:
            shops.append({"name": name, "category": category, "url": href})

    return shops
