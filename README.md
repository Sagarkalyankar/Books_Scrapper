# Book Catalog Scraper

A Python web scraping project that collects book information from Books to Scrape and stores the cleaned data in a SQLite database.

## Features

- Scrapes multiple pages of book listings
- Extracts book title, price, rating, and stock status
- Cleans scraped price data
- Handles request failures with retry logic
- Uses rate limiting between requests
- Stores data in SQLite
- Performs a basic database query for the most expensive books

## Tech Stack

- Python
- Requests
- BeautifulSoup4
- SQLite
- Regular Expressions

## Installation

Clone the repository:

git clone YOUR_GITHUB_REPOSITORY_URL

Navigate into the project:

cd book-scraper

Install dependencies:

pip install -r requirements.txt

Run the scraper:

python book_scraper.py

## Output

The scraper creates a `books.db` SQLite database containing the scraped book information.

## Data Collected

- Title
- Price
- Rating
- Availability

## Target Website

https://books.toscrape.com/

This website is specifically designed for practicing web scraping.