import streamlit as st, pandas as pd, pandas_datareader.data as web, yfinance as yf
from datetime import date, timedelta

st.set_page_config(page_title="VRP Feed", layout="centered")
st.title("Daily Volatility-Risk Premium (VRP)")
st.markdown("Updates 30 min after US close.  *VRP = IV – RV*")

@st.cache_data(ttl=60*60*4)   # 4-hour cache
def vrp(sym: str, tkr: str):
    iv = float(web.DataReader(sym, "fred", START, date.today()).dropna().iloc[-1])
    p  = yf.download(tkr, start=START, interval="1d")["Adj Close"].dropna()
    rv = float(p.pct_change().rolling(21).std().iloc[-1] * (252**0.5))
    return {"IV": round(iv,2), "RV": round(rv,2), "VRP": round(iv-rv,2)}

START = (date.today() - timedelta(days=300)).isoformat()
pairs = {"Gold (GVZ)": ("GVZ", "GLD"),
         "S&P 500 (VIX)": ("VIXCLS", "SPY"),
         "10-Y Yield (TYNV)": ("TYNVOLIndex", "^TNX")}

if st.button("Refresh now"):
    st.cache_data.clear()

data = {name: vrp(sym, tkr) for name, (sym, tkr) in pairs.items()}
df   = pd.DataFrame.from_dict(data, orient="index")
st.dataframe(df.style.highlight_max(axis=0, props="color:#00ff00"))