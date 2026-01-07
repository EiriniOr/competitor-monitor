"""
Web scraper for competitor product pages.
Uses requests+BeautifulSoup for static sites, Playwright for JS-rendered.
"""
import re
import time
import hashlib
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import COMPETITORS, REQUEST_TIMEOUT, REQUEST_DELAY
from database import add_product, log_scrape

# Common user agent
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
}

# Words that indicate navigation/menu items, not products
SKIP_WORDS = {
    'home', 'αρχική', 'menu', 'μενού', 'contact', 'επικοινωνία',
    'about', 'σχετικά', 'careers', 'καριέρα', 'news', 'νέα',
    'history', 'ιστορία', 'philosophy', 'φιλοσοφία', 'quality', 'ποιότητα',
    'recipes', 'συνταγές', 'facebook', 'instagram', 'linkedin', 'youtube',
    'privacy', 'cookies', 'terms', 'copyright', 'newsletter',
    'login', 'register', 'cart', 'checkout', 'search', 'αναζήτηση',
    'all rights reserved', 'open menu', 'close menu',
}

# Minimum product name length
MIN_NAME_LENGTH = 4
MAX_NAME_LENGTH = 100


def is_valid_product_name(name: str) -> bool:
    """Check if name looks like a real product, not navigation."""
    if not name or len(name) < MIN_NAME_LENGTH or len(name) > MAX_NAME_LENGTH:
        return False

    name_lower = name.lower().strip()

    # Skip if it's a known navigation word
    for skip in SKIP_WORDS:
        if name_lower == skip or name_lower.startswith(skip + ' '):
            return False

    # Skip if too many uppercase letters (likely acronym/menu)
    if len(name) > 5 and sum(1 for c in name if c.isupper()) / len(name) > 0.7:
        return False

    # Skip if contains typical menu patterns
    menu_patterns = [
        r'^(en|el|ru)\s*$',  # Language codes
        r'^\d+$',  # Just numbers
        r'^[→←↓↑»«]+',  # Arrows
        r'\|{2,}',  # Multiple pipes
        r'^(view|see|read|click|learn)\s+(all|more)',
    ]
    for pattern in menu_patterns:
        if re.search(pattern, name_lower):
            return False

    return True


def clean_text(text: str) -> str:
    """Clean extracted text."""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove leading/trailing punctuation
    text = re.sub(r'^[\-–—:]+|[\-–—:]+$', '', text).strip()
    return text


def get_page_content(url: str, use_playwright: bool = False,
                     headers: dict = None) -> Optional[str]:
    """Fetch page HTML content."""
    if use_playwright:
        return get_page_playwright(url)

    try:
        req_headers = {**DEFAULT_HEADERS, **(headers or {})}
        response = requests.get(url, headers=req_headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"    Error fetching {url}: {e}")
        return None


