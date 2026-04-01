import streamlit as st
import streamlit.components.v1 as components
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time
import json

st.set_page_config(
    page_title="\u53f0\u80a1\u770b\u76e4",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# \u2500\u2500 \u5168\u57df\u6a23\u5f0f \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0d14 !important;
    color: #e2e8f0 !important;
    font-family: 'Noto Sans TC', sans-serif !important;
}
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #0f1a2e 0%, #0a0d14 60%) !important;
}
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stSidebarNav"] { display: none !important; }

[data-testid="stAppViewBlockContainer"] {
    padding: 1rem 0.75rem 5rem !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}

/* \u2500\u2500 \u9802\u90e8\u6a19\u984c \u2500\u2500 */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 1.25rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.1rem;
}
.app-title { font-size: 1.35rem; font-weight: 900; letter-spacing: -0.02em; color: #f8fafc; }
.app-title span { color: #38bdf8; }
.app-time { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #64748b; text-align: right; line-height: 1.6; }
.live-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #22c55e; margin-right: 5px; animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.8)} }

/* \u2500\u2500 \u65b0\u589e\u80a1\u7968\u5340\u584a \u2500\u2500 */
.add-section {
    background: linear-gradient(135deg, #111827, #0f172a);
    border: 1px dashed rgba(56,189,248,0.3);
    border-radius: 14px;
    padding: 1rem;
    margin-bottom: 1rem;
}
.add-section-title {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 0.7rem;
}

/* \u2500\u2500 Streamlit input \u7f8e\u5316 \u2500\u2500 */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 0.75rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(56,189,248,0.5) !important;
    box-shadow: 0 0 0 2px rgba(56,189,248,0.1) !important;
}
[data-testid="stTextInput"] label { display: none !important; }

/* \u2500\u2500 \u6309\u9215 \u2500\u2500 */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #0ea5e9, #38bdf8) !important;
    color: #0a0d14 !important;
    font-family: 'Noto Sans TC', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.2rem !important;
    transition: opacity 0.2s !important;
    width: 100% !important;
}
[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

/* \u2500\u2500 \u80a1\u7968\u5361\u7247 \u2500\u2500 */
.stock-card {
    background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.1rem 1.1rem 0.9rem;
    margin-bottom: 0.9rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.stock-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, #38bdf8);
    border-radius: 16px 16px 0 0;
}
.stock-card.up   { --accent: #22c55e; }
.stock-card.down { --accent: #ef4444; }
.stock-card.flat { --accent: #94a3b8; }

.card-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 0.85rem;
}
.stock-name { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; line-height: 1.3; }
.stock-code { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; margin-top: 2px; }
.price-block { text-align: right; }
.price-main { font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 700; line-height: 1; color: #f8fafc; }
.price-change { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; margin-top: 3px; }
.up-color   { color: #22c55e; }
.down-color { color: #ef4444; }
.flat-color { color: #94a3b8; }

.ohlc-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 0.3rem; background: rgba(255,255,255,0.03); border-radius: 10px; padding: 0.55rem 0.5rem; margin-bottom: 0.85rem; }
.ohlc-item { text-align: center; }
.ohlc-label { font-size: 0.6rem; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 3px; }
.ohlc-val { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #cbd5e1; font-weight: 500; }

.card-divider { height: 1px; background: rgba(255,255,255,0.05); margin: 0.75rem 0; }

.tech-section-title { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #475569; margin-bottom: 0.6rem; }
.kd-row { display: flex; gap: 0.5rem; margin-bottom: 0.65rem; }
.kd-chip { flex: 1; background: rgba(255,255,255,0.04); border-radius: 8px; padding: 0.45rem 0.6rem; text-align: center; }
.kd-chip-label { font-size: 0.6rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }
.kd-chip-val { font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 700; color: #e2e8f0; margin-top: 1px; }
.kd-bar-wrap { background: rgba(255,255,255,0.06); border-radius: 99px; height: 4px; margin-top: 5px; overflow: hidden; }
.kd-bar-fill { height: 100%; border-radius: 99px; background: var(--bar-color, #38bdf8); width: var(--bar-width, 50%); }

.momentum-row { display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.03); border-radius: 8px; padding: 0.4rem 0.65rem; margin-bottom: 0.65rem; }
.momentum-label { font-size: 0.7rem; color: #64748b; }
.momentum-val { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; }

.signal-row { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; justify-content: space-between; }
.badge { display: inline-flex; align-items: center; gap: 4px; font-size: 0.72rem; font-weight: 700; border-radius: 99px; padding: 0.3rem 0.75rem; }
.badge-signal-buy   { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.badge-signal-sell  { background: rgba(239,68,68,0.15);  color: #ef4444