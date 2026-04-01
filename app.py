import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time

st.set_page_config(
    page_title="大師加持開發版（v2）",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── 全域樣式 ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap');

/* 全域重設 */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0d14 !important;
    color: #e2e8f0 !important;
    font-family: 'Noto Sans TC', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, #0f1a2e 0%, #0a0d14 60%) !important;
}

/* 隱藏 Streamlit 預設元素 */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stSidebarNav"] { display: none !important; }

[data-testid="stAppViewBlockContainer"] {
    padding: 1rem 0.75rem 4rem !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}

/* ── 頂部標題 ── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.25rem;
}
.app-title {
    font-size: 1.35rem;
    font-weight: 900;
    letter-spacing: -0.02em;
    color: #f8fafc;
}
.app-title span { color: #38bdf8; }
.app-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #64748b;
    text-align: right;
    line-height: 1.6;
}
.live-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22c55e;
    margin-right: 5px;
    animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.4; transform: scale(0.8); }
}

/* ── 股票卡片 ── */
.stock-card {
    background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.1rem 1.1rem 0.9rem;
    margin-bottom: 0.9rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    transition: border-color 0.2s;
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

/* 卡片頂部：名稱 + 價格 */
.card-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 0.85rem;
}
.stock-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1.3;
}
.stock-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 2px;
}
.price-block { text-align: right; }
.price-main {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    line-height: 1;
    color: #f8fafc;
}
.price-change {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
    margin-top: 3px;
}
.up-color   { color: #22c55e; }
.down-color { color: #ef4444; }
.flat-color { color: #94a3b8; }

/* OHLC 列 */
.ohlc-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.3rem;
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 0.55rem 0.5rem;
    margin-bottom: 0.85rem;
}
.ohlc-item { text-align: center; }
.ohlc-label {
    font-size: 0.6rem;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 3px;
}
.ohlc-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #cbd5e1;
    font-weight: 500;
}

/* 分隔線 */
.card-divider {
    height: 1px;
    background: rgba(255,255,255,0.05);
    margin: 0.75rem 0;
}

/* 技術指標區 */
.tech-section-title {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.6rem;
}
.kd-row {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.65rem;
}
.kd-chip {
    flex: 1;
    background: rgba(255,255,255,0.04);
    border-radius: 8px;
    padding: 0.45rem 0.6rem;
    text-align: center;
}
.kd-chip-label {
    font-size: 0.6rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.kd-chip-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-top: 1px;
}

/* KD 進度條 */
.kd-bar-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 99px;
    height: 4px;
    margin-top: 5px;
    overflow: hidden;
}
.kd-bar-fill {
    height: 100%;
    border-radius: 99px;
    background: var(--bar-color, #38bdf8);
    width: var(--bar-width, 50%);
    transition: width 0.5s ease;
}

/* 動能 */
.momentum-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    padding: 0.4rem 0.65rem;
    margin-bottom: 0.65rem;
}
.momentum-label { font-size: 0.7rem; color: #64748b; }
.momentum-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    font-weight: 700;
}

