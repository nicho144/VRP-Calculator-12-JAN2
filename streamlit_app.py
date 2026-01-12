import streamlit as st, pandas as pd, yfinance as yf, requests
from datetime import date, timedelta

st.set_page_config(page_title="VRP Feed", layout="centered")
st.title("Daily Volatility-Risk Premium (VRP)")
st.markdown("Updates 30 min after US close.  *VRP = IV – RV*")

@st.cache_data(ttl=60*60*4)
def fred(series: str) -> float:
    """Pull last observation from FRED JSON API."""
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {"series_id": series, "api_key": "DEMO_KEY", "file_type": "json", "limit": 1, "sort_order": "desc"}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        st.error(f"FRED error {r.status_code} for {series}")
        st.stop()
    latest = r.json()["observations"][0]["value"]
    return float(latest)

@st.cache_data(ttl=60*60*4)
def rv(tkr: str, days: int = 21) -> float:
    p = yf.download(tkr, start=START, interval="1d")["Adj Close"].dropna()
    return float(p.pct_change().rolling(days).std().iloc[-1] * (252**0.5))

START = (date.today() - timedelta(days=300)).isoformat()
pairs = {"Gold (GVZ)": ("GVZ", "GLD"),
         "S&P 500 (VIX)": ("VIXCLS", "SPY"),
         "10-Y Yield (TYNV)": ("TYNVOLIndex", "^TNX")}

if st.button("Refresh now"):
    st.cache_data.clear()

data = {name: {"IV": round(fred(sym), 2),
               "RV": round(rv(tkr), 2),
               "VRP": round(fred(sym) - rv(tkr), 2)}
        for name, (sym, tkr) in pairs.items()}
df = pd.DataFrame.from_dict(data, orient="index")
st.dataframe(df.style.highlight_max(axis=0, props="color:#00ff00"))
