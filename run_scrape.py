#!/usr/bin/env python3
"""
Run competitor scrape. Use with cron or launchd for scheduling.
"""
import sys
import os

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from scraper import scrape_all, scrape_single

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Scrape specific brand
        brand = sys.argv[1]
        print(f"Scraping single brand: {brand}")
        scrape_single(brand)
    else:
        # Scrape all
        scrape_all()
