import re
from urllib.parse import urlparse

# Les classes Westfield sont des CSS Modules : préfixe stable + hash variable (ex: BrandCard_name__MDcdt)
_CLS_CARD  = re.compile(r'BrandCardGrid_cardLink')
_CLS_NAME  = re.compile(r'BrandCard_name')
_CLS_LEVEL = re.compile(r'BrandCard_level')
_CLS_INFO  = re.compile(r'BrandCard_info')


def detect_westfield_shops(soup, base_url: str) -> list[dict]:
    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    shops = []
    for card in soup.find_all("a", class_=_CLS_CARD):
        href = card.get("href", "")
        if href.startswith("/"):
            href = origin + href

        name_tag = card.find(True, class_=_CLS_NAME)
        name = name_tag.get_text(strip=True) if name_tag else ""

        details = ""
        info_tag = card.find(True, class_=_CLS_INFO)
        if info_tag:
            level_tag = info_tag.find(True, class_=_CLS_LEVEL)
            level = level_tag.get_text(strip=True) if level_tag else ""
            # La zone est le dernier <span> dans info (après le level et le sr-only)
            spans = info_tag.find_all("span", recursive=False)
            zone = spans[-1].get_text(strip=True) if spans else ""
            parts = [p for p in [level, zone] if p]
            details = " | ".join(parts)

        if name:
            shops.append({"name": name, "details": details, "url": href})

    return shops
