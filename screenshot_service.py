"""
Screenshot service for capturing competitor websites.
Uses Screenshotone API (free tier: 100 screenshots/month).
Alternative: Can also use local Playwright screenshots.
"""
import os
import time
import base64
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.parse import urlencode
import requests

# Directory to store screenshots
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


def get_screenshot_api_key():
    """Get API key from environment or Streamlit secrets."""
    key = os.environ.get("SCREENSHOTONE_API_KEY", "")
    if key:
        return key
    try:
        import streamlit as st
        return st.secrets.get("SCREENSHOTONE_API_KEY", "")
    except:
        return ""


SCREENSHOTONE_API_KEY = get_screenshot_api_key()


def get_screenshot_filename(brand: str, url: str) -> Path:
    """Generate unique filename for screenshot."""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    date_str = datetime.now().strftime("%Y%m%d")
    return SCREENSHOT_DIR / f"{brand}_{url_hash}_{date_str}.png"


def capture_with_screenshotone(url: str, output_path: Path) -> bool:
    """Capture screenshot using Screenshotone API."""
    if not SCREENSHOTONE_API_KEY:
        print("    No SCREENSHOTONE_API_KEY set, using Playwright fallback")
        return False

    params = {
        "access_key": SCREENSHOTONE_API_KEY,
        "url": url,
        "viewport_width": 1280,
        "viewport_height": 2000,
        "full_page": "true",
        "format": "png",
        "block_ads": "true",
        "block_cookie_banners": "true",
        "delay": 3,  # Wait for JS to render
    }

    api_url = f"https://api.screenshotone.com/take?{urlencode(params)}"

    try:
        response = requests.get(api_url, timeout=60)
        if response.status_code == 200:
            output_path.write_bytes(response.content)
            return True
        else:
            print(f"    Screenshotone error: {response.status_code}")
            return False
    except Exception as e:
        print(f"    Screenshotone error: {e}")
        return False


def capture_with_playwright(url: str, output_path: Path) -> bool:
    """Capture screenshot using local Playwright (fallback)."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 2000},
                locale="el-GR",
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            )
            page = context.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)  # Wait for JS
                page.screenshot(path=str(output_path), full_page=True)
                browser.close()
                return True
            except Exception as e:
                print(f"    Playwright error: {str(e)[:50]}")
                browser.close()
                return False

    except Exception as e:
        print(f"    Playwright not available: {e}")
        return False


def capture_screenshot(brand: str, url: str) -> tuple[bool, Path | None]:
    """
    Capture screenshot of URL.
    Returns (success, path_to_screenshot).
    """
    output_path = get_screenshot_filename(brand, url)

    print(f"  Capturing {brand}: {url}")

    # Try Screenshotone first (better at bypassing blocks)
    if SCREENSHOTONE_API_KEY:
        if capture_with_screenshotone(url, output_path):
            print(f"    Saved: {output_path.name}")
            return True, output_path

    # Fallback to Playwright
    if capture_with_playwright(url, output_path):
        print(f"    Saved: {output_path.name}")
        return True, output_path

    return False, None


def capture_all_competitors(competitors: dict) -> dict:
    """
    Capture screenshots for all competitor URLs.
    Returns dict of {brand: [screenshot_paths]}.
    """
    results = {}

    for brand, config in competitors.items():
        urls = config.get("urls", [])
        if not urls:
            continue

        results[brand] = []

        # Take screenshot of first URL only (main product page)
        url = urls[0]
        success, path = capture_screenshot(brand, url)

        if success and path:
            results[brand].append(path)

        time.sleep(2)  # Be polite between requests

    return results


def load_screenshot_as_base64(path: Path) -> str | None:
    """Load screenshot and encode as base64 for API."""
    if not path.exists():
        return None
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


if __name__ == "__main__":
    # Test single screenshot
    from config import COMPETITORS

    test_brand = "Condito"
    if test_brand in COMPETITORS:
        urls = COMPETITORS[test_brand].get("urls", [])
        if urls:
            success, path = capture_screenshot(test_brand, urls[0])
            print(f"Result: {success}, {path}")
