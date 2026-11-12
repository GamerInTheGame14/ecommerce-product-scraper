
import csv
import json
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

OUTPUT_FILE = DATA_DIR / "products.csv"
CHECKPOINT_FILE = DATA_DIR / "checkpoint.json"

FIELDNAMES = [
    "title",
    "price",
    "rating",
    "product_url",
    "upc",
    "availability",
    "category",
    "description",
    "price_excl_tax",
    "price_incl_tax",
]


def create_session():
    session = requests.Session()

    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update({
        "User-Agent": "PortfolioProductScraper/1.0"
    })

    return session


def save_checkpoint(next_url, page_number):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "next_url": next_url,
        "page_number": page_number,
    }

    temporary_file = CHECKPOINT_FILE.with_suffix(".tmp")
    temporary_file.write_text(
        json.dumps(checkpoint, indent=2),
        encoding="utf-8"
    )
    temporary_file.replace(CHECKPOINT_FILE)


def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        return json.loads(
            CHECKPOINT_FILE.read_text(encoding="utf-8")
        )

    return {
        "next_url": URL,
        "page_number": 1,
    }


def load_existing_products():
    if not OUTPUT_FILE.exists():
        return set()

    with open(OUTPUT_FILE, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return {row["product_url"] for row in reader}


def save_product(book):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_exists = OUTPUT_FILE.exists() and OUTPUT_FILE.stat().st_size > 0

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)

        if not file_exists:
            writer.writeheader()

        writer.writerow(book)


def get_product_details(session, product_url):
    response = session.get(product_url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    product_info = {}

    for row in soup.select("table.table-striped tr"):
        key = row.select_one("th").get_text(strip=True)
        value = row.select_one("td").get_text(strip=True)
        product_info[key] = value

    breadcrumbs = soup.select("ul.breadcrumb li a")

    category = (
        breadcrumbs[-1].get_text(strip=True)
        if breadcrumbs else ""
    )

    description = ""
    description_heading = soup.select_one("#product_description")

    if description_heading:
        description_element = description_heading.find_next_sibling("p")
        if description_element:
            description = description_element.get_text(strip=True)

    return {
        "upc": product_info.get("UPC", ""),
        "availability": product_info.get("Availability", ""),
        "category": category,
        "description": description,
        "price_excl_tax": product_info.get("Price (excl. tax)", ""),
        "price_incl_tax": product_info.get("Price (incl. tax)", ""),
    }


def scrape_books():
    checkpoint = load_checkpoint()

    current_url = checkpoint["next_url"]
    page_number = checkpoint["page_number"]

    existing_products = load_existing_products()

    print(f"Existing products: {len(existing_products)}")

    with create_session() as session:
        while current_url:
            print(f"\nScraping page {page_number}")

            response = session.get(current_url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            products = soup.select("article.product_pod")

            for product in products:
                title_element = product.select_one("h3 a")

                product_url = urljoin(
                    response.url,
                    title_element["href"]
                )

                if product_url in existing_products:
                    continue

                title = title_element["title"]
                price = product.select_one(".price_color").get_text(strip=True)
                rating = product.select_one(".star-rating")["class"][1]

                details = get_product_details(session, product_url)

                book = {
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "product_url": product_url,
                    **details,
                }

                save_product(book)
                existing_products.add(product_url)

                print(f"[{len(existing_products)}] {title}")

                time.sleep(0.3)

            next_button = soup.select_one("li.next a")

            if next_button:
                next_url = urljoin(response.url, next_button["href"])
                save_checkpoint(next_url, page_number + 1)

                current_url = next_url
                page_number += 1
                time.sleep(1)
            else:
                current_url = None
                save_checkpoint(None, page_number + 1)

    print(f"\nScraping completed. Total: {len(existing_products)}")


if __name__ == "__main__":
    try:
        scrape_books()
    except requests.RequestException as error:
        print(f"\nNetwork error: {error}")
        print("Run the script again to resume.")
    except KeyboardInterrupt:
        print("\nInterrupted. Run again to resume.")
