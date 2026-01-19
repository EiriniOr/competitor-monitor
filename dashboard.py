"""
Streamlit dashboard for competitor product monitoring.
Run with: streamlit run dashboard.py
"""
import os
import subprocess
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

from database import (
    get_stats, get_new_products, get_all_products,
    get_products_by_brand, get_scrape_history, mark_all_as_baseline
)
from config import COMPETITORS

# Page config
st.set_page_config(
    page_title="Competitor Monitor",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Competitor Product Monitor")

# Check API key status (env vars or Streamlit secrets)
def get_secret(key):
    """Get secret from env var or Streamlit secrets."""
    val = os.environ.get(key)
    if val:
        return val
    try:
        return st.secrets[key]
    except:
        return ""

has_anthropic_key = bool(get_secret("ANTHROPIC_API_KEY"))
has_screenshot_key = bool(get_secret("SCREENSHOTONE_API_KEY"))

# Sidebar
st.sidebar.header("Actions")

# Vision-based scan (recommended)
st.sidebar.subheader("📸 Vision Analysis")
if not has_anthropic_key:
    st.sidebar.warning("Set ANTHROPIC_API_KEY to enable")
else:
    if st.sidebar.button("🔍 Run Vision Scan", type="primary", help="Uses Claude Vision API"):
        with st.spinner("Capturing screenshots and analyzing with AI..."):
            # Pass secrets as env vars to subprocess
            env = os.environ.copy()
            env["ANTHROPIC_API_KEY"] = get_secret("ANTHROPIC_API_KEY")
            if get_secret("SCREENSHOTONE_API_KEY"):
                env["SCREENSHOTONE_API_KEY"] = get_secret("SCREENSHOTONE_API_KEY")

            result = subprocess.run(
                ["python", "run_vision.py"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
                env=env,
                timeout=300  # 5 min timeout
            )
            if result.returncode == 0:
                st.sidebar.success("Vision scan complete!")
                if result.stdout:
                    st.expander("Output").code(result.stdout[-2000:])
            else:
                st.sidebar.error(f"Error: {result.stderr[:500] if result.stderr else 'Unknown error'}")
        st.rerun()

st.sidebar.divider()

# Legacy scraper
st.sidebar.subheader("🕷️ Traditional Scraper")
if st.sidebar.button("Run HTML Scraper", help="Pattern-based scraping (less accurate)"):
    with st.spinner("Scraping competitor sites..."):
        result = subprocess.run(
            ["python", "run_scrape.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
    st.sidebar.success("Scrape complete!")
    st.rerun()

# Single brand scan
st.sidebar.divider()
st.sidebar.subheader("Single Brand")
selected_brand = st.sidebar.selectbox(
    "Select brand:",
    options=[""] + list(COMPETITORS.keys())
)
if selected_brand:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("📸 Vision"):
            with st.spinner(f"Analyzing {selected_brand}..."):
                env = os.environ.copy()
                env["ANTHROPIC_API_KEY"] = get_secret("ANTHROPIC_API_KEY")
                if get_secret("SCREENSHOTONE_API_KEY"):
                    env["SCREENSHOTONE_API_KEY"] = get_secret("SCREENSHOTONE_API_KEY")
                subprocess.run(
                    ["python", "run_vision.py", selected_brand],
                    cwd=Path(__file__).parent,
                    env=env,
                    timeout=120
                )
            st.rerun()
    with col2:
        if st.button("🕷️ Scrape"):
            with st.spinner(f"Scraping {selected_brand}..."):
                subprocess.run(
                    ["python", "-c", f"from scraper import scrape_single; scrape_single('{selected_brand}')"],
                    cwd=Path(__file__).parent
                )
            st.rerun()

# Facebook quick links
st.sidebar.divider()
with st.sidebar.expander("📱 Facebook Pages"):
    for brand, config in COMPETITORS.items():
        social = config.get("social", [])
        if social:
            st.markdown(f"[{brand}]({social[0]})")

# Manual check links (brands that can't be auto-scanned)
with st.sidebar.expander("🔗 Manual Check"):
    st.caption("These brands need manual checking:")
    for brand, config in COMPETITORS.items():
        status = config.get("status", "")
        if status in ["maintenance", "server_blocking", "no_website", "url_not_found"]:
            website = config.get("website", "")
            social = config.get("social", [])
            link = website or (social[0] if social else "")
            if link:
                st.markdown(f"[{brand}]({link})")

# Stats
stats = get_stats()

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Products", stats["total_products"])
with col2:
    st.metric("New (Last 15 Days)", stats["new_products_15d"])
with col3:
    st.metric("Brands Tracked", len(COMPETITORS))
with col4:
    last_scan = stats["last_scrape"]
    if last_scan:
        st.metric("Last Scan", last_scan[:10])
    else:
        st.metric("Last Scan", "Never")

# API Status
with st.expander("🔑 API Status"):
    col1, col2 = st.columns(2)
    with col1:
        if has_anthropic_key:
            st.success("✓ ANTHROPIC_API_KEY set")
        else:
            st.error("✗ ANTHROPIC_API_KEY not set")
            st.code("export ANTHROPIC_API_KEY='your-key'")
    with col2:
        if has_screenshot_key:
            st.success("✓ SCREENSHOTONE_API_KEY set")
        else:
            st.info("ℹ Screenshotone not set (using Playwright fallback)")

st.divider()

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🆕 New Products", "📦 All Products", "📊 By Brand", "📸 Screenshots", "📋 Scan Log"
])

with tab1:
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.header("🆕 New Products (Last 15 Days)")
    with col_h2:
        if st.button("Mark all as seen", help="Clear baseline - only truly new products will show after next scan"):
            mark_all_as_baseline()
            st.success("Baseline set! Next scan will only show new products.")
            st.rerun()

    # New products (0-15 days)
    new_products = get_new_products(15)

    if new_products:
        df = pd.DataFrame(new_products, columns=["Brand", "Product", "URL", "Image", "First Seen"])
        df["First Seen"] = pd.to_datetime(df["First Seen"])

        for brand in df["Brand"].unique():
            brand_df = df[df["Brand"] == brand]
            st.subheader(f"{brand} ({len(brand_df)} new)")

            for _, row in brand_df.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    if row["URL"]:
                        st.markdown(f"🆕 [{row['Product']}]({row['URL']})")
                    else:
                        st.write(f"🆕 {row['Product']}")
                with col2:
                    st.caption(row["First Seen"].strftime("%Y-%m-%d"))

        st.download_button(
            "📥 Export New Products CSV",
            df.to_csv(index=False),
            "new_products.csv",
            "text/csv"
        )
    else:
        st.info("No new products in the last 15 days.")

    # Recent products (15-60 days)
    st.divider()
    st.subheader("📋 Recent Products (15-60 days ago)")

    recent_products = get_new_products(60)
    if recent_products:
        df_recent = pd.DataFrame(recent_products, columns=["Brand", "Product", "URL", "Image", "First Seen"])
        df_recent["First Seen"] = pd.to_datetime(df_recent["First Seen"])
        # Filter to 15-60 days only
        cutoff_15 = pd.Timestamp.now() - pd.Timedelta(days=15)
        df_recent = df_recent[df_recent["First Seen"] < cutoff_15]

        if not df_recent.empty:
            for brand in df_recent["Brand"].unique():
                brand_df = df_recent[df_recent["Brand"] == brand]
                with st.expander(f"{brand} ({len(brand_df)} products)"):
                    for _, row in brand_df.iterrows():
                        st.write(f"• {row['Product']} ({row['First Seen'].strftime('%Y-%m-%d')})")
        else:
            st.caption("No products from 15-60 days ago.")
    else:
        st.caption("No recent products.")

with tab2:
    st.header("All Tracked Products")

    all_products = get_all_products()
    if all_products:
        df = pd.DataFrame(all_products, columns=["Brand", "Product", "URL", "Image", "First Seen", "Last Seen"])

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            brand_filter = st.multiselect("Filter by brand:", df["Brand"].unique())
        with col2:
            search = st.text_input("Search products:", "")

        filtered_df = df.copy()
        if brand_filter:
            filtered_df = filtered_df[filtered_df["Brand"].isin(brand_filter)]
        if search:
            filtered_df = filtered_df[filtered_df["Product"].str.contains(search, case=False, na=False)]

        st.dataframe(
            filtered_df[["Brand", "Product", "First Seen", "Last Seen"]],
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "📥 Export CSV",
            filtered_df.to_csv(index=False),
            "all_products.csv",
            "text/csv"
        )
    else:
        st.info("No products in database. Run a scan first.")

with tab3:
    st.header("Products by Brand")

    brand = st.selectbox("Select brand:", list(COMPETITORS.keys()), key="brand_tab")

    if brand:
        config = COMPETITORS[brand]
        col1, col2 = st.columns(2)
        with col1:
            urls = config.get("urls", [])
            if urls:
                st.markdown(f"**Website:** [{urls[0]}]({urls[0]})")
            else:
                st.write("**Website:** Not configured")
        with col2:
            social = config.get("social", [])
            if social:
                st.markdown(f"**Social:** [Facebook]({social[0]})")

        products = get_products_by_brand(brand)
        if products:
            df = pd.DataFrame(products, columns=["Product", "URL", "Image", "First Seen", "Last Seen"])
            st.dataframe(df[["Product", "First Seen", "Last Seen"]], use_container_width=True, hide_index=True)
        else:
            st.info(f"No products found for {brand}. Run a scan.")

with tab4:
    st.header("Screenshots")

    screenshot_dir = Path(__file__).parent / "screenshots"
    if screenshot_dir.exists():
        screenshots = sorted(screenshot_dir.glob("*.png"), reverse=True)

        if screenshots:
            # Group by brand
            brands_with_screenshots = {}
            for ss in screenshots:
                brand = ss.name.split("_")[0]
                if brand not in brands_with_screenshots:
                    brands_with_screenshots[brand] = []
                brands_with_screenshots[brand].append(ss)

            selected = st.selectbox(
                "View brand:",
                options=list(brands_with_screenshots.keys())
            )

            if selected and brands_with_screenshots[selected]:
                latest = brands_with_screenshots[selected][0]
                st.image(str(latest), caption=f"{selected} - {latest.name}")
        else:
            st.info("No screenshots yet. Run a Vision scan to capture.")
    else:
        st.info("Screenshots directory not found.")

with tab5:
    st.header("Scan History")

    history = get_scrape_history(100)
    if history:
        # Check if method column exists
        if len(history[0]) >= 6:
            df = pd.DataFrame(history, columns=["Brand", "Date", "Found", "New", "Status", "Error"])
        else:
            df = pd.DataFrame(history, columns=["Brand", "Date", "Found", "New", "Status", "Error", "Method"])

        df["Date"] = pd.to_datetime(df["Date"])

        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Scans", len(df))
        with col2:
            st.metric("Successful", len(df[df["Status"] == "success"]))
        with col3:
            st.metric("Failed", len(df[df["Status"] == "error"]))

        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No scan history yet.")

# Footer
st.divider()
st.caption("Competitor Product Monitor | Run Vision scans on 1st and 15th of each month")
