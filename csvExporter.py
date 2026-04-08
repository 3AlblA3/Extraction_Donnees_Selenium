import os
import csv

FIELDNAMES = ["name", "details", "url"]

# Enregistre la liste des boutiques dans un fichier CSV
def save_csv(shops: list[dict], csv_path: str) -> None:
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(shops)
    print(f"CSV sauvegardé : {csv_path}")
