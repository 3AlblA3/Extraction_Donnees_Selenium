import re
from collections import Counter
from urllib.parse import urlparse

# Préfixes de classes CSS souvent associés au nom d'une boutique
_NAME_PREFIXES = re.compile(r'(name|title|label|brand|heading)', re.IGNORECASE)
# Textes à exclure : numéros d'étage, statuts d'ouverture, ponctuation seule
_EXCLUDE = re.compile(r'^(-?\d+|ouvert|fermé|open|closed|\.+)$', re.IGNORECASE)

def _find_by_class_prefix(tag, pattern: re.Pattern) -> str:
    texts = []
    for el in tag.find_all(True):
        classes = el.get("class", [])
        if any(pattern.search(c) for c in classes):
            text = el.get_text(strip=True)
            if text:
                texts.append(text)

    if not texts:
        return ""

    # Élément le plus spécifique = texte le plus court
    text = min(texts, key=len)

    # Déduplique si le nom apparaît deux fois (logo + texte)
    half = len(text) // 2
    if half > 0 and text[:half] == text[half:]:
        text = text[:half]

    text = text.strip()
    return text if text and not _EXCLUDE.match(text) else ""

def detect_shops(soup, min_count: int = 10) -> list[dict]:
    class_counter = Counter()
    candidates = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        path = urlparse(href).path if href.startswith("http") else href
        segments = [s for s in path.split("/") if s]
        if len(segments) < 2:
            continue
        for cls in a.get("class", []):
            class_counter[cls] += 1
        candidates.append(a)

    if not class_counter:
        return []

    dominant_class = class_counter.most_common(1)[0][0]
    if class_counter[dominant_class] < min_count:
        return []

    print(f"Classe dominante détectée : '{dominant_class}' ({class_counter[dominant_class]} occurrences)")

    shops = []
    seen_urls = set()
    for a in candidates:
        if dominant_class not in a.get("class", []):
            continue

        href = a.get("href", "")
        if href in seen_urls:
            continue
        seen_urls.add(href)

        name = _find_by_class_prefix(a, _NAME_PREFIXES)

        # fallback — texte le plus long parmi les non-exclus
        if not name:
            texts = [t.strip() for t in a.stripped_strings
                     if len(t.strip()) > 1 and not _EXCLUDE.match(t.strip())]
            if texts:
                name = max(texts, key=len)

        all_texts = [t.strip() for t in a.stripped_strings
                     if len(t.strip()) > 1 and not _EXCLUDE.match(t.strip()) and t.strip() != name]
        details = " | ".join(dict.fromkeys(all_texts))  # dédupliqué, ordre préservé

        if name:
            shops.append({"name": name, "details": details, "url": href})

    return shops