/* 訊號徽章 */
.signal-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.72rem;
    font-weight: 700;
    border-radius: 99px;
    padding: 0.3rem 0.75rem;
}
.badge-signal-buy    { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.badge-signal-sell   { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.badge-signal-watch  { background: rgba(148,163,184,0.1); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2); }
.badge-trend-up      { background: rgba(251,146,60,0.12); color: #fb923c; border: 1px solid rgba(251,146,60,0.25); }
.badge-trend-down    { background: rgba(96,165,250,0.12); color: #60a5fa; border: 1px solid rgba(96,165,250,0.25); }

/* 無資料狀態 */
.no-data {
    font-size: 0.75rem;
    color: #475569;
    text-align: center;
    padding: 0.5rem;
    font-style: italic;
}

/* 底部說明 */
.footer-note {
    text-align: center;
    font-size: 0.65rem;
    color: #334155;
    margin-top: 1.5rem;
    line-height: 1.7;
}

/* Streamlit dataframe 隱藏 */
[data-testid="stDataFrameResizable"] { display: none !important; }

/* 隱藏所有 st.write 預設邊距 */
.element-container { margin-bottom: 0 !important; }
</style>
""", unsafe_allow_html=True)

stocks = [
    {"id": "2330", "name": "台積電"},
    {"id": "2002", "name": "中鋼"},
    {"id": "1326", "name": "台化"},
    {"id": "6505", "name": "台塑化"}
]

# ── 資料函式 ──────────────────────────────────────────────
def fetch_twse():
    ex_ch = "|".join([f"tse_{s['id']}.tw" for s in stocks])
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json().get("msgArray", [])
    except:
        return None

def fetch_yf_hist(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        df = ticker.history(period="3mo")
        return None if df.empty else df
    except:
        return None

def get_realtime_price(tw, yf_close):
    try:
        z = tw.get("z")
        if z not in ["-", "", None, "0"]:
            return float(z)
        b = tw.get("b")
        if b:
            return float(b.split("_")[0])
        a = tw.get("a")
        if a:
            return float(a.split("_")[0])
    except:
        pass
    return yf_close

def calculate_kd(df, period=9):
    low_min  = df['Low'].rolling(window=period).min()
    high_max = df['High'].rolling(window=period).max()
    rsv = (df['Close'] - low_min) / (high_max - low_min) * 100
    df['K'] = rsv.ewm(com=2).mean()
    df['D'] = df['K'].ewm(com=2).mean()
    return df

def calculate_momentum(df, period=10):
    df['Momentum'] = df['Close'] - df['Close'].shift(period)
    return df

def analyze_signal(df):
    if len(df) < 2:
        return "觀望", "無法判斷"
    latest, prev = df.iloc[-1], df.iloc[-2]
    signal = "觀望"
    if prev['K'] < prev['D'] and latest['K'] > latest['D']:
        signal = "📈 買進（黃金交叉）"
    elif prev['K'] > prev['D'] and latest['K'] < latest['D']:
        signal = "📉 賣出（死亡交叉）"
    trend = "🔥 上升動能" if latest['Momentum'] > 0 else "❄️ 下跌動能"
    return signal, trend

def get_stock_data(twse_data, stock):
    code, name = stock["id"], stock["name"]
    tw = next((x for x in twse_data if x["c"] == code), None)
    df = fetch_yf_hist(code)

    if df is not None and len(df) >= 2:
        prev_close = df["Close"].iloc[-2]
        open_price = df["Open"].iloc[-1]
        high = df["High"].iloc[-1]
        low  = df["Low"].iloc[-1]
        yf_close = df["Close"].iloc[-1]
    else:
        prev_close = open_price = high = low = yf_close = None

    price = get_realtime_price(tw, yf_close) if tw else yf_close

    if prev_close is None and tw:
        prev_close = float(tw.get("y") or 0)

    if df is not None:
        df = calculate_kd(df)
        df = calculate_momentum(df)
        signal, trend = analyze_signal(df)
        latest = df.iloc[-1]
        k, d, momentum = latest["K"], latest["D"], latest["Momentum"]
    else:
        signal = trend = "無資料"
        k = d = momentum = None

    change     = price - prev_close if prev_close and price else 0
    change_pct = (change / prev_close * 100) if prev_close else 0

    return {
        "name": name, "code": code,
        "price": price, "prev_close": prev_close,
        "open": open_price, "high": high, "low": low,
        "change": change, "change_pct": change_pct,
        "K": k, "D": d, "Momentum": momentum,
        "signal": signal, "trend": trend
    }

# ── 輔助：格式化數字 ──────────────────────────────────────
def fmt(v, d=2):
    return f"{v:.{d}f}" if v is not None else "－"

def direction_class(change):
    if change > 0:   return "up",   "up-color",   "▲"
    if change < 0:   return "down", "down-color",  "▼"
    return "flat", "flat-color", "－"

def signal_badge_class(signal):
    if "買進" in signal: return "badge-signal-buy"
    if "賣出" in signal: return "badge-signal-sell"
    return "badge-signal-watch"

def trend_badge_class(trend):
    return "badge-trend-up" if "上升" in trend else "badge-trend-down"

# ── 主流程 ────────────────────────────────────────────────
twse_data = fetch_twse() or []
rows = [get_stock_data(twse_data, s) for s in stocks]
now  = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

# ── 頂部標題 ──────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div class="app-title">📊 大師加持<span>開發版v2</span></div>
  <div class="app-time">
    <span class="live-dot"></span>即時更新<br>{now}
  </div>
</div>
""", unsafe_allow_html=True)

# ── 股票卡片 ──────────────────────────────────────────────
for row in rows:
    card_cls, price_cls, arrow = direction_class(row["change"])

    # OHLC 格式
    ohlc_html = "".join([
        f'<div class="ohlc-item"><div class="ohlc-label">{lbl}</div>'
        f'<div class="ohlc-val">{fmt(val)}</div></div>'
        for lbl, val in [("昨收", row["prev_close"]),
                         ("開盤", row["open"]),
                         ("最高", row["high"]),
                         ("最低", row["low"])]
    ])

    # KD 進度條
    def kd_bar(val, color):
        pct = min(max(val, 0), 100) if val is not None else 50
        return f'<div class="kd-bar-wrap"><div class="kd-bar-fill" style="--bar-width:{pct:.0f}%;--bar-color:{color};"></div></div>'

    kd_html = ""
    momentum_html = ""
    tech_section_title = ""
    if row["K"] is not None:
        tech_section_title = '<div class="tech-section-title">技術指標</div>'
        k_bar = kd_bar(row["K"], "#38bdf8")
        d_bar = kd_bar(row["D"], "#f472b6")
        kd_html = f"""
<div class="kd-row">
  <div class="kd-chip">
    <div class="kd-chip-label">K 值</div>
    <div class="kd-chip-val">{fmt(row["K"])}</div>
    {k_bar}
  </div>
  <div class="kd-chip">
    <div class="kd-chip-label">D 值</div>
    <div class="kd-chip-val">{fmt(row["D"])}</div>
    {d_bar}
  </div>
</div>"""
        mom_color = "#22c55e" if row["Momentum"] > 0 else "#ef4444"
        momentum_html = f"""
<div class="momentum-row">
  <span class="momentum-label">動能指標 (10日)</span>
  <span class="momentum-val" style="color:{mom_color};">{fmt(row["Momentum"])}</span>
</div>"""
    else:
        tech_section_title = '<div class="tech-section-title">技術指標</div>'
        kd_html = '<div class="no-data">歷史資料不足，無法計算技術指標</div>'

    # 訊號徽章
    sig_cls   = signal_badge_class(row["signal"])
    trend_cls = trend_badge_class(row["trend"])
    sig_text  = row["signal"] if row["K"] is not None else "資料不足"
    trend_text = row["trend"] if row["K"] is not None else ""

    change_str = f"{arrow} {abs(row['change']):.2f} ({abs(row['change_pct']):.2f}%)" \
                 if row["change"] else "－"

    price_str = fmt(row["price"])

    st.markdown(f"""
<div class="stock-card {card_cls}">
  <!-- 頂部：名稱 & 價格 -->
  <div class="card-top">
    <div>
      <div class="stock-name">{row['name']}</div>
      <div class="stock-code">{row['code']} · TW</div>
    </div>
    <div class="price-block">
      <div class="price-main">{price_str}</div>
      <div class="price-change {price_cls}">{change_str}</div>
    </div>
  </div>

  <!-- OHLC -->
  <div class="ohlc-row">{ohlc_html}</div>

  <div class="card-divider"></div>

  <!-- 技術指標 -->
  {tech_section_title}
  {kd_html}
  {momentum_html}

  <!-- 訊號 -->
  <div class="signal-row">
    <span class="badge {sig_cls}">{sig_text}</span>
    {"" if not trend_text else f'<span class="badge {trend_cls}">{trend_text}</span>'}
  </div>
</div>
""", unsafe_allow_html=True)

# ── 頁尾 ─────────────────────────────────────────────────
st.markdown("""
<div class="footer-note">
  資料來源：TWSE 即時 API ＋ Yahoo Finance<br>
  每 15 秒自動更新 ／ 僅供參考，不構成投資建議
</div>
""", unsafe_allow_html=True)

time.sleep(15)
st.rerun()
