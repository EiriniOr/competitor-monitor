"""
Configuration loader - imports from competitors_config.
Competitor URLs are stored privately in secrets, not in this public repo.
"""
from competitors_config import COMPETITORS, DB_PATH, SCRAPE_INTERVAL, REQUEST_TIMEOUT, REQUEST_DELAY

__all__ = ['COMPETITORS', 'DB_PATH', 'SCRAPE_INTERVAL', 'REQUEST_TIMEOUT', 'REQUEST_DELAY']
