# 🚀 Deployment Guide for Wyvernomics Growth Intelligence Tool

This guide helps you deploy the tool quickly for testing and internal use.

## Recommended: Streamlit Community Cloud (Fastest for Testing)

This is the **easiest and recommended** way to get the app live in under 5 minutes.

### Step-by-step

1. **Create a GitHub repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Wyvernomics Growth Intelligence Tool"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/wyvernomics-growth-intel.git
   git push -u origin main
   ```

2. **Go to [share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.

3. **Click "New app"**
   - Repository: Select your new repo
   - Branch: `main`
   - Main file path: `wyvernomics_growth_intelligence_tool.py`
   - Click **Deploy**

4. **Add Secrets (Important)**
   After the first deploy, go to the app settings → **Secrets** and paste something like this:

   ```toml
   [dune]
   api_key = "dune_xxxxxxxxxxxx"

   [nansen]
   api_key = "nansen_xxxxxxxxxxxx"
   ```

   Then restart the app.

### After Deployment

- The app will be live at `https://YOUR-APP-NAME.streamlit.app`
- You can share the link with your team for testing
- Every push to `main` will auto-redeploy

---

## Alternative Deployment Options

| Platform              | Free Tier | Difficulty | Best For                  | Notes |
|-----------------------|-----------|------------|---------------------------|-------|
| **Streamlit Cloud**   | Yes       | Very Easy  | Testing + Internal        | Recommended starting point |
| **Hugging Face Spaces** | Yes     | Easy       | Public demos              | Good alternative |
| **Render.com**        | Yes       | Medium     | More control              | Supports Docker |
| **Railway**           | Yes       | Medium     | Full-stack later          | Nice UI |
| **Docker + VPS**      | No        | Advanced   | Production                | Full control |

---

## Local Testing Before Deploying

```bash
# 1. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run wyvernomics_growth_intelligence_tool.py
```

The app will open at `http://localhost:8501`

---

## Handling API Keys Securely

- **Never** commit real API keys to GitHub.
- Use `.streamlit/secrets.toml` locally (already in `.gitignore`).
- Use Streamlit Cloud **Secrets** manager when deployed.
- The app already handles missing keys gracefully (shows demo data + instructions).

---

## Recommended Testing Flow

1. Deploy to Streamlit Cloud (as above)
2. Test with your real Dune + Nansen keys
3. Share the link with 1-2 team members for feedback
4. Once stable, we can add more features (more Nansen endpoints, better visualizations, user accounts, etc.)

---

## Next Recommended Improvements (After Testing)

- Better error handling for API rate limits
- Caching of Dune/Nansen results
- Ability to save favorite queries
- Dark mode / improved UI
- Export intelligence reports as PDF

Let me know when you're ready to continue building after testing!