def get_page_playwright(url: str) -> Optional[str]:
    """Fetch page using Playwright for JS-rendered content."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=DEFAULT_HEADERS["User-Agent"],
                locale="el-GR"
            )
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            # Wait for dynamic content
            page.wait_for_timeout(3000)
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        print(f"    Playwright error: {str(e)[:100]}")
        return None


def extract_products(html: str, config: dict, base_url: str) -> list:
    """Extract products using CSS selectors from config."""
    products = []
    soup = BeautifulSoup(html, 'lxml')

    product_sel = config.get("product_selector", "")
    name_sel = config.get("name_selector", "")
    image_sel = config.get("image_selector", "")
    link_sel = config.get("link_selector", "")

    if not product_sel:
        return []

    # Find product containers
    elements = soup.select(product_sel)

    if not elements:
        # Fallback selectors
        fallback = ['article', '.product', '.item', '[class*="product"]']
        for sel in fallback:
            elements = soup.select(sel)
            if elements:
                break

    seen_names = set()

    for elem in elements[:100]:  # Limit to prevent noise
        # Extract name
        name = ""
        for sel in name_sel.split(", "):
            if sel:
                name_elem = elem.select_one(sel)
                if name_elem:
                    name = clean_text(name_elem.get_text())
                    if is_valid_product_name(name):
                        break
                    name = ""

        # If no name from selectors, try element text
        if not name:
            direct_text = clean_text(elem.get_text()[:150])
            # Take first meaningful part
            parts = re.split(r'[|·•]', direct_text)
            for part in parts:
                part = clean_text(part)
                if is_valid_product_name(part):
                    name = part
                    break

        if not name or name.lower() in seen_names:
            continue

        seen_names.add(name.lower())

        # Extract URL
        url = None
        for sel in link_sel.split(", "):
            if sel:
                link = elem.select_one(sel)
                if link:
                    href = link.get('href', '')
                    if href and not href.startswith('#') and not href.startswith('javascript:'):
                        url = urljoin(base_url, href)
                        break
        if not url:
            link = elem.select_one('a[href]')
            if link:
                href = link.get('href', '')
                if href and not href.startswith('#'):
                    url = urljoin(base_url, href)

        # Extract image
        image_url = None
        for sel in image_sel.split(", "):
            if sel:
                img = elem.select_one(sel)
                if img:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if src:
                        image_url = urljoin(base_url, src)
                        break
        if not image_url:
            img = elem.select_one('img')
            if img:
                src = img.get('src') or img.get('data-src')
                if src:
                    image_url = urljoin(base_url, src)

        products.append({
            "name": name,
            "url": url,
            "image_url": image_url
        })

    return products


def scrape_brand(brand: str, config: dict) -> tuple[int, int]:
    """Scrape products for a single brand. Returns (total, new) count."""
    urls = config.get("urls", [])

    # Handle legacy single URL format
    if not urls and config.get("url"):
        urls = [config["url"]]

    if not urls:
        status = config.get("status", "no_url")
        print(f"  {brand}: Skipped ({status})")
        log_scrape(brand, 0, 0, "skipped", status)
        return 0, 0

    needs_js = config.get("needs_js", False)
    custom_headers = config.get("headers", {})

    all_products = []
    errors = []

    for url in urls:
        print(f"  {brand}: {url}")
        try:
            html = get_page_content(url, use_playwright=needs_js, headers=custom_headers)
            if not html:
                errors.append(f"Failed to fetch {url}")
                continue

            products = extract_products(html, config, url)
            all_products.extend(products)
            print(f"    Found {len(products)} products")

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            errors.append(str(e)[:100])
            print(f"    Error: {str(e)[:100]}")

    # Deduplicate across URLs
    seen = set()
    unique_products = []
    for p in all_products:
        key = p["name"].lower()
        if key not in seen:
            seen.add(key)
            unique_products.append(p)

    # Save to database
    new_count = 0
    for prod in unique_products:
        is_new = add_product(
            brand=brand,
            name=prod["name"],
            url=prod.get("url"),
            image_url=prod.get("image_url")
        )
        if is_new:
            new_count += 1
            print(f"    NEW: {prod['name']}")

    status = "success" if not errors else "partial"
    error_msg = "; ".join(errors) if errors else None
    log_scrape(brand, len(unique_products), new_count, status, error_msg)

    return len(unique_products), new_count


def scrape_all():
    """Scrape all configured competitor websites."""
    print("=" * 60)
    print("Starting competitor product scrape")
    print("=" * 60)

    total_products = 0
    total_new = 0
    results = {}

    for brand, config in COMPETITORS.items():
        count, new = scrape_brand(brand, config)
        total_products += count
        total_new += new
        results[brand] = {"found": count, "new": new}
        time.sleep(1)

    print("=" * 60)
    print(f"Scrape complete: {total_products} products, {total_new} new")
    print("=" * 60)

    # Summary
    print("\nSummary by brand:")
    for brand, r in sorted(results.items(), key=lambda x: x[1]["found"], reverse=True):
        status = "✓" if r["found"] > 0 else "✗"
        print(f"  {status} {brand}: {r['found']} products ({r['new']} new)")

    return total_products, total_new


def scrape_single(brand: str):
    """Scrape a single brand."""
    if brand not in COMPETITORS:
        print(f"Unknown brand: {brand}")
        print(f"Available: {', '.join(COMPETITORS.keys())}")
        return 0, 0

    return scrape_brand(brand, COMPETITORS[brand])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        scrape_single(sys.argv[1])
    else:
        scrape_all()
