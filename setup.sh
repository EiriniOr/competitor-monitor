#!/bin/bash
# Setup script for competitor monitor

cd "$(dirname "$0")"

echo "Setting up Competitor Monitor..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install playwright browsers
playwright install chromium

echo ""
echo "Setup complete!"
echo ""
echo "To run the dashboard:"
echo "  cd $(pwd)"
echo "  source venv/bin/activate"
echo "  streamlit run dashboard.py"
echo ""
echo "To run a manual scrape:"
echo "  python run_scrape.py"
