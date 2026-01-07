"""
SQLite database for storing scraped products.
"""
import sqlite3
from datetime import datetime
from typing import Optional
from config import DB_PATH


def get_connection():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            name TEXT NOT NULL,
            url TEXT,
            image_url TEXT,
            first_seen DATE NOT NULL,
            last_seen DATE NOT NULL,
            is_new INTEGER DEFAULT 1,
            UNIQUE(brand, name)
        )
    """)

    # Scrape history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scrape_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            scrape_date DATETIME NOT NULL,
            products_found INTEGER DEFAULT 0,
            new_products INTEGER DEFAULT 0,
            status TEXT,
            error TEXT,
            method TEXT DEFAULT 'scrape'
        )
    """)

    # Add method column if not exists (for existing DBs)
    try:
        cursor.execute("ALTER TABLE scrape_log ADD COLUMN method TEXT DEFAULT 'scrape'")
    except:
        pass  # Column already exists

    # Add category column to products if not exists
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN category TEXT")
    except:
        pass

    conn.commit()
    conn.close()


def add_product(brand: str, name: str, url: Optional[str] = None,
                image_url: Optional[str] = None) -> bool:
    """
    Add or update product. Returns True if product is new.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date()

    # Check if product exists
    cursor.execute(
        "SELECT id, first_seen FROM products WHERE brand = ? AND name = ?",
        (brand, name)
    )
    existing = cursor.fetchone()

    if existing:
        # Update last_seen
        cursor.execute(
            "UPDATE products SET last_seen = ?, url = COALESCE(?, url), image_url = COALESCE(?, image_url) WHERE id = ?",
            (today, url, image_url, existing[0])
        )
        conn.commit()
        conn.close()
        return False
    else:
        # Insert new product
        cursor.execute(
            "INSERT INTO products (brand, name, url, image_url, first_seen, last_seen, is_new) VALUES (?, ?, ?, ?, ?, ?, 1)",
            (brand, name, url, image_url, today, today)
        )
        conn.commit()
        conn.close()
        return True


def log_scrape(brand: str, products_found: int, new_products: int,
               status: str = "success", error: Optional[str] = None,
               method: str = "scrape"):
    """Log scrape attempt."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO scrape_log (brand, scrape_date, products_found, new_products, status, error, method) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (brand, datetime.now(), products_found, new_products, status, error, method)
    )
    conn.commit()
    conn.close()


def add_product_vision(brand: str, name: str, category: str = None) -> bool:
    """
    Add product detected via vision analysis. Returns True if new.
    """
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date()

    # Check if product exists (fuzzy match - ignore case)
    cursor.execute(
        "SELECT id FROM products WHERE brand = ? AND LOWER(name) = LOWER(?)",
        (brand, name)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE products SET last_seen = ?, category = COALESCE(?, category) WHERE id = ?",
            (today, category, existing[0])
        )
        conn.commit()
        conn.close()
        return False
    else:
        cursor.execute(
            "INSERT INTO products (brand, name, category, first_seen, last_seen, is_new) VALUES (?, ?, ?, ?, ?, 1)",
            (brand, name, category, today, today)
        )
        conn.commit()
        conn.close()
        return True


def get_new_products(since_days: int = 15):
    """Get products first seen in the last N days."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT brand, name, url, image_url, first_seen
        FROM products
        WHERE first_seen >= date('now', ?)
        ORDER BY first_seen DESC, brand
    """, (f'-{since_days} days',))
    results = cursor.fetchall()
    conn.close()
    return results


def get_all_products():
    """Get all products."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT brand, name, url, image_url, first_seen, last_seen
        FROM products
        ORDER BY brand, name
    """)
    results = cursor.fetchall()
    conn.close()
    return results


def get_products_by_brand(brand: str):
    """Get all products for a brand."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, url, image_url, first_seen, last_seen
        FROM products
        WHERE brand = ?
        ORDER BY first_seen DESC
    """, (brand,))
    results = cursor.fetchall()
    conn.close()
    return results


def get_scrape_history(limit: int = 50):
    """Get recent scrape history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT brand, scrape_date, products_found, new_products, status, error
        FROM scrape_log
        ORDER BY scrape_date DESC
        LIMIT ?
    """, (limit,))
    results = cursor.fetchall()
    conn.close()
    return results


def mark_all_as_baseline():
    """Mark all current products as baseline (not new)."""
    conn = get_connection()
    cursor = conn.cursor()
    # Set first_seen to 30 days ago so they don't appear as "new"
    cursor.execute("UPDATE products SET first_seen = date('now', '-30 days')")
    conn.commit()
    conn.close()


def get_stats():
    """Get dashboard statistics."""
    conn = get_connection()
    cursor = conn.cursor()

    # Total products
    cursor.execute("SELECT COUNT(*) FROM products")
    total = cursor.fetchone()[0]

    # New products (last 15 days)
    cursor.execute("""
        SELECT COUNT(*) FROM products
        WHERE first_seen >= date('now', '-15 days')
    """)
    new = cursor.fetchone()[0]

    # Products per brand
    cursor.execute("""
        SELECT brand, COUNT(*) as cnt
        FROM products
        GROUP BY brand
        ORDER BY cnt DESC
    """)
    by_brand = cursor.fetchall()

    # Last scrape date
    cursor.execute("SELECT MAX(scrape_date) FROM scrape_log")
    last_scrape = cursor.fetchone()[0]

    conn.close()
    return {
        "total_products": total,
        "new_products_15d": new,
        "by_brand": by_brand,
        "last_scrape": last_scrape
    }


def mark_products_as_seen():
    """Mark all products as not new (after user views them)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET is_new = 0")
    conn.commit()
    conn.close()


# Initialize DB on import
init_db()
