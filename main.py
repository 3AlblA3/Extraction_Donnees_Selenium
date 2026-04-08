import argparse
import re
from datetime import date
from urllib.parse import urlparse
from getHtml import fetch_html
from getList import get_shop_list
from csvExporter import save_csv

parser = argparse.ArgumentParser(description="Scraper de boutiques")
parser.add_argument("url", help="URL de la page liste des boutiques")
args = parser.parse_args()

DATE_SUFFIX = date.today().strftime("%Y%m%d")
match = re.search(r'www\.([^.]+)\.', args.url)
mall_name = match.group(1) if match else "shop"

HTML_PATH = f"htmls/{mall_name}_{DATE_SUFFIX}.html"
CSV_PATH = f"shop-list/{mall_name}_{DATE_SUFFIX}.csv"

fetch_html(args.url, HTML_PATH)
shops = get_shop_list(HTML_PATH)

# Reconstruction des URLs relatives en absolues
parsed = urlparse(args.url)
base_origin = f"{parsed.scheme}://{parsed.netloc}"
for shop in shops:
    if shop["url"].startswith("/"):
        shop["url"] = base_origin + shop["url"]

save_csv(shops, CSV_PATH)
