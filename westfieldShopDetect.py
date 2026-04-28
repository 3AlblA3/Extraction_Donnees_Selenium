"""
Extraction des données d'une page détail boutique Westfield.

- Catégories  : parsées dans le DOM (BrandDetail_tagList > BrandDetail_tag)
- Horaires    : extraits du payload RSC Next.js (trading_hours > days_of_week)
  Les horaires ne sont PAS rendus côté serveur dans le DOM (BAILOUT_TO_CLIENT_SIDE_RENDERING),
  mais les données JSON brutes sont bien présentes dans les scripts self.__next_f.push.
"""

import re
from bs4 import BeautifulSoup

_CLS_TAG_LIST = re.compile(r'BrandDetail_tagList')
_CLS_TAG      = re.compile(r'BrandDetail_tag__')

# day_of_week suit la convention JS : 0=Dim, 1=Lun, ..., 6=Sam
_DAYS_FR = {0: "Dim", 1: "Lun", 2: "Mar", 3: "Mer", 4: "Jeu", 5: "Ven", 6: "Sam"}

# Regex pour extraire le tableau days_of_week depuis le payload RSC (quotes échappées \")
_RE_DAYS_ARRAY = re.compile(r'\\"days_of_week\\":\[(.+?)\](?=[,}])', re.DOTALL)
_RE_DAY_ENTRY  = re.compile(
    r'\\"day_of_week\\":(\d+)'
    r',\\"starts_at\\":\\"(\d{2}:\d{2}):\d{2}\\"'
    r',\\"ends_at\\":\\"(\d{2}:\d{2}):\d{2}\\"'
    r',\\"type\\":\\"(\w+)\\"'
)


def _extract_categories(soup: BeautifulSoup) -> str:
    tag_list = soup.find(True, class_=_CLS_TAG_LIST)
    if not tag_list:
        return ""
    tags = [t.get_text(strip=True) for t in tag_list.find_all(True, class_=_CLS_TAG)]
    return " | ".join(dict.fromkeys(t for t in tags if t))  # dédoublonné, ordre préservé


def _extract_trading_hours(html_content: str) -> str:
    match = _RE_DAYS_ARRAY.search(html_content)
    if not match:
        return ""
    parts = []
    for m in _RE_DAY_ENTRY.finditer(match.group(1)):
        dow, start, end, typ = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        label = _DAYS_FR.get(dow, str(dow))
        parts.append(f"{label} {start}-{end}" if typ == "open" else f"{label} fermé")
    return " | ".join(parts)


def detect_westfield_shop_details(html_path: str) -> dict:
    """Lit le HTML d'une page boutique et retourne {"category": str, "schedule": str}."""
    try:
        with open(html_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError):
        return {"category": "", "schedule": ""}

    soup = BeautifulSoup(content, "html.parser")
    return {
        "category": _extract_categories(soup),
        "schedule": _extract_trading_hours(content),
    }
