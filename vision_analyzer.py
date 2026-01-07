"""
Claude Vision API analyzer for extracting products from screenshots.
Uses Claude Haiku for cost efficiency (~$0.25 per 1000 images).
"""
import os
import json
import base64
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic


def get_api_key():
    """Get API key from environment or Streamlit secrets."""
    # Try environment variable first
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key

    # Try Streamlit secrets (for cloud deployment)
    try:
        import streamlit as st
        return st.secrets["ANTHROPIC_API_KEY"]
    except:
        return ""


ANTHROPIC_API_KEY = get_api_key()

# Use Haiku for cost efficiency
MODEL = "claude-3-5-haiku-latest"

EXTRACTION_PROMPT = """Analyze this screenshot of a food/condiment company's product page.

Extract ALL product names visible on this page. Focus on:
- Mayonnaise, ketchup, mustard, sauces, dressings, dips
- Salads (Russian salad, tzatziki, etc.)
- Any packaged food products

For each product, provide:
1. Product name (in the original language shown)
2. Category (sauce/dip/salad/condiment/other)

IMPORTANT:
- Only list actual products, NOT navigation items, menus, or page sections
- Include product variants (e.g., "Mayonnaise Light 500g", "Mayonnaise Classic 250g")
- If you see product packaging or labels, include those products

Return your response as a JSON array:
[
  {"name": "Product Name", "category": "sauce"},
  {"name": "Another Product", "category": "dip"}
]

If no products are visible, return an empty array: []
"""


def analyze_screenshot(image_path: Path, brand: str) -> list[dict]:
    """
    Analyze a screenshot using Claude Vision API.
    Returns list of products found.
    """
    if not ANTHROPIC_API_KEY:
        print("    Error: ANTHROPIC_API_KEY not set")
        return []

    if not image_path.exists():
        print(f"    Error: Screenshot not found: {image_path}")
        return []

    # Load and encode image
    image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")

    # Determine media type
    suffix = image_path.suffix.lower()
    media_type = "image/png" if suffix == ".png" else "image/jpeg"

    client = Anthropic(api_key=ANTHROPIC_API_KEY)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": f"Brand: {brand}\n\n{EXTRACTION_PROMPT}"
                        }
                    ],
                }
            ],
        )

        # Parse response
        response_text = response.content[0].text

        # Extract JSON from response
        try:
            # Try to find JSON array in response
            start = response_text.find("[")
            end = response_text.rfind("]") + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                products = json.loads(json_str)
                return products
            else:
                print(f"    No JSON found in response")
                return []
        except json.JSONDecodeError as e:
            print(f"    JSON parse error: {e}")
            return []

    except Exception as e:
        print(f"    API error: {e}")
        return []


def analyze_brand(brand: str, screenshot_paths: list[Path]) -> list[dict]:
    """
    Analyze all screenshots for a brand.
    Returns deduplicated list of products.
    """
    all_products = []
    seen_names = set()

    for path in screenshot_paths:
        print(f"  Analyzing {brand}: {path.name}")
        products = analyze_screenshot(path, brand)
        print(f"    Found {len(products)} products")

        for prod in products:
            name = prod.get("name", "").strip()
            if name and name.lower() not in seen_names:
                seen_names.add(name.lower())
                prod["brand"] = brand
                all_products.append(prod)

    return all_products


def batch_analyze(screenshots_by_brand: dict) -> dict:
    """
    Analyze screenshots for multiple brands.
    Returns {brand: [products]}.
    """
    results = {}

    for brand, paths in screenshots_by_brand.items():
        if paths:
            products = analyze_brand(brand, paths)
            results[brand] = products
            print(f"  {brand}: {len(products)} unique products")

    return results


if __name__ == "__main__":
    # Test with existing screenshot
    test_dir = Path(__file__).parent / "screenshots"
    if test_dir.exists():
        screenshots = list(test_dir.glob("*.png"))
        if screenshots:
            path = screenshots[0]
            brand = path.name.split("_")[0]
            print(f"Testing with: {path}")
            products = analyze_screenshot(path, brand)
            print(f"Found {len(products)} products:")
            for p in products[:10]:
                print(f"  - {p}")
