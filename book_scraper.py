"""
Book Catalog Scraper
---------------------
A end-to-end scraping project: fetches book listings, cleans the data,
and stores it in a SQLite database with basic error handling.

Target site: https://books.toscrape.com 

"""

import re
import sqlite3
import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
DB_PATH = "books.db"
HEADERS = {"User-Agent": "Mozilla/5.0 (educational scraping project)"}

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


@dataclass
class Book:
    title: str
    price: float
    rating: int
    in_stock: bool


def fetch_page(url: str) -> BeautifulSoup:
    """Fetch a page and return a parsed BeautifulSoup object with basic retry."""
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as e:
            print(f"  Request failed (attempt {attempt + 1}/3): {e}")
            time.sleep(2)
    raise RuntimeError(f"Failed to fetch {url} after 3 attempts")


def parse_books(soup: BeautifulSoup) -> list[Book]:
    """Extract and clean book data from a listing page."""
    books = []
    for article in soup.select("article.product_pod"):
        title = article.h3.a["title"].strip()

        price_text = article.select_one(".price_color").text
        price = float(re.sub(r"[^\d.]", "", price_text))  # strip currency symbol

        rating_class = article.select_one(".star-rating")["class"][1]
        rating = RATING_MAP.get(rating_class, 0)

        availability = article.select_one(".availability").text.strip()
        in_stock = "In stock" in availability

        books.append(Book(title=title, price=price, rating=rating, in_stock=in_stock))
    return books


def get_next_page_url(soup: BeautifulSoup, current_url: str) -> str | None:
    next_link = soup.select_one("li.next a")
    if not next_link:
        return None
    return current_url.rsplit("/", 1)[0] + "/" + next_link["href"]


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            rating INTEGER,
            in_stock INTEGER
        )
    """)
    conn.commit()


def save_books(conn: sqlite3.Connection, books: list[Book]) -> None:
    conn.executemany(
        "INSERT INTO books (title, price, rating, in_stock) VALUES (?, ?, ?, ?)",
        [(b.title, b.price, b.rating, int(b.in_stock)) for b in books],
    )
    conn.commit()


def scrape_all_pages(start_url: str, max_pages: int = 5) -> list[Book]:
    all_books = []
    url = start_url
    page_num = 1

    while url and page_num <= max_pages:
        print(f"Scraping page {page_num}: {url}")
        soup = fetch_page(url)
        page_books = parse_books(soup)
        all_books.extend(page_books)
        print(f"  Found {len(page_books)} books")

        url = get_next_page_url(soup, url)
        page_num += 1
        time.sleep(1)  # be polite — rate limit requests

    return all_books


def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    books = scrape_all_pages(BASE_URL, max_pages=5)
    save_books(conn, books)

    print(f"\nSaved {len(books)} books to {DB_PATH}")

    # quick sanity query
    cursor = conn.execute(
        "SELECT title, price, rating FROM books ORDER BY price DESC LIMIT 5"
    )
    print("\nTop 5 most expensive books scraped:")
    for title, price, rating in cursor.fetchall():
        print(f"  £{price:.2f} | {rating}★ | {title}")

    conn.close()


if __name__ == "__main__":
    main()