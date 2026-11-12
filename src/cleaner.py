
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "products.csv"
OUTPUT_CSV = BASE_DIR / "data" / "products_clean.csv"
OUTPUT_EXCEL = BASE_DIR / "data" / "products.xlsx"

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def clean_price(value):
    if pd.isna(value):
        return None

    value = re.sub(r"[^\d.]", "", str(value))

    if not value:
        return None

    return float(value)


def extract_stock(value):
    if pd.isna(value):
        return 0

    match = re.search(r"\((\d+)\s+available\)", str(value))

    if match:
        return int(match.group(1))

    return 0


def clean_products():
    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    print(f"Original products: {len(df)}")

    # Remove duplicate products
    df = df.drop_duplicates(subset=["upc"])

    # Clean prices
    for column in ["price", "price_excl_tax", "price_incl_tax"]:
        df[column] = df[column].apply(clean_price)

    # Convert rating to numeric
    df["rating"] = df["rating"].map(RATING_MAP)

    # Extract stock quantity
    df["stock_quantity"] = df["availability"].apply(extract_stock)

    # Add currency
    df["currency"] = "GBP"

    # Save CSV
    df.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    # Save Excel
    df.to_excel(
        OUTPUT_EXCEL,
        index=False,
        engine="openpyxl"
    )

    print(f"Clean products: {len(df)}")
    print(f"CSV saved: {OUTPUT_CSV}")
    print(f"Excel saved: {OUTPUT_EXCEL}")


if __name__ == "__main__":
    clean_products()
