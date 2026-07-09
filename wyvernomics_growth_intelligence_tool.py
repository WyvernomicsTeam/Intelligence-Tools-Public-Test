#!/usr/bin/env python3
"""
Wyvernomics Web3 Growth Intelligence & Prospect Tool
Updated v2 - Now includes full demo of the Web3 Growth Intelligence Platform
combining KOL Analytics, On-chain/User Analytics, AI Narrative Tracking,
Whale/Smart Money Alerts, Fake Follower Detection, Community Analytics & Campaign Management.

A Streamlit dashboard for:
- Researching upcoming Web3 projects (valuation, hiring signals, budget fit)
- Demoing the proprietary Growth Intelligence Platform to prospects
- Generating tailored pitches for KOL packages, BD subscriptions, Talent, AND the new Platform subscription
- Tracking prospects pipeline
"""

import streamlit as st
from coingecko_sdk import Coingecko, APIError
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import urllib.parse
import random
import requests
from typing import Optional, Dict, Any, List

# ------------------ CONFIG & INIT ------------------
st.set_page_config(
    page_title="Wyvernomics | Growth Intelligence + BD",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (dragon/gold theme + new intel cards)
st.markdown("""
<style>
    .main-header { font-size: 2.1rem; font-weight: 700; color: #D4AF37; }
    .sub-header { font-size: 1.05rem; color: #555; }
    .metric-card { background-color: #f8f9fa; padding: 1rem; border-radius: 10px; border-left: 4px solid #D4AF37; }
    .section-header { color: #D4AF37; border-bottom: 2px solid #D4AF37; padding-bottom: 0.3rem; }
    .pitch-box { background-color: #fffbeb; padding: 1.5rem; border-radius: 12px; border: 1px solid #D4AF37; }
    .intel-card { background-color: #0f172a; color: #e2e8f0; padding: 1.2rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1rem; }
    .warning-box { background-color: #fff3cd; padding: 0.8rem; border-radius: 8px; }
    .success-box { background-color: #d1fae5; padding: 0.8rem; border-radius: 8px; border-left: 4px solid #10b981; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: 600; }
    .stButton>button:hover { background-color: #B8860B; color: white; }
    .platform-badge { background-color: #1e3a8a; color: #bfdbfe; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_cg_client() -> Coingecko:
    return Coingecko()

client = get_cg_client()

PROSPECTS_FILE = "wyvernomics_prospects.json"

# ==================== PRICING (Updated with new Platform) ====================
KOL_PRICING = {
    "Pilot Package": {
        "price": "$2,999 - $3,499",
        "desc": "Low-risk entry with 20 best KOLs (SEA & APAC focused). Full management. Measurable results + learnings in 2-3 weeks.",
        "best_for": "Early-stage projects testing traction"
    },
    "Custom KOL Package": {
        "price": "From $100/KOL (min)",
        "desc": "Fully customizable number of KOLs, management level. SEA & APAC authentic local reach.",
        "best_for": "Targeted campaigns or scaling proven pilots"
    },
    "Gold Subscription (BD)": {
        "price": "$5,000 - $6,000 / month",
        "desc": "7-8 dedicated BD team members. Weekly reports, deck creation, negotiation support, event access (TBD).",
        "best_for": "Projects ready for CEX listings, L1/L2 integrations, B2B alliances"
    },
    "Silver Subscription (BD)": {
        "price": "$2,500 - $3,000 / month",
        "desc": "4-5 dedicated BD team members. Weekly reports + deck creation.",
        "best_for": "Foundational pipeline building"
    }
}

# NEW: Web3 Growth Intelligence Platform Subscription (from team discussion)
PLATFORM_PRICING = {
    "Growth Intelligence Platform": {
        "price": "$299 - $999 / month",
        "desc": "Proprietary Web3 Growth Intelligence Platform. Includes KOL Analytics, On-chain User Analytics, AI Narrative Tracker, Whale & Smart Money Alerts, Fake Follower Detection, Community Analytics, Campaign Management & ROI tracking. SEA/APAC data depth.",
        "best_for": "Projects that want data-driven GTM, better KOL ROI, and real user insights (not just vanity metrics)"
    },
    "Platform + KOL Pilot Bundle": {
        "price": "$3,499 - $4,299 (one-time + platform access)",
        "desc": "KOL Pilot execution + 3 months full access to the Growth Intelligence Platform. Best value for projects that want both immediate traction AND the tools to measure & optimize it.",
        "best_for": "Projects ready to move fast and learn from real data"
    }
}

def save_prospects(prospects: List[Dict]):
    try:
        with open(PROSPECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(prospects, f, indent=2, default=str)
    except Exception as e:
        st.error(f"Could not save prospects: {e}")

def load_prospects() -> List[Dict]:
    if os.path.exists(PROSPECTS_FILE):
        try:
            with open(PROSPECTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

# ==================== MOCK DATA FOR GROWTH INTELLIGENCE PLATFORM ====================

def get_sample_kols() -> pd.DataFrame:
    """SEA & APAC focused sample KOL data for demo"""
    data = [
        {"handle": "@indogaming_kol", "name": "Indo Gaming KOL", "followers": 187000, "eng_rate": 5.8, "fake_pct": 9, "niche": "Gaming, NFT, Web3", "country": "Indonesia", "recent_roi": "4.1x", "last_campaign": "2 days ago"},
        {"handle": "@sg_defi_alpha", "name": "SG DeFi Alpha", "followers": 92000, "eng_rate": 4.9, "fake_pct": 14, "niche": "DeFi, Layer2, RWA", "country": "Singapore", "recent_roi": "2.8x", "last_campaign": "5 days ago"},
        {"handle": "@vn_crypto_guru", "name": "Vietnam Crypto Guru", "followers": 245000, "eng_rate": 3.7, "fake_pct": 22, "niche": "Layer1, Memecoin, CEX", "country": "Vietnam", "recent_roi": "5.3x", "last_campaign": "Yesterday"},
        {"handle": "@thailand_web3", "name": "Thailand Web3 Hub", "followers": 78000, "eng_rate": 6.2, "fake_pct": 7, "niche": "Gaming, SocialFi, DePIN", "country": "Thailand", "recent_roi": "3.9x", "last_campaign": "1 week ago"},
        {"handle": "@ph_crypto_queen", "name": "PH Crypto Queen", "followers": 134000, "eng_rate": 5.1, "fake_pct": 11, "niche": "NFT, Metaverse, AI x Crypto", "country": "Philippines", "recent_roi": "3.4x", "last_campaign": "3 days ago"},
        {"handle": "@my_web3_insider", "name": "MY Web3 Insider", "followers": 61000, "eng_rate": 7.4, "fake_pct": 5, "niche": "DeFi, Infrastructure, BD", "country": "Malaysia", "recent_roi": "4.7x", "last_campaign": "4 days ago"},
        {"handle": "@sea_kol_collective", "name": "SEA KOL Collective", "followers": 156000, "eng_rate": 4.3, "fake_pct": 16, "niche": "Multi-niche, Cross-border", "country": "Regional", "recent_roi": "2.9x", "last_campaign": "6 days ago"},
        {"handle": "@jakarta_defi", "name": "Jakarta DeFi Daily", "followers": 88000, "eng_rate": 5.5, "fake_pct": 8, "niche": "DeFi, RWA, Stablecoin", "country": "Indonesia", "recent_roi": "3.6x", "last_campaign": "Today"},
    ]
    return pd.DataFrame(data)

def mock_ai_narrative_scan(keyword: str, real_description: str = "") -> Dict[str, Any]:
    """Simple rule-based narrative scanner (demo). Enhanced with real CoinGecko description when available."""
    kw = keyword.lower().strip()
    desc = real_description.lower() if real_description else ""
    
    if not kw:
        return {"score": 0, "sentiment": "N/A", "narratives": [], "insight": "Enter a project name or narrative keyword to scan."}
    
    base = {
        "score": 58,
        "sentiment": "Neutral",
        "narratives": ["General Web3", "Infrastructure", "Adoption"],
        "insight": "Narrative is broad. Needs sharper positioning. AI Narrative Tracker suggests combining with trending meta (AI or RWA).",
        "whale_activity": "Medium",
        "recommended_action": "Start with targeted micro-KOL test + platform data to refine messaging."
    }
    
    if any(x in kw for x in ["ai", "agent", "llm", "intelligence"]) or "ai" in desc:
        base.update({
            "score": 87,
            "sentiment": "Very Bullish",
            "narratives": ["AI Agents", "On-chain AI", "DePIN x AI", "Autonomous Agents"],
            "insight": "Strong emerging narrative. High KOL interest in SEA for AI x Crypto projects. " + ("Real project description aligns well with this narrative." if "ai" in desc else "Recommend targeting @indogaming_kol + @sg_defi_alpha for narrative seeding."),
            "whale_activity": "High - 3 smart money wallets accumulated in last 48h",
            "recommended_action": "Launch AI Narrative KOL Pilot immediately. Narrative is heating up fast."
        })
    elif any(x in kw for x in ["gaming", "gamefi", "play"]) or "game" in desc:
        base.update({
            "score": 76,
            "sentiment": "Bullish",
            "narratives": ["GameFi 2.0", "Play-to-Earn Evolution", "AAA Web3 Gaming"],
            "insight": "Solid narrative in SEA. Vietnam and Indonesia KOLs performing well. " + ("Project categories support strong gaming positioning." if "game" in desc else "Watch for new title launches."),
            "whale_activity": "Medium - Some accumulation from gaming guilds",
            "recommended_action": "Good fit for KOL Pilot + Community Analytics bundle."
        })
    elif any(x in kw for x in ["defi", "rwa", "lending"]) or any(x in desc for x in ["defi", "rwa", "lending", "real world"]):
        base.update({
            "score": 69,
            "sentiment": "Neutral to Bullish",
            "narratives": ["RWA", "Real Yield", "Institutional DeFi"],
            "insight": "RWA narrative still early but growing. Singapore KOLs have good reach to institutions. " + ("Real description mentions relevant sectors." if any(x in desc for x in ["defi", "rwa"]) else ""),
            "whale_activity": "Low - More institutional than retail whales",
            "recommended_action": "Use On-chain User Analytics to prove real TVL retention before big KOL push."
        })
    
    return base

def mock_whale_and_smart_money(coin_name: str = "Selected Project") -> List[Dict]:
    """Generate realistic looking whale alerts"""
    now = datetime.now()
    alerts = [
        {
            "time": (now - timedelta(hours=4)).strftime("%H:%M"),
            "type": "Smart Money Accumulation",
            "wallet": "0x7a2b...f91e (Early Investor #3)",
            "action": f"Bought 142,000 {coin_name} tokens",
            "value_usd": "$87,400",
            "note": "Previously bought at $0.012 in 2025. Still holding 68% of position."
        },
        {
            "time": (now - timedelta(hours=11)).strftime("%H:%M"),
            "type": "Whale Exit",
            "wallet": "0x3f1c...a4d2 (CEX Hot Wallet)",
            "action": f"Sold 89,500 {coin_name} tokens",
            "value_usd": "$54,200",
            "note": "Likely profit taking. Watch for further pressure."
        },
        {
            "time": (now - timedelta(hours=19)).strftime("%H:%M"),
            "type": "New Whale Entry",
            "wallet": "0x9d4e...c88b (New Smart Money)",
            "action": f"Bought 210,000 {coin_name} tokens",
            "value_usd": "$129,800",
            "note": "First on-chain activity in this token. High conviction wallet."
        },
        {
            "time": (now - timedelta(hours=27)).strftime("%H:%M"),
            "type": "Smart Money Movement",
            "wallet": "0x2e8f...b31a (Guild Treasury)",
            "action": f"Transferred 55,000 {coin_name} to staking contract",
            "value_usd": "$33,900",
            "note": "Long-term holder behavior. Positive signal."
        }
    ]
    return alerts

def mock_onchain_user_analytics(coin_name: str = "Project") -> Dict[str, Any]:
    """Mock on-chain + user growth analytics"""
    return {
        "active_wallets_24h": random.randint(1240, 8750),
        "d7_retention": round(random.uniform(18, 47), 1),
        "top_10_holders_pct": round(random.uniform(22, 61), 1),
        "user_growth_7d": f"+{random.randint(4, 19)}%",
        "avg_tx_per_user": round(random.uniform(2.1, 7.8), 1),
        "daily_active_trend": pd.DataFrame({
            "Day": pd.date_range(end=datetime.now(), periods=14).strftime("%m/%d"),
            "Active Wallets": [random.randint(800, 2200) for _ in range(14)]
        }),
        "insight": f"{coin_name} shows healthy retention for its stage. Top holder concentration is manageable. Good signal for BD discussions around real user traction."
    }

def mock_fake_follower_detection(handle: str) -> Dict[str, Any]:
    """Demo fake follower detection"""
    if not handle or "@" not in handle:
        handle = "@demo_kol"
    
    # Pseudo-deterministic but realistic output
    seed = sum(ord(c) for c in handle) % 100
    fake_pct = max(4, min(38, (seed % 32) + 6))
    quality = max(55, 96 - fake_pct)
    bot_risk = "Low" if fake_pct < 15 else ("Medium" if fake_pct < 25 else "High")
    
    notes = {
        "Low": "Audience quality is excellent. Mostly organic growth from content & community.",
        "Medium": "Some bot clusters detected (likely from past airdrop/giveaway campaigns). Core audience still strong.",
        "High": "Significant fake follower activity. Recommend audience cleansing before major campaign spend."
    }
    
    return {
        "handle": handle,
        "fake_pct": fake_pct,
        "real_followers_est": int(100 - fake_pct),
        "quality_score": quality,
        "bot_risk": bot_risk,
        "notes": notes[bot_risk],
        "recommendation": "Safe to work with" if fake_pct < 18 else "Request audience report or run smaller test first"
    }

def mock_community_analytics(project_name: str = "Project") -> Dict[str, Any]:
    return {
        "tg_members": random.randint(8500, 124000),
        "tg_growth_7d": f"+{random.randint(120, 890)}",
        "msg_volume_24h": random.randint(340, 2100),
        "sentiment": random.choice(["Bullish", "Slightly Bullish", "Neutral", "Cautious"]),
        "top_topics": ["Token utility", "Upcoming TGE", "Partnership rumors", "AMA recap"],
        "insight": f"{project_name} community is active but narrative needs sharpening. High message volume around utility discussions = good sign for educated holders."
    }

# ==================== HELPER FUNCTIONS ====================
def format_usd(val: Optional[float]) -> str:
    if val is None:
        return "N/A"
    if val >= 1_000_000_000:
        return f"${val/1_000_000_000:.2f}B"
    elif val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val/1_000:.1f}K"
    return f"${val:,.2f}"

def generate_research_links(project_name: str, twitter_handle: Optional[str] = None) -> Dict[str, str]:
    encoded_name = urllib.parse.quote(project_name)
    links = {}
    q_hiring = f'"{project_name}" (hiring OR "we\'re hiring" OR "open position" OR "join our team" OR careers OR "business development" OR BD OR "marketing" OR KOL) -inurl:(job jobber)'
    links["🔍 Google - Hiring Signals"] = f"https://www.google.com/search?q={urllib.parse.quote(q_hiring)}"
    links["💼 LinkedIn - People (Founders/Team)"] = f"https://www.linkedin.com/search/results/people/?keywords={encoded_name}%20(founder%20OR%20CEO%20OR%20CTO%20OR%20hiring%20OR%20BD)"
    links["💼 LinkedIn - Jobs at project"] = f"https://www.linkedin.com/search/results/jobs/?keywords={encoded_name}"
    links["💰 Crunchbase - Funding & Valuation"] = f"https://www.crunchbase.com/search/organizations/field/organizations/num_funding_rounds/num_funding_rounds?query={encoded_name}"
    if twitter_handle:
        links["🐦 X Query (from official)"] = f'from:{twitter_handle} (hiring OR "we are hiring" OR "team expansion" OR "looking for" OR BD OR "business dev" OR KOL OR marketing)'
    links["🐦 X General Search Query (copy-paste)"] = f'"{project_name}" (hiring OR "hiring now" OR "we\'re hiring" OR "team is growing" OR "open roles") min_faves:2'
    links["🚀 Wellfound (AngelList) Jobs"] = f"https://wellfound.com/search?q={encoded_name}"
    return links


# ------------------ DATA FETCH FUNCTIONS (from original, required for CoinGecko integration) ------------------
@st.cache_data(ttl=300, show_spinner="Fetching trending projects...")
def fetch_trending_coins() -> List[Dict]:
    try:
        resp = client.search.trending.get(show_max="coins")
        coins = []
        for item in resp.coins:
            c = item.item
            coins.append({
                "id": c.id,
                "name": c.name,
                "symbol": c.symbol.upper(),
                "market_cap_rank": getattr(c, "market_cap_rank", None),
                "thumb": getattr(c, "thumb", None),
                "score": getattr(c, "score", 0)
            })
        return coins
    except APIError as e:
        st.error(f"CoinGecko API error (trending): {e}")
        return []
    except Exception as e:
        st.error(f"Unexpected error fetching trending: {e}")
        return []

@st.cache_data(ttl=300, show_spinner="Searching CoinGecko...")
def search_coins(query: str) -> List[Dict]:
    if not query or len(query) < 2:
        return []
    try:
        resp = client.search.get(q=query)
        results = []
        for coin in resp.coins:
            results.append({
                "id": coin.id,
                "name": coin.name,
                "symbol": coin.symbol.upper(),
                "market_cap_rank": getattr(coin, "market_cap_rank", None),
                "thumb": getattr(coin, "thumb", None)
            })
        return results[:25]
    except APIError as e:
        st.error(f"CoinGecko search error: {e}")
        return []
    except Exception as e:
        st.error(f"Search error: {e}")
        return []

@st.cache_data(ttl=600, show_spinner="Loading project details from CoinGecko...")
def fetch_coin_details(coin_id: str) -> Optional[Dict]:
    if not coin_id:
        return None
    try:
        coin = client.coins.get_id.get(
            id=coin_id,
            localization=False,
            tickers=False,
            market_data=True,
            community_data=True,
            developer_data=True,
            sparkline=False
        )
        data = {
            "id": coin.id,
            "symbol": coin.symbol,
            "name": coin.name,
            "image": {"thumb": coin.image.thumb if coin.image else None, "small": coin.image.small if coin.image else None},
            "description": coin.description.en if coin.description and hasattr(coin.description, 'en') else "No description available.",
            "categories": [cat.name for cat in coin.categories] if coin.categories else [],
            "links": {
                "homepage": coin.links.homepage[0] if coin.links and coin.links.homepage else None,
                "whitepaper": coin.links.whitepaper if coin.links else None,
                "twitter_screen_name": coin.links.twitter_screen_name if coin.links else None,
                "telegram_channel_identifier": coin.links.telegram_channel_identifier if coin.links else None,
                "subreddit": coin.links.subreddit if coin.links else None,
                "github": coin.links.repos_url.github[0] if coin.links and coin.links.repos_url and coin.links.repos_url.github else None,
            },
            "market_data": {
                "current_price_usd": coin.market_data.current_price.usd if coin.market_data and coin.market_data.current_price else None,
                "market_cap_usd": coin.market_data.market_cap.usd if coin.market_data and coin.market_data.market_cap else None,
                "fully_diluted_valuation_usd": coin.market_data.fully_diluted_valuation.usd if coin.market_data and coin.market_data.fully_diluted_valuation else None,
                "total_volume_usd": coin.market_data.total_volume.usd if coin.market_data and coin.market_data.total_volume else None,
                "price_change_24h": coin.market_data.price_change_percentage_24h if coin.market_data else None,
                "ath_usd": coin.market_data.ath.usd if coin.market_data and coin.market_data.ath else None,
            },
            "community_data": {
                "twitter_followers": getattr(coin.community_data, "twitter_followers", None) if coin.community_data else None,
                "telegram_channel_user_count": getattr(coin.community_data, "telegram_channel_user_count", None) if coin.community_data else None,
            },
            "developer_data": {
                "forks": getattr(coin.developer_data, "forks", None) if coin.developer_data else None,
                "stars": getattr(coin.developer_data, "stars", None) if coin.developer_data else None,
                "subscribers": getattr(coin.developer_data, "subscribers", None) if coin.developer_data else None,
                "total_issues": getattr(coin.developer_data, "total_issues", None) if coin.developer_data else None,
            },
            "last_updated": coin.last_updated.isoformat() if coin.last_updated else None,
            "genesis_date": coin.genesis_date,
        }
        return data
    except APIError as e:
        if "404" in str(e) or "not found" in str(e).lower():
            st.warning(f"Project '{coin_id}' not found on CoinGecko. It may be very early-stage (pre-TGE) or not yet tracked.")
        else:
            st.error(f"CoinGecko detail error: {e}")
        return None
    except Exception as e:
        st.error(f"Failed to fetch details: {e}")
        return None

@st.cache_data(ttl=300)
def fetch_top_gainers() -> List[Dict]:
    try:
        resp = client.coins.top_gainers_losers.get(vs_currency="usd", price_change_percentage="24h")
        gainers = []
        for item in resp.top_gainers[:15]:
            gainers.append({
                "id": item.id,
                "name": item.name,
                "symbol": item.symbol.upper(),
                "price_change_24h": item.price_change_percentage_24h,
                "market_cap": getattr(item, "market_cap", None)
            })
        return gainers
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner="Fetching market chart from CoinGecko...")
def fetch_market_chart(coin_id: str, days: str = "14", vs_currency: str = "usd") -> Optional[Dict]:
    """Fetch real historical market data (prices + volumes) from CoinGecko."""
    if not coin_id:
        return None
    try:
        chart = client.coins.market_chart.get(
            id=coin_id,
            days=days,
            vs_currency=vs_currency
        )
        # chart.prices is list of [timestamp, price]
        # chart.total_volumes is list of [timestamp, volume]
        prices = chart.prices if hasattr(chart, 'prices') else []
        volumes = chart.total_volumes if hasattr(chart, 'total_volumes') else []
        
        return {
            "prices": prices,
            "volumes": volumes,
            "days": days
        }
    except Exception as e:
        st.warning(f"Could not fetch market chart for {coin_id}: {e}")
        return None


# ------------------ DUNE ANALYTICS INTEGRATION ------------------
DUNE_API_URL = "https://api.dune.com/api/v1"

def get_dune_api_key() -> Optional[str]:
    """Get Dune API key from session state or sidebar input."""
    return st.session_state.get("dune_api_key", None)

def execute_dune_query(query_id: int, params: Dict[str, Any], api_key: str) -> Optional[Dict]:
    """Execute a Dune query and return the execution result."""
    if not api_key:
        return None
    
    url = f"{DUNE_API_URL}/query/{query_id}/execute"
    headers = {
        "X-Dune-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json={"query_parameters": params})
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Dune API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to execute Dune query: {e}")
        return None

def get_dune_query_results(execution_id: str, api_key: str) -> Optional[Dict]:
    """Poll and retrieve results from a Dune query execution."""
    if not api_key or not execution_id:
        return None
    
    url = f"{DUNE_API_URL}/execution/{execution_id}/results"
    headers = {"X-Dune-API-Key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("state") == "QUERY_STATE_COMPLETED":
                return data.get("result", {})
            elif data.get("state") in ["QUERY_STATE_PENDING", "QUERY_STATE_EXECUTING"]:
                return {"state": "running", "message": "Query still running..."}
            else:
                return {"state": "error", "message": data.get("state")}
        else:
            return None
    except Exception as e:
        st.error(f"Failed to get Dune results: {e}")
        return None

def run_dune_query_and_get_results(query_id: int, params: Dict[str, Any], api_key: str, max_wait: int = 30) -> Optional[pd.DataFrame]:
    """High-level helper: execute + wait for results and return as DataFrame."""
    import time
    
    exec_result = execute_dune_query(query_id, params, api_key)
    if not exec_result or "execution_id" not in exec_result:
        return None
    
    execution_id = exec_result["execution_id"]
    
    for _ in range(max_wait):
        results = get_dune_query_results(execution_id, api_key)
        if results and results.get("state") == "QUERY_STATE_COMPLETED":
            rows = results.get("rows", [])
            if rows:
                return pd.DataFrame(rows)
            return pd.DataFrame()
        elif results and results.get("state") == "error":
            st.error(f"Dune query failed: {results.get('message')}")
            return None
        time.sleep(1)
    
    st.warning("Dune query took too long. Try running it directly on dune.com or increase timeout.")
    return None


# ------------------ NANSEN SMART MONEY INTEGRATION (Premium) ------------------
NANSEN_API_URL = "https://api.nansen.ai/v1"  # Update if Nansen changes their base URL

def get_nansen_api_key() -> Optional[str]:
    return st.session_state.get("nansen_api_key", None)

def fetch_nansen_smart_money_flows(token_address: str, api_key: str, chain: str = "ethereum", days: int = 7) -> Optional[pd.DataFrame]:
    """
    Example integration for Nansen Smart Money flows.
    NOTE: Exact endpoint and parameters depend on your Nansen plan.
    Check your Nansen dashboard / API docs for the latest endpoints.
    """
    if not api_key or not token_address:
        return None
    
    # Common pattern - adjust based on actual Nansen API
    url = f"{NANSEN_API_URL}/smart-money/flows"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    params = {
        "token_address": token_address,
        "chain": chain,
        "days": days
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                return pd.DataFrame(data["data"])
            return pd.DataFrame(data) if isinstance(data, list) else None
        else:
            st.warning(f"Nansen API returned {response.status_code}. Check your key and plan limits.")
            return None
    except Exception as e:
        st.error(f"Nansen API call failed: {e}")
        return None

def fetch_nansen_smart_money_wallets(api_key: str, limit: int = 20) -> Optional[pd.DataFrame]:
    """Fetch top smart money wallets (example endpoint)."""
    if not api_key:
        return None
    
    url = f"{NANSEN_API_URL}/smart-money/wallets"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, params={"limit": limit}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data.get("wallets", data))
        return None
    except Exception as e:
        st.error(f"Nansen wallets call failed: {e}")
        return None


def assess_budget_fit(details: Dict, user_inputs: Dict) -> Dict[str, Any]:
    """Updated assessment - now also scores fit for Growth Intelligence Platform"""
    mc = details.get("market_data", {}).get("market_cap_usd") or 0
    vol = details.get("market_data", {}).get("total_volume_usd") or 0
    stage = user_inputs.get("stage", "Unknown")
    hiring = user_inputs.get("hiring_potential", "Medium")
    
    score = 0
    reasons = []
    platform_fit = 0
    platform_reasons = []
    
    # Valuation signals
    if mc > 50_000_000:
        score += 3
        reasons.append("Solid market cap indicates established traction")
    elif mc > 10_000_000:
        score += 2
        reasons.append("Mid-stage valuation - good for growth packages")
    else:
        score += 1
        reasons.append("Early-stage / low MC - ideal for pilot testing")
    
    # Volume = budget + need for analytics
    if vol > 5_000_000:
        score += 3
        platform_fit += 3
        reasons.append("High 24h volume = strong user activity & likely marketing budget")
        platform_reasons.append("High volume = perfect for On-chain User Analytics + KOL ROI tracking")
    elif vol > 500_000:
        score += 2
        platform_fit += 2
        platform_reasons.append("Decent volume - platform can help prove real user growth to investors/partners")
    
    # Stage
    if stage in ["Series A", "Listed / TGE done", "Growth"]:
        score += 2
        platform_fit += 2
        reasons.append("Later stage = higher budget for BD & scaling")
        platform_reasons.append("Growth stage projects need data to optimize spend and report to stakeholders")
    elif stage in ["Seed", "Pre-seed / Testnet"]:
        score += 1
        platform_fit += 1
    
    # Hiring signal
    if hiring == "High":
        score += 2
        platform_fit += 1
        reasons.append("Active hiring signals budget & ambition")
        platform_reasons.append("Hiring team = they will value internal analytics tools for BD & marketing team")
    
    # Recommendation logic (services)
    if score >= 7:
        rec = "Gold Subscription (BD) + Custom KOL + Growth Platform"
        why = "High potential client ready for strategic closings, integrations & scaled visibility. They will also benefit hugely from proprietary data tools."
    elif score >= 5:
        rec = "Gold or Silver BD + KOL Pilot + Platform Access"
        why = "Good fit for pipeline building + quick traction wins. Platform data will make campaigns more measurable and defensible."
    else:
        rec = "KOL Pilot Package ($2,999-$3,499) + Platform Trial"
        why = "Low-risk entry to generate initial results & learnings in 2-3 weeks. Platform access helps them see the value of data-driven growth early."
    
    if hiring == "High":
        rec += " + Talent Placement Support"
        why += " They are hiring — we can offer to source quality Web3 talent (BD, marketing, devs) from our network."
    
    # Platform specific rec
    if platform_fit >= 5:
        platform_rec = "Strong fit for Growth Intelligence Platform subscription (or bundle with KOL/BD)"
    elif platform_fit >= 3:
        platform_rec = "Good candidate for Platform + KOL Pilot Bundle"
    else:
        platform_rec = "Start with KOL Pilot; introduce Platform after first results"
    
    return {
        "score": score,
        "recommendation": rec,
        "why": why,
        "reasons": reasons,
        "platform_fit_score": platform_fit,
        "platform_recommendation": platform_rec,
        "platform_reasons": platform_reasons,
        "suggested_price_range": KOL_PRICING.get(rec.split(" + ")[0], {}).get("price", "Custom quote")
    }

def generate_pitch(project_name: str, details: Optional[Dict], assessment: Dict, user_inputs: Dict, selected_services: List[str]) -> str:
    """Updated pitch generator - now sells the platform as key differentiator"""
    mc_str = format_usd(details.get("market_data", {}).get("market_cap_usd")) if details else "N/A"
    vol_str = format_usd(details.get("market_data", {}).get("total_volume_usd")) if details else "N/A"
    
    stage = user_inputs.get("stage", "early stage")
    hiring_note = ""
    if user_inputs.get("hiring_potential") == "High":
        hiring_note = "\nWe noticed strong hiring signals — we'd love to explore how we can support your team growth with vetted Web3 talent as well."
    
    pain_points = user_inputs.get("pain_points", "scaling visibility and closing strategic partnerships in a crowded market")
    
    # Platform mention
    platform_line = ""
    if any("Platform" in s or "Growth Intelligence" in s for s in selected_services):
        platform_line = """
**Our secret weapon (included in recommended packages):**
Access to Wyvernomics proprietary **Web3 Growth Intelligence Platform** — KOL Analytics, On-chain User Analytics, AI Narrative Tracker, Whale Alerts, Fake Follower Detection, and Campaign ROI tracking. Most agencies guess. We let data drive every recommendation and optimization.
"""
    
    pitch = f"""Subject: Quick wins for {project_name} — KOL traction + BD pipeline in SEA/APAC (2-3 weeks) + data advantage

Hi {project_name} Team,

I'm reaching out from Wyvernomics, a dedicated BD Acceleration Agency for Web3 projects.

We've been following {project_name}'s progress (current MC ~{mc_str}, strong {vol_str} 24h volume). Many promising protocols have excellent tech but struggle with the "last mile" of business development and real-user traction — exactly where we specialize.

**Why we're a strong fit right now:**
- {assessment['why']}
- {hiring_note}

**Our recommended package for you:**
{assessment['recommendation']} — {assessment['suggested_price_range']}

{platform_line}

We don't just find leads. We close them and scale your ecosystem with:
• End-to-end pipeline management for CEX listings, L1/L2 integrations, B2B alliances
• Rapid GTM execution turning users into transactional volume (SEA & APAC focus)
• Measurable KOL results in 2–3 weeks with full management & weekly reporting
• Proprietary data tools so you can see exactly which KOLs, narratives, and user segments are driving real value

**Next step:** A short 15-min call to review your current GTM priorities and see if a Pilot, Gold package, or Growth Intelligence Platform access makes sense. No commitment — we'll even share a free mini-audit of your current BD pipeline + sample intelligence report.

Looking forward to helping {project_name} bridge the gap to real market dominance with both execution and data.

Best regards,  
[Your Name]  
Wyvernomics | BD Acceleration & KOL Execution  
@Rathian_Wyvernomics | @BobCA2  
business@wyvernomics.team

P.S. We recently helped similar projects in AI, Gaming, and L2 space achieve measurable volume and partnership closes while giving them full visibility through our Growth Intelligence Platform. Happy to share relevant case studies + live demo.
"""
    return pitch.strip()

# ==================== UI ====================
def main():
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/300x80/1a1a1a/D4AF37?text=WYVERNOMICS", use_container_width=True)
    st.sidebar.markdown("### 🐉 Wyvernomics")
    st.sidebar.caption("We bridge the gap between high-potential protocols and real-world market dominance — with data.")
    
    st.sidebar.divider()
    st.sidebar.markdown("**Quick Services**")
    
    for pkg, info in KOL_PRICING.items():
        with st.sidebar.expander(pkg):
            st.write(f"**{info['price']}**")
            st.caption(info['desc'])
            st.caption(f"Best for: {info['best_for']}")
    
    st.sidebar.divider()
    st.sidebar.markdown("**NEW: Growth Intelligence Platform**")
    for pkg, info in PLATFORM_PRICING.items():
        with st.sidebar.expander(pkg, expanded=(pkg == "Growth Intelligence Platform")):
            st.write(f"**{info['price']}**")
            st.caption(info['desc'])
            st.caption(f"Best for: {info['best_for']}")
    
    # Dune Analytics Integration (for real on-chain data)
    st.sidebar.divider()
    with st.sidebar.expander("🔗 Dune Analytics (On-Chain Data)", expanded=False):
        st.caption("Connect your Dune API key for live whale tracking, smart money flows, and real user activity on-chain.")
        dune_key = st.text_input(
            "Dune API Key",
            value=st.session_state.get("dune_api_key", ""),
            type="password",
            placeholder="Paste your Dune API key here",
            help="Get free key at dune.com → Account → API Keys. Free tier has rate limits."
        )
        if dune_key:
            st.session_state.dune_api_key = dune_key
            st.success("Dune API key saved for this session")
        elif st.session_state.get("dune_api_key"):
            st.info("Using saved Dune API key")
        
        st.markdown("**Recommended Dune queries for Web3 Growth:**")
        st.caption("• Large token transfers / whale movements\n• Unique active wallets (daily/weekly)\n• Top holder concentration changes\n• Smart money / early buyer tracking")
        st.caption("Create these on dune.com and paste the Query ID in the Growth Intelligence tab.")
    
    # Nansen Smart Money Integration (Premium)
    with st.sidebar.expander("🧠 Nansen Smart Money (Premium)", expanded=False):
        st.caption("Connect Nansen API for labeled smart money wallets, alpha flows, and high-conviction on-chain signals. (Requires Nansen paid plan)")
        nansen_key = st.text_input(
            "Nansen API Key",
            value=st.session_state.get("nansen_api_key", ""),
            type="password",
            placeholder="Paste your Nansen API key",
            help="Available in Nansen dashboard under API / Integrations (paid plans only)"
        )
        if nansen_key:
            st.session_state.nansen_api_key = nansen_key
            st.success("Nansen API key saved for this session")
        elif st.session_state.get("nansen_api_key"):
            st.info("Using saved Nansen API key")
        
        st.markdown("**High-value Nansen signals for prospects:**")
        st.caption("• Smart money inflows/outflows for a token\n• Top performing smart money wallets\n• Early buyer / smart money accumulation\n• Wallet labeling & behavior clustering")
        st.caption("This is one of the strongest differentiators when pitching data-driven BD/KOL services.")
    
    st.sidebar.divider()
    st.sidebar.markdown("**How to use this tool**")
    st.sidebar.markdown("""
    1. **Discover** trending or search new projects  
    2. **Demo the Platform** — show prospects real analytics live  
    3. **Analyze** valuation, hiring signals & platform fit  
    4. **Pitch** — generate customized outreach (now includes platform value prop)  
    5. **Track** everything in Prospects portfolio
    """)
    
    st.sidebar.caption("Data powered by CoinGecko • Growth Intelligence features are interactive demos • Research links for deep-dive")
    
    # Session state
    if "prospects" not in st.session_state:
        st.session_state.prospects = load_prospects()
    
    if "current_project" not in st.session_state:
        st.session_state.current_project = None
        st.session_state.current_project_name = None
    
    # Main header
    st.markdown('<p class="main-header">🐉 Wyvernomics | Web3 Growth Intelligence + BD Acceleration</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Research projects • Demo proprietary analytics platform • Assess budget & platform fit • Craft winning pitches • Track pipeline</p>', unsafe_allow_html=True)
    
    tabs = st.tabs([
        "🔍 Discover Projects", 
        "📈 Growth Intelligence Platform", 
        "🔬 Analyze & Platform Fit", 
        "✍️ Pitch Builder", 
        "📁 My Prospects Portfolio"
    ])
    
    # ========== TAB 1: DISCOVER ==========
    with tabs[0]:
        st.markdown("## 🔍 Discover New & Trending Web3 Projects")
        
        col_search, col_trending = st.columns([3, 2])
        
        with col_search:
            search_q = st.text_input("Search CoinGecko by name / keyword", placeholder="e.g. Saakuru, AI agent, new L2, gaming, RWA", key="search_q")
            if st.button("Search Projects", type="primary", key="btn_search"):
                if search_q:
                    with st.spinner("Searching..."):
                        results = search_coins(search_q)
                        if results:
                            st.session_state.search_results = results
                        else:
                            st.info("No results or API limit reached. Try a more specific term.")
        
        with col_trending:
            if st.button("🚀 Load Trending Coins (24h)", type="secondary"):
                with st.spinner("Loading trending..."):
                    trending = fetch_trending_coins()
                    if trending:
                        st.session_state.trending_results = trending
        
        results_to_show = st.session_state.get("search_results") or st.session_state.get("trending_results")
        
        if results_to_show:
            st.markdown("### Results")
            selected_name = st.selectbox(
                "Select a project from results to analyze or demo in Growth Intelligence tab:",
                options=[f"{r['name']} ({r['symbol']}) — ID: {r['id']}" for r in results_to_show],
                index=0 if results_to_show else None
            )
            
            if selected_name:
                for r in results_to_show:
                    if f"{r['name']} ({r['symbol']})" in selected_name:
                        selected = r
                        break
                else:
                    selected = results_to_show[0]
                
                st.success(f"Selected: **{selected['name']}** (CoinGecko ID: `{selected['id']}`)")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 Analyze this project (valuation + hiring)", type="primary"):
                        st.session_state.current_project = selected["id"]
                        st.session_state.current_project_name = selected["name"]
                        st.info("👉 Switch to **Analyze & Platform Fit** tab")
                with col2:
                    if st.button("📈 Demo this project in Growth Intelligence Platform", type="secondary"):
                        st.session_state.current_project = selected["id"]
                        st.session_state.current_project_name = selected["name"]
                        st.info("👉 Switch to **Growth Intelligence Platform** tab — the project context is loaded!")
        
        st.divider()
        st.markdown("**Pro tip:** Very early projects (pre-TGE) often won't appear on CoinGecko. Use the **Growth Intelligence Platform** tab + X research links for those, or add them manually in Pitch Builder.")
    
    # ========== TAB 2: GROWTH INTELLIGENCE PLATFORM (NEW MAIN FEATURE) ==========
    with tabs[1]:
        st.markdown("## 📈 Wyvernomics Web3 Growth Intelligence Platform")
        st.markdown('<span class="platform-badge">PROPRIETARY • SEA/APAC FOCUSED • DEMO MODE</span>', unsafe_allow_html=True)
        st.caption("This is the exact platform your team discussed — now built as an interactive demo you can show prospects live. Subscription model ready.")
        
        # Context from selected project + real CoinGecko data
        current_name = st.session_state.get("current_project_name", "a selected project")
        current_id = st.session_state.get("current_project")
        
        if current_id:
            # Try to get fresh details for live metrics
            live_details = fetch_coin_details(current_id)
            if live_details:
                mc = live_details.get("market_data", {}).get("market_cap_usd")
                vol = live_details.get("market_data", {}).get("total_volume_usd")
                tw = live_details.get("community_data", {}).get("twitter_followers")
                st.success(f"**Live context from CoinGecko:** {current_name} | MC: {format_usd(mc)} | 24h Vol: {format_usd(vol)} | Twitter: {tw:,}" if tw else f"**Live context from CoinGecko:** {current_name} | MC: {format_usd(mc)} | 24h Vol: {format_usd(vol)}")
            else:
                st.info(f"**Current context:** {current_name} — Many features below use this project where relevant.")
        else:
            st.info(f"**Current context:** {current_name} — Many features below are pre-filled with this project where relevant. Change project in Discover or Analyze tabs.")
        
        # Feature selector
        feature = st.selectbox(
            "Choose a platform capability to demo:",
            [
                "KOL Analytics (SEA/APAC)",
                "AI Narrative Scanner & Tracker",
                "Whale Alerts & Smart Money Tracker",
                "On-chain User Analytics",
                "Dune On-Chain Intelligence (Whales & Smart Money)",
                "Nansen Smart Money Intelligence",
                "Fake Follower Detection",
                "Community Analytics",
                "Campaign Management & ROI"
            ],
            index=0
        )
        
        st.divider()
        
        # === KOL ANALYTICS ===
        if feature == "KOL Analytics (SEA/APAC)":
            st.markdown("### 👥 KOL Analytics — SEA & APAC Focus")
            st.caption("Find, score, and compare authentic KOLs. Filter by niche, country, engagement quality, and historical ROI.")
            
            kols_df = get_sample_kols()
            
            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                niche_filter = st.multiselect("Filter by Niche", options=["Gaming", "DeFi", "NFT", "Layer2", "AI", "RWA", "Infrastructure"], default=[])
            with col_f2:
                min_followers = st.slider("Min Followers", 50000, 250000, 70000, step=10000)
            
            filtered = kols_df[kols_df["followers"] >= min_followers]
            if niche_filter:
                filtered = filtered[filtered["niche"].str.contains("|".join(niche_filter), case=False, na=False)]
            
            st.dataframe(
                filtered[["handle", "name", "followers", "eng_rate", "fake_pct", "niche", "country", "recent_roi", "last_campaign"]],
                use_container_width=True,
                hide_index=True
            )
            
            st.success("**Key insight for prospects:** We filter out high fake-follower KOLs and prioritize those with proven ROI in similar verticals. This is why our KOL Pilots consistently outperform generic outreach.")
        
        # === AI NARRATIVE SCANNER ===
        elif feature == "AI Narrative Scanner & Tracker":
            st.markdown("### 🧠 AI Narrative Scanner & Tracker")
            st.caption("Understand what narratives are heating up, how a project fits, and which KOLs to activate. Uses real project data from CoinGecko when available.")
            
            current_id = st.session_state.get("current_project")
            live_details = fetch_coin_details(current_id) if current_id else None
            
            col_n1, col_n2 = st.columns([1, 1])
            with col_n1:
                default_val = current_name if current_name != "a selected project" else "AI Agent"
                narrative_input = st.text_input("Project name or narrative keyword", value=default_val, placeholder="e.g. AI Agent, GameFi, RWA, Saakuru")
            
            if live_details:
                with st.expander("Use real CoinGecko description & categories for this scan"):
                    st.write("**Real description:**", live_details.get("description", "")[:400] + "...")
                    if live_details.get("categories"):
                        st.write("**Categories:**", " • ".join(live_details["categories"]))
            
            if st.button("🔍 Scan Narrative", type="primary"):
                # Enhanced: pass real description to mock function for better context
                real_desc = live_details.get("description", "") if live_details else ""
                result = mock_ai_narrative_scan(narrative_input, real_desc)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Narrative Strength", f"{result['score']}/100")
                m2.metric("Sentiment", result["sentiment"])
                m3.metric("Whale Activity", result.get("whale_activity", "Medium"))
                
                st.markdown("**Top Related Narratives**")
                for n in result["narratives"]:
                    st.write(f"• {n}")
                
                st.markdown("**AI Insight**")
                st.write(result["insight"])
                
                if result.get("recommended_action"):
                    st.info(f"**Recommended Action:** {result['recommended_action']}")
        
        # === WHALE & SMART MONEY ===
        elif feature == "Whale Alerts & Smart Money Tracker":
            st.markdown("### 🐋 Whale Alerts & Smart Money Tracker")
            st.caption("Real-time large wallet movements + labeled smart money behavior. Critical for timing campaigns and understanding holder conviction.")
            
            coin_for_whale = current_name if current_name != "a selected project" else "Selected Token"
            alerts = mock_whale_and_smart_money(coin_for_whale)
            
            for alert in alerts:
                with st.container():
                    col_t, col_a = st.columns([1, 5])
                    with col_t:
                        st.markdown(f"**{alert['time']}**")
                    with col_a:
                        st.markdown(f"**{alert['type']}** — {alert['action']} ({alert['value_usd']})")
                        st.caption(f"{alert['wallet']} • {alert['note']}")
                    st.divider()
            
            st.success("**Value for prospects:** Show them real holder behavior instead of vanity metrics. Great for investor updates and internal decision making on when to push KOL campaigns.")
        
        # === DUNE ON-CHAIN INTELLIGENCE (NEW) ===
        elif feature == "Dune On-Chain Intelligence (Whales & Smart Money)":
            st.markdown("### 🔗 Dune On-Chain Intelligence")
            st.caption("Live on-chain data powered by Dune Analytics — whale movements, smart money flows, active users, and holder behavior.")
            
            dune_key = get_dune_api_key()
            
            if not dune_key:
                st.warning("⚠️ No Dune API key connected. Add your key in the sidebar (under 'Dune Analytics') to use live on-chain data.")
                st.info("**What you can do with Dune here:**\n- Track large token buys/sells by labeled smart money wallets\n- Monitor daily/weekly active users for a protocol\n- See changes in top holder concentration\n- Detect accumulation/distribution patterns")
                
                st.markdown("**Example use case for a prospect:**")
                st.code("Query: 'Large transfers for [Token Contract] in last 7 days'\n→ Filter > $10k transfers → See which wallets are accumulating", language="text")
            else:
                st.success("✅ Dune API key connected — live queries enabled")
                
                col_d1, col_d2 = st.columns([1, 2])
                with col_d1:
                    query_id = st.number_input("Dune Query ID", min_value=1, value=1234567, step=1, 
                                               help="Create a query on dune.com and copy the ID from the URL")
                    token_address = st.text_input("Token Contract Address (optional)", 
                                                  placeholder="0x...", 
                                                  help="Pass as {{token_address}} parameter in your Dune query")
                
                with col_d2:
                    st.markdown("**Quick Actions**")
                    if st.button("Run Example: Whale Transfers (last 7d)"):
                        # This is a placeholder - user needs to create their own query
                        st.info("Create a Dune query like:\nSELECT * FROM token_transfers WHERE contract_address = '{{token_address}}' AND amount_usd > 10000\nThen paste the Query ID above.")
                    
                    if st.button("Run Example: Daily Active Wallets"):
                        st.info("Create a query that counts unique addresses interacting with the protocol daily.")
                
                params = {}
                if token_address:
                    params["token_address"] = token_address
                
                if st.button("🚀 Execute Dune Query", type="primary"):
                    with st.spinner("Running query on Dune... (can take 5-30s)"):
                        df = run_dune_query_and_get_results(query_id, params, dune_key)
                        
                        if df is not None and not df.empty:
                            st.success(f"Query returned {len(df)} rows")
                            st.dataframe(df, use_container_width=True)
                            
                            # Simple insight
                            if "amount_usd" in df.columns or "value_usd" in df.columns:
                                total_vol = df["amount_usd"].sum() if "amount_usd" in df.columns else df.get("value_usd", pd.Series([0])).sum()
                                st.metric("Total On-Chain Volume Detected", f"${total_vol:,.0f}")
                        elif df is not None:
                            st.info("Query executed successfully but returned no rows.")
                        else:
                            st.error("Query failed or timed out. Check your Query ID and parameters.")
                
                st.caption("Tip: Start with simple queries on dune.com first. Once they work, bring the Query ID here for one-click execution during prospect calls.")
        
        # === NANSEN SMART MONEY INTELLIGENCE (NEW) ===
        elif feature == "Nansen Smart Money Intelligence":
            st.markdown("### 🧠 Nansen Smart Money Intelligence")
            st.caption("Premium labeled smart money data — see exactly which high-conviction wallets are accumulating or exiting a token.")
            
            nansen_key = get_nansen_api_key()
            
            if not nansen_key:
                st.warning("⚠️ No Nansen API key connected. Add your key in the sidebar under 'Nansen Smart Money (Premium)'.")
                st.info("Nansen is one of the best sources for **labeled smart money** behavior. When connected, you can show prospects real alpha flows during calls — a massive trust builder for premium BD/KOL packages.")
            else:
                st.success("✅ Nansen API key connected")
                
                current_id = st.session_state.get("current_project")
                token_input = st.text_input(
                    "Token Contract Address",
                    value="",
                    placeholder="0x... (Ethereum, Base, Solana, etc.)",
                    help="The token you want smart money data for"
                )
                
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    chain = st.selectbox("Chain", ["ethereum", "base", "solana", "arbitrum", "bsc"], index=0)
                    days = st.slider("Lookback Days", 1, 30, 7)
                
                with col_n2:
                    st.markdown("**Available Actions**")
                    if st.button("Fetch Smart Money Flows"):
                        if not token_input:
                            st.error("Please enter a token contract address")
                        else:
                            with st.spinner("Querying Nansen for smart money flows..."):
                                df = fetch_nansen_smart_money_flows(token_input, nansen_key, chain, days)
                                if df is not None and not df.empty:
                                    st.success(f"Found {len(df)} smart money flow records")
                                    st.dataframe(df, use_container_width=True)
                                    
                                    # Quick insights
                                    if "inflow_usd" in df.columns or "amount_usd" in df.columns:
                                        col = "inflow_usd" if "inflow_usd" in df.columns else "amount_usd"
                                        st.metric("Total Smart Money Inflow", f"${df[col].sum():,.0f}")
                                else:
                                    st.info("No smart money flows found or API returned empty. This can be normal for low-activity tokens.")
                    
                    if st.button("Fetch Top Smart Money Wallets"):
                        with st.spinner("Fetching top smart money wallets from Nansen..."):
                            df = fetch_nansen_smart_money_wallets(nansen_key)
                            if df is not None and not df.empty:
                                st.dataframe(df.head(20), use_container_width=True)
                            else:
                                st.info("Could not retrieve top wallets (check API access).")
                
                st.caption("Note: Nansen endpoints can vary by plan. Update the helper functions in the code if your Nansen API structure is different. This integration gives you a professional starting point.")
        
        # === ON-CHAIN USER ANALYTICS (Hybrid: Real CoinGecko + Demo) ===
        elif feature == "On-chain User Analytics":
            st.markdown("### 📊 On-chain User Analytics")
            st.caption("Real market & community signals from CoinGecko + demo user behavior analytics. (Full on-chain wallet data requires premium providers)")
            
            current_id = st.session_state.get("current_project")
            real_chart = None
            
            if current_id:
                real_chart = fetch_market_chart(current_id, days="14")
            
            if real_chart and real_chart.get("volumes"):
                # Use REAL CoinGecko data
                st.success("✅ Showing **live CoinGecko market data** for this project")
                
                # Build dataframe for charts
                vol_df = pd.DataFrame(real_chart["volumes"], columns=["timestamp", "volume"])
                vol_df["date"] = pd.to_datetime(vol_df["timestamp"], unit="ms").dt.strftime("%m/%d")
                
                price_df = pd.DataFrame(real_chart["prices"], columns=["timestamp", "price"])
                price_df["date"] = pd.to_datetime(price_df["timestamp"], unit="ms").dt.strftime("%m/%d")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("24h Volume (latest)", format_usd(vol_df["volume"].iloc[-1]) if len(vol_df) > 0 else "N/A")
                c2.metric("14d Volume Trend", "↑" if vol_df["volume"].iloc[-1] > vol_df["volume"].iloc[0] else "↓")
                c3.metric("Price Change (14d)", f"{((price_df['price'].iloc[-1] / price_df['price'].iloc[0] - 1) * 100):.1f}%" if len(price_df) > 1 else "N/A")
                c4.metric("Data Points", f"{len(vol_df)} days")
                
                st.markdown("**Real 14-Day Trading Volume Trend (CoinGecko)**")
                st.line_chart(vol_df.set_index("date")["volume"])
                
                st.markdown("**Real Price Trend (CoinGecko)**")
                st.line_chart(price_df.set_index("date")["price"])
                
                st.info("High sustained volume + healthy price action = strong signal that the project has real user activity and likely marketing/BD budget. This is the kind of data we use to qualify prospects for the Growth Intelligence Platform.")
            else:
                # Fallback to mock
                st.warning("No live project selected or chart data unavailable. Showing demo data.")
                onchain = mock_onchain_user_analytics(current_name)
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Active Wallets (24h)", f"{onchain['active_wallets_24h']:,}")
                c2.metric("D7 Retention", f"{onchain['d7_retention']}%")
                c3.metric("Top 10 Holders %", f"{onchain['top_10_holders_pct']}%")
                c4.metric("7d User Growth", onchain["user_growth_7d"])
                
                st.markdown("**14-Day Active Wallet Trend (Demo)**")
                st.line_chart(onchain["daily_active_trend"].set_index("Day"))
                
                st.info(onchain["insight"])
            
            st.caption("Note: True per-wallet on-chain analytics (whale wallets, retention cohorts) require additional data providers. CoinGecko gives excellent market + community proxies.")
        
        # === FAKE FOLLOWER DETECTION ===
        elif feature == "Fake Follower Detection":
            st.markdown("### 🕵️ Fake Follower Detection")
            st.caption("Quickly audit any KOL or project Twitter before committing budget. Protect campaign ROI.")
            
            handle_input = st.text_input("Twitter / X handle to check", value="@demo_kol_sea", placeholder="@handle")
            
            if st.button("Analyze Audience Quality", type="primary"):
                result = mock_fake_follower_detection(handle_input)
                
                col_f1, col_f2, col_f3 = st.columns(3)
                col_f1.metric("Fake Followers", f"{result['fake_pct']}%")
                col_f2.metric("Est. Real Followers", f"{result['real_followers_est']}%")
                col_f3.metric("Audience Quality Score", f"{result['quality_score']}/100")
                
                risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                st.markdown(f"**Bot Risk Level:** {risk_color.get(result['bot_risk'], '')} {result['bot_risk']}")
                
                st.write(result["notes"])
                st.warning(result["recommendation"])
        
        # === COMMUNITY ANALYTICS ===
        elif feature == "Community Analytics":
            st.markdown("### 💬 Community Analytics (TG + X)")
            st.caption("Message volume, sentiment, growth, and top discussion topics — all in one view.")
            
            comm = mock_community_analytics(current_name)
            
            cc1, cc2, cc3 = st.columns(3)
            cc1.metric("Telegram Members", f"{comm['tg_members']:,}")
            cc2.metric("7d Growth", f"+{comm['tg_growth_7d']}")
            cc3.metric("Messages (24h)", f"{comm['msg_volume_24h']:,}")
            
            st.markdown(f"**Current Sentiment:** {comm['sentiment']}")
            st.markdown("**Top Discussion Topics**")
            for t in comm["top_topics"]:
                st.write(f"• {t}")
            
            st.info(comm["insight"])
        
        # === CAMPAIGN MANAGEMENT ===
        elif feature == "Campaign Management & ROI":
            st.markdown("### 📋 Campaign Management & ROI Tracker")
            st.caption("Plan, track, and prove the ROI of every KOL and campaign. This is what makes our service defensible.")
            
            with st.form("campaign_form"):
                st.write("**Create / Simulate a New Campaign**")
                c_name = st.text_input("Campaign Name", value=f"{current_name} KOL Pilot - July 2026")
                selected_kols = st.multiselect("Select KOLs from our database", options=get_sample_kols()["handle"].tolist(), default=["@indogaming_kol", "@sg_defi_alpha"])
                budget = st.number_input("Total KOL Budget (USD)", min_value=500, value=8500, step=500)
                expected_reach = st.number_input("Expected Total Reach", min_value=10000, value=420000, step=10000)
                
                submitted = st.form_submit_button("Simulate Campaign & Calculate ROI")
            
            if submitted:
                # Mock ROI calculation
                roi = round(random.uniform(2.1, 5.8), 1)
                volume_generated = int(budget * roi * random.uniform(0.8, 1.4))
                
                st.success(f"**Projected ROI: {roi}x**")
                st.metric("Est. On-chain Volume Generated", f"${volume_generated:,}")
                st.caption("Based on historical performance of similar campaigns in our database + current narrative strength.")
                
                st.markdown("**Campaign Summary**")
                st.write(f"- KOLs: {', '.join(selected_kols)}")
                st.write(f"- Budget: ${budget:,}")
                st.write(f"- Est. Reach: {expected_reach:,}")
                st.write(f"- Est. Cost per Engaged User: ${round(budget / (expected_reach * 0.012), 3)}")
                
                st.info("In the real platform, this view would be connected to on-chain attribution, KOL performance history, and automated weekly reporting for clients.")
        
        st.divider()
        st.markdown("**This entire platform can be offered as a standalone subscription or bundled with our KOL/BD execution services.** Prospects love seeing the data live — it builds massive trust and differentiates us from every other agency.")
    
    # ========== TAB 3: ANALYZE & PLATFORM FIT (Updated) ==========
    with tabs[2]:
        st.markdown("## 🔬 Project Analyzer & Platform Fit Assessment")
        
        coin_id_input = st.text_input(
            "CoinGecko Project ID (or from Discover tab)",
            value=st.session_state.get("current_project", ""),
            placeholder="e.g. bitcoin, ethereum, saakuru-protocol, or any new project",
            help="Find exact ID from CoinGecko URL or Discover tab"
        )
        
        if st.button("Load / Refresh Project Data", type="primary"):
            if coin_id_input:
                st.session_state.current_project = coin_id_input.strip().lower()
                st.session_state.current_project_name = None
        
        if not coin_id_input and not st.session_state.get("current_project"):
            st.info("Enter a CoinGecko ID above or select from **Discover** tab.")
            st.stop()
        
        coin_id = coin_id_input or st.session_state.get("current_project")
        details = fetch_coin_details(coin_id)
        
        if not details:
            st.warning("Could not load project. Check ID or try again (rate limits possible).")
            st.stop()
        
        if not st.session_state.get("current_project_name"):
            st.session_state.current_project_name = details["name"]
        
        # Header
        col_logo, col_title = st.columns([1, 5])
        with col_logo:
            if details.get("image", {}).get("small"):
                st.image(details["image"]["small"], width=90)
        with col_title:
            st.markdown(f"### {details['name']} ({details['symbol'].upper()})")
            if details.get("genesis_date"):
                st.caption(f"Genesis / Launch: {details['genesis_date']}")
        
        # Valuation metrics (same as original)
        st.markdown("### 💰 Valuation & Activity Signals (Budget + Platform Fit Proxy)")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mc = details["market_data"].get("market_cap_usd")
        fdv = details["market_data"].get("fully_diluted_valuation_usd")
        vol = details["market_data"].get("total_volume_usd")
        price_chg = details["market_data"].get("price_change_24h")
        
        with mcol1:
            st.metric("Market Cap", format_usd(mc))
        with mcol2:
            st.metric("Fully Diluted Val", format_usd(fdv))
        with mcol3:
            st.metric("24h Volume", format_usd(vol), help="High volume = higher budget + strong need for user analytics")
        with mcol4:
            delta = f"{price_chg:.1f}%" if price_chg else None
            st.metric("24h Price Change", delta or "N/A")
        
        # Community signals
        st.markdown("### 👥 Community & Development Signals")
        ccol1, ccol2, ccol3 = st.columns(3)
        with ccol1:
            st.metric("Twitter Followers", f"{details['community_data'].get('twitter_followers') or 0:,}" if details['community_data'].get('twitter_followers') else "N/A")
        with ccol2:
            st.metric("Telegram Members", f"{details['community_data'].get('telegram_channel_user_count') or 0:,}" if details['community_data'].get('telegram_channel_user_count') else "N/A")
        with ccol3:
            st.metric("GitHub Stars", f"{details['developer_data'].get('stars') or 0:,}" if details['developer_data'].get('stars') else "N/A")
        
        # Links
        st.markdown("### 🔗 Official Links")
        link_cols = st.columns(4)
        links = details.get("links", {})
        if links.get("homepage"):
            link_cols[0].link_button("🌐 Website", links["homepage"])
        if links.get("twitter_screen_name"):
            link_cols[1].link_button("🐦 Twitter/X", f"https://x.com/{links['twitter_screen_name']}")
        if links.get("telegram_channel_identifier"):
            link_cols[2].link_button("📱 Telegram", f"https://t.me/{links['telegram_channel_identifier']}")
        if links.get("github"):
            link_cols[3].link_button("💻 GitHub", links["github"])
        
        st.divider()
        
        # Hiring research (kept from original)
        st.markdown("## 🔎 Hiring Signals & Team Research")
        twitter_handle = links.get("twitter_screen_name")
        research_links = generate_research_links(details["name"], twitter_handle)
        
        for label, url in research_links.items():
            if url.startswith("http"):
                st.link_button(label, url)
            else:
                st.code(url, language="text")
        
        st.divider()
        
        # User inputs + assessment (updated)
        st.markdown("## 📋 Your Research Inputs (for personalized recommendation + platform fit)")
        
        with st.form(key="assessment_form"):
            i_col1, i_col2 = st.columns(2)
            with i_col1:
                stage = st.selectbox("Project Stage (your estimate)", ["Pre-seed / Testnet", "Seed", "Series A", "Listed / TGE done", "Growth / Scaling", "Unknown"], index=0)
                hiring_pot = st.select_slider("Hiring Potential (from research)", options=["Low", "Medium", "High"], value="Medium")
            with i_col2:
                team_size_est = st.number_input("Est. Core Team Size", min_value=1, max_value=100, value=8)
                raised_funding = st.number_input("Est. Total Raised (USD millions)", min_value=0.0, value=2.0, step=0.5)
            
            pain_points = st.text_area("Key pain points / opportunities observed", value="Need better GTM execution in emerging markets, structured BD pipeline, and data to prove real user traction to investors/partners.", height=80)
            
            submitted = st.form_submit_button("💾 Save Inputs & Calculate Full Recommendation (incl. Platform)", type="primary")
        
        if submitted or st.session_state.get("assessment_done"):
            user_inputs = {
                "stage": stage,
                "hiring_potential": hiring_pot,
                "team_size_est": team_size_est,
                "raised_funding_m": raised_funding,
                "pain_points": pain_points
            }
            st.session_state.user_inputs = user_inputs
            st.session_state.assessment_done = True
            
            assessment = assess_budget_fit(details, user_inputs)
            st.session_state.assessment = assessment
            
            st.markdown("### 🎯 Recommended Wyvernomics Package + Platform Fit")
            
            rec_col1, rec_col2 = st.columns([2, 3])
            with rec_col1:
                st.success(f"**{assessment['recommendation']}**")
                st.metric("Overall Fit Score", f"{assessment['score']}/10")
                st.metric("Growth Platform Fit", f"{assessment['platform_fit_score']}/7")
            with rec_col2:
                st.write(assessment['why'])
                for r in assessment['reasons']:
                    st.write(f"• {r}")
                
                st.markdown("**Platform-specific recommendation:**")
                st.info(assessment['platform_recommendation'])
                for pr in assessment.get('platform_reasons', []):
                    st.write(f"• {pr}")
            
            if st.button("✍️ Go to Pitch Builder with this project + recommendation", type="secondary"):
                st.session_state.pitch_project_id = coin_id
                st.info("Switch to the **Pitch Builder** tab — everything is pre-loaded.")
    
    # ========== TAB 4: PITCH BUILDER (Updated) ==========
    with tabs[3]:
        st.markdown("## ✍️ Customized Pitch & Outreach Generator")
        st.caption("Turn research + platform demo into high-conversion outreach. Now includes the Growth Intelligence Platform as a key differentiator.")
        
        default_name = st.session_state.get("current_project_name", "")
        default_id = st.session_state.get("current_project", "")
        
        pitch_col1, pitch_col2 = st.columns([1, 1])
        with pitch_col1:
            project_name = st.text_input("Project Name", value=default_name or "New Web3 Protocol")
        with pitch_col2:
            coin_id_for_pitch = st.text_input("CoinGecko ID (optional)", value=default_id)
        
        pitch_details = None
        if coin_id_for_pitch:
            pitch_details = fetch_coin_details(coin_id_for_pitch)
            if pitch_details:
                st.caption(f"Loaded rich data for {pitch_details['name']}")
        
        # Services selection (now includes platform options)
        st.markdown("**Services to offer (select all that apply):**")
        services = st.multiselect(
            "",
            ["KOL Pilot Package", "Custom KOL Package", "Silver BD Subscription", "Gold BD Subscription", 
             "Talent Placement / Team Sourcing", "Growth Intelligence Platform Subscription", 
             "Platform + KOL Pilot Bundle", "Combo: KOL + BD + Platform"],
            default=["KOL Pilot Package", "Growth Intelligence Platform Subscription"]
        )
        
        if not pitch_details:
            st.warning("No CoinGecko data loaded. Pitch will be more generic.")
            mc_manual = st.text_input("Est. Market Cap / FDV", value="$5-15M FDV")
            vol_manual = st.text_input("Est. 24h Volume", value="Strong / Growing")
        else:
            mc_manual = format_usd(pitch_details["market_data"].get("market_cap_usd"))
            vol_manual = format_usd(pitch_details["market_data"].get("total_volume_usd"))
        
        pain = st.text_area(
            "Observed pain points / opportunity (customize)",
            value=st.session_state.get("user_inputs", {}).get("pain_points", "scaling GTM execution in SEA/APAC and proving real user traction with data (not just vanity metrics)."),
            height=70
        )
        
        if st.button("🚀 Generate Professional Pitch", type="primary"):
            assessment = st.session_state.get("assessment", {
                "recommendation": ", ".join(services) if services else "Custom Package",
                "why": "Tailored to current traction and growth stage. Includes access to proprietary Growth Intelligence Platform.",
                "suggested_price_range": "Custom quote after discovery call"
            })
            
            user_in = st.session_state.get("user_inputs", {"stage": "early-mid stage", "hiring_potential": "Medium"})
            
            pitch_text = generate_pitch(
                project_name,
                pitch_details,
                assessment,
                {"stage": user_in.get("stage", "early-mid stage"), "pain_points": pain, "hiring_potential": user_in.get("hiring_potential", "Medium")},
                services
            )
            
            st.markdown("### 📨 Your Ready-to-Send Pitch")
            st.text_area("Copy & customize (ready for email/DM/LinkedIn):", value=pitch_text, height=480, key="generated_pitch")
            
            st.download_button(
                "📥 Download Pitch as .txt",
                data=pitch_text,
                file_name=f"wyvernomics_pitch_{project_name.lower().replace(' ', '_')}.txt",
                mime="text/plain"
            )
            
            st.success("Pitch generated! The platform mention builds huge credibility — prospects see we have proprietary tools, not just 'we will manage KOLs'.")
    
    # ========== TAB 5: MY PROSPECTS ==========
    with tabs[4]:
        st.markdown("## 📁 My Prospects Portfolio")
        st.caption("Track researched projects, package + platform recommendations, hiring potential, and outreach status. Export for CRM.")
        
        # Quick add current
        if st.session_state.get("current_project_name") and st.session_state.get("assessment"):
            if st.button("➕ Add Current Project to Portfolio"):
                new_prospect = {
                    "id": st.session_state.current_project,
                    "name": st.session_state.current_project_name,
                    "mc": st.session_state.get("assessment", {}).get("score", 0),
                    "recommended_package": st.session_state.assessment["recommendation"],
                    "platform_fit": st.session_state.assessment.get("platform_recommendation", ""),
                    "hiring_potential": st.session_state.user_inputs.get("hiring_potential", "Medium"),
                    "stage": st.session_state.user_inputs.get("stage", "Unknown"),
                    "notes": st.session_state.user_inputs.get("pain_points", ""),
                    "last_updated": datetime.now().isoformat(),
                    "status": "Researched - Not Contacted"
                }
                existing_ids = [p.get("id") for p in st.session_state.prospects]
                if new_prospect["id"] not in existing_ids:
                    st.session_state.prospects.append(new_prospect)
                    save_prospects(st.session_state.prospects)
                    st.success(f"Added {new_prospect['name']} to portfolio!")
                else:
                    st.info("Already in portfolio.")
        
        if not st.session_state.prospects:
            st.info("No prospects saved yet. Research projects and add them here after assessment.")
        else:
            prospects_df = pd.DataFrame(st.session_state.prospects)
            
            st.dataframe(
                prospects_df[["name", "recommended_package", "platform_fit", "hiring_potential", "stage", "status", "last_updated"]],
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("**Update Status or Notes**")
            selected_name = st.selectbox("Select prospect to update", options=[p["name"] for p in st.session_state.prospects])
            
            if selected_name:
                idx = next(i for i, p in enumerate(st.session_state.prospects) if p["name"] == selected_name)
                current = st.session_state.prospects[idx]
                
                new_status = st.selectbox("Status", ["Researched - Not Contacted", "DM Sent", "Platform Demo Done", "Call Scheduled", "Proposal Sent", "Interested", "Closed Won", "Not a Fit"], index=0)
                new_notes = st.text_area("Additional Notes", value=current.get("notes", ""), height=60)
                
                if st.button("Update Prospect"):
                    st.session_state.prospects[idx]["status"] = new_status
                    st.session_state.prospects[idx]["notes"] = new_notes
                    st.session_state.prospects[idx]["last_updated"] = datetime.now().isoformat()
                    save_prospects(st.session_state.prospects)
                    st.success("Updated!")
                    st.rerun()
            
            csv = prospects_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Portfolio as CSV (for CRM / Sheets)",
                data=csv,
                file_name=f"wyvernomics_prospects_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Footer
    st.divider()
    st.caption("Built for Wyvernomics Team • CoinGecko data + proprietary Growth Intelligence Platform demos • Not financial advice • Always DYOR")

if __name__ == "__main__":
    main()
