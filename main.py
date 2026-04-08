import argparse
import re
from datetime import date
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

shops = get_shop_list(args.url, HTML_PATH)
save_csv(shops, CSV_PATH)
