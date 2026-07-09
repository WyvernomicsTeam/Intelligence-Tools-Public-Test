# 🐉 Wyvernomics Web3 Growth Intelligence + Prospect Tool

**Internal tool for Wyvernomics Team** — Research Web3 projects + live demo of proprietary **Growth Intelligence Platform** (KOL Analytics, AI Narrative, On-chain + Smart Money data via CoinGecko + Dune + Nansen).

## Features

- **Discover** trending and search projects via CoinGecko
- **Growth Intelligence Platform** demo with:
  - KOL Analytics (SEA/APAC focused)
  - AI Narrative Scanner (uses real project data)
  - Whale Alerts & Smart Money Tracker
  - **Live On-chain charts** from CoinGecko
  - **Dune Analytics** integration (custom queries)
  - **Nansen Smart Money** integration (labeled smart money flows)
  - Fake Follower Detection
  - Community Analytics
  - Campaign Management & ROI simulator
- **Prospect Analyzer** with budget + platform fit scoring
- **Pitch Builder** with personalized outreach templates
- **Prospects Portfolio** tracking + CSV export

## Quick Start (Local)

```bash
git clone https://github.com/YOUR_USERNAME/wyvernomics-growth-intel.git
cd wyvernomics-growth-intel

python -m venv venv
source venv/bin/activate          # or venv\Scripts\activate on Windows

pip install -r requirements.txt
streamlit run wyvernomics_growth_intelligence_tool.py
```

App opens at `http://localhost:8501`

## Deployment (Recommended)

See full guide in [DEPLOYMENT.md](DEPLOYMENT.md)

**Fastest way to test:**
1. Push this repo to GitHub
2. Deploy on [Streamlit Community Cloud](https://share.streamlit.io)
3. Add your Dune + Nansen API keys in the app **Secrets** settings

## API Keys Setup

The tool works without keys (shows demo data), but for full power:

| Service     | Purpose                        | Cost     | Where to get          |
|-------------|--------------------------------|----------|-----------------------|
| CoinGecko   | Market, community, charts      | Free     | Auto (no key needed)  |
| Dune        | Custom on-chain queries        | Free tier| dune.com              |
| Nansen      | Labeled smart money intelligence | Paid   | Nansen dashboard      |

Add keys in sidebar or Streamlit Secrets.

## Project Structure

```
wyvernomics_growth_intelligence_tool.py   # Main Streamlit app
requirements.txt
DEPLOYMENT.md                             # How to deploy
README.md
.gitignore
.streamlit/
    secrets.toml.example
```

## Recommended Testing Flow

1. Deploy to Streamlit Cloud
2. Test with real Dune + Nansen keys
3. Share link with team for feedback
4. Then we continue adding features (better visualizations, saved queries, PDF export, etc.)

---

**Built for Wyvernomics** • SEA/APAC Web3 BD + KOL Acceleration • Data-driven growth

Ready to test? Let's get it deployed.
