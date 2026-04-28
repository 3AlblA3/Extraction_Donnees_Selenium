"""
Détection des fermetures de boutiques.

Pour chaque centre commercial, compare les CSVs dans shop-list/ triés par date.
Une boutique est considérée fermée si elle apparaissait dans un CSV passé
mais n'est plus présente dans le CSV le plus récent.

Sortie :
  - shop-list/<mall>_historique_fermeture.csv  ← créé/mis à jour si fermetures trouvées
  - Logs console dans tous les cas
"""

import csv
import os
import re
from collections import defaultdict
from datetime import datetime

SHOP_LIST_DIR = "shop-list"

# Correspond à : <mall_slug>_liste_<YYYYMMDD>.csv
_CSV_RE = re.compile(r'^(.+)_liste_(\d{8})\.csv$')

FERMETURE_COLS = ["nom_boutique", "date_fermeture_supposee"]


def read_shop_names(csv_path: str) -> set[str]:
    """Retourne l'ensemble des noms de boutiques d'un CSV."""
    names = set()
    with open(csv_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            name = row.get("name", "").strip()
            if name:
                names.add(name)
    return names


def fmt_date(date_str: str) -> str:
    """20260428 → 28/04/2026"""
    return datetime.strptime(date_str, "%Y%m%d").strftime("%d/%m/%Y")


# ── 1. Regrouper les CSVs par centre commercial ────────────────────────────────
mall_csvs: dict[str, list[tuple[str, str]]] = defaultdict(list)

for fname in os.listdir(SHOP_LIST_DIR):
    m = _CSV_RE.match(fname)
    if m:
        mall_slug, date_str = m.group(1), m.group(2)
        mall_csvs[mall_slug].append((date_str, os.path.join(SHOP_LIST_DIR, fname)))

if not mall_csvs:
    print("Aucun CSV trouvé dans shop-list/. Lancez d'abord parse_htmls.py.")
    raise SystemExit(1)

# ── 2. Analyser chaque centre ──────────────────────────────────────────────────
for mall_slug, entries in sorted(mall_csvs.items()):
    entries.sort(key=lambda x: x[0])  # tri chronologique croissant

    if len(entries) < 2:
        print(f"[{mall_slug}] Un seul CSV disponible — pas de comparaison possible.")
        continue

    all_dates = [d for d, _ in entries]
    latest_date = all_dates[-1]

    # Construire l'historique de présence : boutique → ensemble de dates où elle apparaît
    presence: dict[str, set[str]] = {}
    for date_str, path in entries:
        for name in read_shop_names(path):
            presence.setdefault(name, set()).add(date_str)

    # Boutiques absentes du dernier CSV
    fermetures: list[tuple[str, str]] = []
    for name, dates_seen in presence.items():
        if latest_date not in dates_seen:
            # Date de fermeture supposée = premier CSV où elles n'apparaissent plus
            last_seen = max(dates_seen)
            dates_after = [d for d in all_dates if d > last_seen]
            first_missing = dates_after[0] if dates_after else latest_date
            fermetures.append((name, first_missing))

    if not fermetures:
        print(f"[{mall_slug}] Aucune fermeture détectée.")
        continue

    # ── 3. Écrire/mettre à jour le CSV historique ─────────────────────────────
    out_path = os.path.join(SHOP_LIST_DIR, f"{mall_slug}_historique_fermeture.csv")

    # Charger les fermetures déjà enregistrées pour éviter les doublons
    already_recorded: set[str] = set()
    file_exists = os.path.exists(out_path)
    if file_exists:
        with open(out_path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                already_recorded.add(row.get("nom_boutique", ""))

    new_fermetures = [(n, d) for n, d in fermetures if n not in already_recorded]

    if new_fermetures:
        mode = "a" if file_exists else "w"
        with open(out_path, mode, encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FERMETURE_COLS)
            if not file_exists:
                writer.writeheader()
            for name, date_str in sorted(new_fermetures):
                writer.writerow({
                    "nom_boutique": name,
                    "date_fermeture_supposee": fmt_date(date_str),
                })
        print(f"[{mall_slug}] {len(new_fermetures)} fermeture(s) enregistrée(s) → {out_path}")
    else:
        print(f"[{mall_slug}] Aucune nouvelle fermeture (déjà toutes enregistrées).")
