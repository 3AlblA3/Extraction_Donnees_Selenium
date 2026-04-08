from bs4 import BeautifulSoup
import re

def to_sql_time(t: str) -> str:
    t = t.strip()
    if re.match(r'^\d{1,2}:\d{2}$', t):
        return t + ":00"
    return t


def parse_detail(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    phone = ""
    phone_tag = soup.find("a", href=lambda h: h and h.startswith("tel:"))
    if phone_tag:
        phone = phone_tag.text.strip()

    hours_list = []
    for li in soup.find_all("li"):
        text = li.text.strip()
        if re.search(r'\d{1,2}:\d{2}', text) and re.search(
            r'(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)', text, re.IGNORECASE
        ):
            formatted = re.sub(r'(\d{1,2}:\d{2})(?!:\d{2})', lambda m: to_sql_time(m.group(1)), text)
            hours_list.append(formatted)

    return {"phone": phone, "hours": " | ".join(hours_list)}