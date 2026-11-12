
import pandas as pd

from src.cleaner import (
    clean_price,
    extract_stock,
    RATING_MAP,
)


def test_clean_price():
    assert clean_price("£51.77") == 51.77


def test_clean_price_without_currency():
    assert clean_price("25.50") == 25.50


def test_clean_price_empty():
    assert clean_price("") is None


def test_clean_price_nan():
    assert clean_price(float("nan")) is None


def test_extract_stock():
    assert extract_stock("In stock (22 available)") == 22


def test_extract_stock_empty():
    assert extract_stock("") == 0


def test_rating_conversion():
    assert RATING_MAP["One"] == 1
    assert RATING_MAP["Three"] == 3
    assert RATING_MAP["Five"] == 5
