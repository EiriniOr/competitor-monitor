# Competitor Product Monitor

Monitors competitor websites for new product launches using AI vision.

## Quick Start

### 1. Deploy Dashboard (Streamlit Cloud - Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in Settings > Secrets:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```

### 2. Enable Automated Scans (GitHub Actions - Free)

1. Go to your GitHub repo > Settings > Secrets > Actions
2. Add secret: `ANTHROPIC_API_KEY`
3. Scans run automatically on 1st and 15th of each month
4. Or trigger manually: Actions > Competitor Scan > Run workflow

## Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Run dashboard
streamlit run dashboard.py

# Run scan
python run_vision.py
```

## Cost

- Streamlit Cloud: Free
- GitHub Actions: Free (2000 min/month)
- Claude API: ~€1-2/month for 17 brands × 2 scans
