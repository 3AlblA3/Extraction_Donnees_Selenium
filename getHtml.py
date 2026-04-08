import os
import time
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
