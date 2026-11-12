
import json
from unittest.mock import Mock

from src import scraper


def test_get_product_details():
    html = """
    <html>
        <ul class="breadcrumb">
            <li><a href="/">Home</a></li>
            <li><a href="/books">Books</a></li>
            <li><a href="/fiction">Fiction</a></li>
        </ul>

        <table class="table-striped">
            <tr><th>UPC</th><td>ABC123</td></tr>
            <tr><th>Availability</th><td>In stock (12 available)</td></tr>
            <tr><th>Price (excl. tax)</th><td>£20.00</td></tr>
            <tr><th>Price (incl. tax)</th><td>£22.00</td></tr>
        </table>

        <div id="product_description"></div>
        <p>This is a sample book.</p>
    </html>
    """

    response = Mock()
    response.text = html
    response.raise_for_status = Mock()

    session = Mock()
    session.get.return_value = response

    result = scraper.get_product_details(
        session,
        "https://example.com/book"
    )

    assert result["upc"] == "ABC123"
    assert result["availability"] == "In stock (12 available)"
    assert result["category"] == "Fiction"
    assert result["description"] == "This is a sample book."
    assert result["price_excl_tax"] == "£20.00"
    assert result["price_incl_tax"] == "£22.00"

    session.get.assert_called_once_with(
        "https://example.com/book",
        timeout=15
    )


def test_get_product_details_without_description():
    html = """
    <html>
        <table class="table-striped">
            <tr><th>UPC</th><td>XYZ999</td></tr>
        </table>
    </html>
    """

    response = Mock()
    response.text = html

    session = Mock()
    session.get.return_value = response

    result = scraper.get_product_details(
        session,
        "https://example.com/book"
    )

    assert result["upc"] == "XYZ999"
    assert result["description"] == ""


def test_save_and_load_checkpoint(tmp_path, monkeypatch):
    checkpoint_file = tmp_path / "checkpoint.json"

    monkeypatch.setattr(scraper, "DATA_DIR", tmp_path)
    monkeypatch.setattr(
        scraper,
        "CHECKPOINT_FILE",
        checkpoint_file
    )

    scraper.save_checkpoint(
        "https://example.com/page-2",
        2
    )

    assert checkpoint_file.exists()

    data = json.loads(
        checkpoint_file.read_text(encoding="utf-8")
    )

    assert data["page_number"] == 2
    assert data["next_url"] == "https://example.com/page-2"

    loaded = scraper.load_checkpoint()

    assert loaded == data


def test_load_checkpoint_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(
        scraper,
        "CHECKPOINT_FILE",
        tmp_path / "missing.json"
    )

    result = scraper.load_checkpoint()

    assert result["next_url"] == scraper.URL
    assert result["page_number"] == 1


def test_save_product_and_load_existing(tmp_path, monkeypatch):
    output_file = tmp_path / "products.csv"

    monkeypatch.setattr(scraper, "DATA_DIR", tmp_path)
    monkeypatch.setattr(scraper, "OUTPUT_FILE", output_file)

    book = {
        field: "" for field in scraper.FIELDNAMES
    }

    book["title"] = "Test Book"
    book["product_url"] = "https://example.com/test-book"
    book["upc"] = "TEST123"

    scraper.save_product(book)

    assert output_file.exists()

    existing = scraper.load_existing_products()

    assert existing == {
        "https://example.com/test-book"
    }
