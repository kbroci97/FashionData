#!/usr/bin/env python3
"""
Attempt to look up products on Saks Fifth Avenue and extract style number,
origin (where created), and primary fiber for each item in dresses.csv.

Note: Saks uses Datadome anti-bot protection, which blocks automated
requests. This script will try to fetch search results but will likely encounter
403 responses. It writes a CSV with the original columns plus the new fields.
"""

import csv
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote_plus

INPUT_CSV = 'dresses.csv'
OUTPUT_CSV = 'dresses_with_specs.csv'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}


def fetch_product_page(brand, product_name):
    """Search the site and return the first product page URL found (or None)."""
    # build search query combining brand and product name
    query = quote_plus(f"{brand} {product_name}")
    search_url = f'https://www.saksfifthavenue.com/search?searchTerm={query}'
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"Search blocked ({resp.status_code}) for {brand} - {product_name}")
            return None
        soup = BeautifulSoup(resp.content, 'html.parser')
        # look for first product link
        link = soup.select_one('a.productTileImageLink')
        if link and 'href' in link.attrs:
            return link['href']
    except Exception as e:
        print(f"Error during search request: {e}")
    return None


def scrape_product_specs(url):
    """Given a product page URL, attempt to scrape style number, origin, primary fiber."""
    # complete relative link
    if url.startswith('/'):
        url = 'https://www.saksfifthavenue.com' + url
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"Page fetch blocked ({resp.status_code}) for {url}")
            return {}, None
        soup = BeautifulSoup(resp.content, 'html.parser')
        specs = {}
        # common label patterns
        for row in soup.select('div.productDetailsKeySpecs label'):
            key = row.text.strip().lower()
            value = row.find_next_sibling('span')
            if not value:
                continue
            text = value.text.strip()
            if 'style' in key and 'number' in key:
                specs['Style Number'] = text
            elif 'made in' in key or 'country of origin' in key or 'origin' in key:
                specs['Origin'] = text
            elif 'fiber' in key or 'fabric' in key or 'content' in key:
                specs['Primary Fiber'] = text
        return specs, soup
    except Exception as e:
        print(f"Error scraping product page: {e}")
        return {}, None


def main():
    with open(INPUT_CSV, newline='', encoding='utf-8') as infile, \
            open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Style Number', 'Origin', 'Primary Fiber', 'Product URL']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            brand = row.get('Brand', '')
            product = row.get('Product Name', '')
            print(f"Looking up: {brand} - {product}")
            url = fetch_product_page(brand, product)
            if url:
                specs, _ = scrape_product_specs(url)
                row.update(specs)
                row['Product URL'] = url
            else:
                # leave specs blank
                pass
            writer.writerow(row)
            time.sleep(1)  # be polite

if __name__ == '__main__':
    main()
    print("Done writing", OUTPUT_CSV)
