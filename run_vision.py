#!/usr/bin/env python3
"""
Vision-based competitor monitoring.
Uses screenshots + Claude Vision API to detect products.

Usage:
    python run_vision.py              # Run for all competitors
    python run_vision.py Condito      # Run for single brand
    python run_vision.py --skip-screenshot  # Analyze existing screenshots only

Requires:
    ANTHROPIC_API_KEY - Your Claude API key
    SCREENSHOTONE_API_KEY - Optional, for better screenshot service
"""
import os
import sys
import time
from pathlib import Path
from datetime import datetime

from config import COMPETITORS
from database import add_product_vision, log_scrape, init_db
from screenshot_service import capture_screenshot, SCREENSHOT_DIR
from vision_analyzer import analyze_screenshot

# Initialize database
init_db()


def process_brand(brand: str, config: dict, skip_screenshot: bool = False) -> tuple[int, int]:
    """
    Process a single brand: capture screenshot and analyze.
    Returns (total_products, new_products).
    """
    urls = config.get("urls", [])
    if not urls:
        status = config.get("status", "no_url")
        print(f"  {brand}: Skipped ({status})")
        return 0, 0

    # Use first URL (main product page)
    url = urls[0]
    print(f"\n{'='*50}")
    print(f"Processing: {brand}")
    print(f"URL: {url}")
    print(f"{'='*50}")

    # Step 1: Capture screenshot
    screenshot_path = None

    if not skip_screenshot:
        success, screenshot_path = capture_screenshot(brand, url)
        if not success:
            print(f"  Failed to capture screenshot")
            log_scrape(brand, 0, 0, "error", "Screenshot failed", method="vision")
            return 0, 0
    else:
        # Find most recent screenshot for this brand
        existing = sorted(SCREENSHOT_DIR.glob(f"{brand}_*.png"), reverse=True)
        if existing:
            screenshot_path = existing[0]
            print(f"  Using existing screenshot: {screenshot_path.name}")
        else:
            print(f"  No existing screenshot found for {brand}")
            return 0, 0

    # Step 2: Analyze with Vision API
    print(f"  Analyzing with Claude Vision...")
    products = analyze_screenshot(screenshot_path, brand)

    if not products:
        print(f"  No products detected")
        log_scrape(brand, 0, 0, "success", "No products found", method="vision")
        return 0, 0

    # Step 3: Save to database
    new_count = 0
    for prod in products:
        name = prod.get("name", "").strip()
        category = prod.get("category", "")

        if name:
            is_new = add_product_vision(brand, name, category)
            if is_new:
                new_count += 1
                print(f"  NEW: {name}")

    print(f"  Total: {len(products)} products, {new_count} new")
    log_scrape(brand, len(products), new_count, "success", method="vision")

    return len(products), new_count


def run_all(skip_screenshot: bool = False):
    """Process all competitors."""
    print("=" * 60)
    print("Vision-Based Competitor Monitor")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\nERROR: ANTHROPIC_API_KEY not set!")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    total_products = 0
    total_new = 0
    results = {}

    for brand, config in COMPETITORS.items():
        count, new = process_brand(brand, config, skip_screenshot)
        total_products += count
        total_new += new
        results[brand] = {"found": count, "new": new}
        time.sleep(1)  # Rate limiting

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total products detected: {total_products}")
    print(f"New products found: {total_new}")
    print("\nBy brand:")

    for brand, r in sorted(results.items(), key=lambda x: x[1]["found"], reverse=True):
        status = "✓" if r["found"] > 0 else "✗"
        new_marker = f" ({r['new']} NEW)" if r["new"] > 0 else ""
        print(f"  {status} {brand}: {r['found']} products{new_marker}")


def run_single(brand: str, skip_screenshot: bool = False):
    """Process single brand."""
    if brand not in COMPETITORS:
        print(f"Unknown brand: {brand}")
        print(f"Available: {', '.join(COMPETITORS.keys())}")
        return

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set!")
        return

    process_brand(brand, COMPETITORS[brand], skip_screenshot)


if __name__ == "__main__":
    skip_ss = "--skip-screenshot" in sys.argv

    # Remove flags from args
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if args:
        run_single(args[0], skip_screenshot=skip_ss)
    else:
        run_all(skip_screenshot=skip_ss)
