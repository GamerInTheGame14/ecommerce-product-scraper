# E-commerce Product Scraper

A Python-based web scraping tool that extracts product information from an online catalog, cleans the collected data, and exports it to CSV and Excel formats.

Built as a portfolio project to demonstrate practical skills in web scraping, data extraction, data processing, automated testing, and CI.

## Features

- Extract product information from multiple catalog pages
- Automatically follow pagination links
- Visit individual product pages for detailed information
- Extract product names, prices, ratings, categories, UPCs, stock availability, descriptions, and URLs
- Clean and normalize product data
- Remove duplicate products using UPC identifiers
- Export datasets to CSV and Excel
- Retry temporary HTTP failures
- Save progress and resume interrupted scraping
- Run automated tests using Pytest
- Execute tests automatically with GitHub Actions

## Technologies

- Python 3.11
- Requests
- BeautifulSoup4
- lxml
- Pandas
- OpenPyXL
- Pytest
- GitHub Actions

## Project Structure

```text
ecommerce-product-scraper/
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── src/
│   ├── scraper.py
│   └── cleaner.py
├── tests/
│   ├── test_cleaner.py
│   └── test_scraper.py
├── data/
├── .gitignore
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/GamerInTheGame14/ecommerce-product-scraper.git
cd ecommerce-product-scraper
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Scrape Products

```bash
python src/scraper.py
```

The scraper collects product information and saves it to:

`data/products.csv`

Progress is stored in:

`data/checkpoint.json`

If the process is interrupted, run the scraper again to resume.

To start a completely new scrape, back up or remove both the checkpoint and the raw products CSV before running it again.

### Step 2: Clean and Export Data

```bash
python src/cleaner.py
```

This generates:

- `data/products_clean.csv`
- `data/products.xlsx`

The cleaning process normalizes prices, converts ratings to numeric values, extracts stock quantities, and removes duplicate UPCs.

## Extracted Data

| Field          | Description               |
| -------------- | ------------------------- |
| title          | Product name              |
| price          | Product price             |
| rating         | Product rating            |
| product_url    | Product page URL          |
| upc            | Unique product identifier |
| availability   | Stock availability        |
| category       | Product category          |
| description    | Product description       |
| price_excl_tax | Price excluding tax       |
| price_incl_tax | Price including tax       |

The cleaned dataset also includes numeric stock quantities and a currency field.

## Automated Testing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
python -m pytest -v
```

The project includes 12 automated tests covering data cleaning, product detail extraction, checkpoint handling, and CSV persistence.

GitHub Actions runs the test suite automatically on pushes and pull requests targeting the main branch.

## Demo Website

This project uses [Books to Scrape](https://books.toscrape.com/), a public demonstration website designed for practicing web scraping.

The sample catalog contains approximately 1,000 products across 50 pages.

No login or paid API is required.

## Limitations

- The scraper is designed for the Books to Scrape HTML structure.
- Other websites may require different selectors or JavaScript rendering.
- Resume functionality skips previously collected product URLs; it does not automatically refresh existing records.
- The tool does not bypass authentication, CAPTCHA, or website access restrictions.

## Potential Applications

- Product catalog extraction
- Price comparison datasets
- Inventory research
- E-commerce data collection
- Product information analysis
- Data preparation for reporting

## Author

Python developer specializing in web scraping, automation, REST APIs, and data processing.

GitHub: https://github.com/GamerInTheGame14

## Disclaimer

This project is intended for educational and portfolio demonstration purposes. When adapting it to other websites, respect applicable terms, access restrictions, and reasonable request rates.
