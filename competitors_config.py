"""
Loads competitor configuration from Streamlit secrets or local file.
Keeps competitor URLs private while code is public.
"""
import os
import json
from pathlib import Path


def load_competitors():
    """Load competitors from secrets (cloud) or local file (dev)."""

    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if "competitors" in st.secrets:
            return dict(st.secrets["competitors"])
    except:
        pass

    # Try environment variable (for GitHub Actions)
    env_config = os.environ.get("COMPETITORS_CONFIG")
    if env_config:
        try:
            return json.loads(env_config)
        except:
            pass

    # Fall back to local file (for development)
    local_file = Path(__file__).parent / "competitors_private.json"
    if local_file.exists():
        with open(local_file) as f:
            return json.load(f)

    # If nothing found, return empty
    print("WARNING: No competitor configuration found!")
    return {}


# Load on import
COMPETITORS = load_competitors()

# Database path
DB_PATH = "products.db"

# Scrape interval (days)
SCRAPE_INTERVAL = 15

# Request settings
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2
