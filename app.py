import streamlit as st
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time
import json

st.set_page_config(
    page_title="大師加持版",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── CSS (raw string 避免反斜線解析問題) ──────────────────
CSS = r"""
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
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebarNav"] { display: none !important; }

[data-testid="stAppViewBlockContainer"] {
    padding: 1rem 0.75rem 5rem !important;
    max-width: 480px !important;
    margin: 0 auto !important;
}

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
.app-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; color: #64748b;
    text-align: right; line-height: 1.6;
}
.live-dot {
    display: inline-block; width: 6px; height: 6px;
    border-radius: 50%; background: #22c55e; margin-right: 5px;
    animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:.4; transform:scale(.8); }
}

.add-section-title {
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #38bdf8; margin-bottom: 0.7rem;
}

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

[data-testid="stButton"] button {
    background: linear-gradient(135deg, #0ea5e9, #38bdf8) !important;
    color: #0a0d14 !important;
    font-family: 'Noto Sans TC', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.2rem !important;
    width: 100% !important;
    transition: opacity 0.2s !important;
}
[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

.stock-card {
    background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.1rem 1.1rem 0.9rem;
    margin-bottom: 0.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.stock-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent, #38bdf8);
    border-radius: 16px 16px 0 0;
}
.stock-card.up   { --accent: #22c55e; }
.stock-card.down { --accent: #ef4444; }
.stock-card.flat { --accent: #94a3b8; }

.card-top {
    display: flex; align-items: flex-start;
    justify-content: space-between; margin-bottom: 0.85rem;
}
.stock-name { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; line-height: 1.3; }
.stock-code { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #64748b; margin-top: 2px; }
.price-block { text-align: right; }
.price-main {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem; font-weight: 700; line-height: 1; color: #f8fafc;
}
.price-change {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem; font-weight: 700; margin-top: 3px;
}
.up-color   { color: #22c55e; }
.down-color { color: #ef4444; }
.flat-color { color: #94a3b8; }

.ohlc-row {
    display: grid; grid-template-columns: repeat(4,1fr);
    gap: 0.3rem; background: rgba(255,255,255,0.03);
    border-radius: 10px; padding: 0.55rem 0.5rem; margin-bottom: 0.85rem;
}
.ohlc-item { text-align: center; }
.ohlc-label {
    font-size: 0.6rem; color: #475569;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 3px;
}
.ohlc-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem; color: #cbd5e1; font-weight: 500;
}

.card-divider { height: 1px; background: rgba(255,255,255,0.05); margin: 0.75rem 0; }

.tech-section-title {
    font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: #475569; margin-bottom: 0.6rem;
}
.kd-row { display: flex; gap: 0.5rem; margin-bottom: 0.65rem; }
.kd-chip {
    flex: 1; background: rgba(255,255,255,0.04);
    border-radius: 8px; padding: 0.45rem 0.6rem; text-align: center;
}
.kd-chip-label { font-size: 0.6rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }
.kd-chip-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1rem; font-weight: 700; color: #e2e8f0; margin-top: 1px;
}
.kd-bar-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 99px; height: 4px; margin-top: 5px; overflow: hidden;
}
.kd-bar-fill {
    height: 100%; border-radius: 99px;
    background: var(--bar-color, #38bdf8);
    width: var(--bar-width, 50%);
}

.momentum-row {
    display: flex; align-items: center;
    justify-content: space-between;
    background: rgba(255,255,255,0.03);
    border-radius: 8px; padding: 0.4rem 0.65rem; margin-bottom: 0.65rem;
}
.momentum-label { font-size: 0.7rem; color: #64748b; }
.momentum-val { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; font-weight: 700; }

.signal-row {
    display: flex; gap: 0.5rem; flex-wrap: wrap;
    align-items: center; justify-content: space-between;
}
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.72rem; font-weight: 700;
    border-radius: 99px; padding: 0.3rem 0.75rem;
}
.badge-signal-buy   { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.badge-signal-sell  { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.badge-signal-watch { background: rgba(148,163,184,0.1); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2); }
.badge-trend-up     { background: rgba(251,146,60,0.12); color: #fb923c; border: 1px solid rgba(251,146,60,0.25); }
.badge-trend-down   { background: rgba(96,165,250,0.12); color: #60a5fa; border: 1px solid rgba(96,165,250,0.25); }

.no-data { font-size: 0.75rem; color: #475569; text-align: center; padding: 0.5rem; font-style: italic; }
.error-msg {
    font-size: 0.75rem; color: #f87171;
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.2);
    border-radius: 8px; padding: 0.5rem 0.75rem; margin-top: 0.5rem;
}
.success-msg {
    font-size: 0.75rem; color: #4ade80;
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 8px; padding: 0.5rem 0.75rem; margin-top: 0.5rem;
}
.card-gap { margin-bottom: 0.9rem; }
.footer-note { text-align: center; font-size: 0.65rem; color: #334155; margin-top: 1.5rem; line-height: 1.7; }
.element-container { margin-bottom: 0 !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# 預設股票 & 初始化
# ══════════════════════════════════════════════════════════
DEFAULT_STOCKS = [
    {"id": "2330", "name": "台積電"},
    {"id": "2002", "name": "中鋼"},
    {"id": "1326", "name": "台化"},
    {"id": "6505", "name": "台塑化"},
]
STORAGE_KEY = "wl"


def init_watchlist():
    if "watchlist" not in st.session_state:
        params = st.query_params
        if STORAGE_KEY in params:
            try:
                decoded = json.loads(params[STORAGE_KEY])
                if isinstance(decoded, list) and len(decoded) > 0:
                    st.session_state.watchlist = decoded
                    return
            except Exception:
                pass
        st.session_state.watchlist = DEFAULT_STOCKS.copy()


def persist_watchlist():
    st.query_params[STORAGE_KEY] = json.dumps(
        st.session_state.watchlist, ensure_ascii=False
    )


# ══════════════════════════════════════════════════════════
# 資料函式
# ══════════════════════════════════════════════════════════
def fetch_twse(stock_ids):
    ex_ch = "|".join([f"tse_{sid}.tw" for sid in stock_ids])
    url = (
        "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
        f"?ex_ch={ex_ch}&json=1"
    )
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return r.json().get("msgArray", [])
    except Exception:
        return []


def fetch_yf_hist(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        df = ticker.history(period="3mo")
        return None if df.empty else df
    except Exception:
        return None


def verify_stock(stock_id):
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    url = (
        "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
        f"?ex_ch=tse_{stock_id}.tw&json=1"
    )
    try:
        r = requests.get(url, headers=headers, timeout=8)
        arr = r.json().get("msgArray", [])
        if arr:
            return True, arr[0].get("n", stock_id)
    except Exception:
        pass
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        df = ticker.history(period="5d")
        if not df.empty:
            info = ticker.info
            name = info.get("shortName", info.get("longName", stock_id))
            for suffix in [" Corporation", " Co., Ltd.", " Co.,Ltd.", " Ltd."]:
                name = name.replace(suffix, "")
            return True, name
    except Exception:
        pass
    return False, ""


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
    except Exception:
        pass
    return yf_close


def calculate_kd(df, period=9):
    low_min  = df["Low"].rolling(window=period).min()
    high_max = df["High"].rolling(window=period).max()
    rsv = (df["Close"] - low_min) / (high_max - low_min) * 100
    df["K"] = rsv.ewm(com=2).mean()
    df["D"] = df["K"].ewm(com=2).mean()
    return df


def calculate_momentum(df, period=10):
    df["Momentum"] = df["Close"] - df["Close"].shift(period)
    return df


def analyze_signal(df):
    if len(df) < 2:
        return "觀望", "無法判斷"
    latest, prev = df.iloc[-1], df.iloc[-2]
    signal = "觀望"
    if prev["K"] < prev["D"] and latest["K"] > latest["D"]:
        signal = "買進 (黃金交叉)"
    elif prev["K"] > prev["D"] and latest["K"] < latest["D"]:
        signal = "賣出 (死亡交叉)"
    trend = "上升動能" if latest["Momentum"] > 0 else "下跌動能"
    return signal, trend


def get_stock_data(twse_data, stock):
    code, name = stock["id"], stock["name"]
    tw = next((x for x in twse_data if x["c"] == code), None)
    df = fetch_yf_hist(code)

    if df is not None and len(df) >= 2:
        prev_close = float(df["Close"].iloc[-2])
        open_price = float(df["Open"].iloc[-1])
        high       = float(df["High"].iloc[-1])
        low        = float(df["Low"].iloc[-1])
        yf_close   = float(df["Close"].iloc[-1])
    else:
        prev_close = open_price = high = low = yf_close = None

    price = get_realtime_price(tw, yf_close) if tw else yf_close

    if prev_close is None and tw:
        try:
            prev_close = float(tw.get("y") or 0)
        except Exception:
            prev_close = None

    if df is not None:
        df = calculate_kd(df)
        df = calculate_momentum(df)
        signal, trend = analyze_signal(df)
        latest = df.iloc[-1]
        k         = float(latest["K"])
        d         = float(latest["D"])
        momentum  = float(latest["Momentum"])
    else:
        signal = trend = "無資料"
        k = d = momentum = None

    change     = (price - prev_close) if (prev_close and price) else 0.0
    change_pct = (change / prev_close * 100) if prev_close else 0.0

    return {
        "name": name, "code": code,
        "price": price, "prev_close": prev_close,
        "open": open_price, "high": high, "low": low,
        "change": change, "change_pct": change_pct,
        "K": k, "D": d, "Momentum": momentum,
        "signal": signal, "trend": trend,
    }


# ══════════════════════════════════════════════════════════
# 輔助函式
# ══════════════════════════════════════════════════════════
def fmt(v, d=2):
    return f"{v:.{d}f}" if v is not None else "－"


def direction_class(change):
    if change > 0:  return "up",   "up-color",   "▲"
    if change < 0:  return "down", "down-color",  "▼"
    return "flat", "flat-color", "－"


def signal_badge_class(sig):
    if "買進" in sig: return "badge-signal-buy"
    if "賣出" in sig: return "badge-signal-sell"
    return "badge-signal-watch"


def trend_badge_class(trend):
    return "badge-trend-up" if "上升" in trend else "badge-trend-down"


def kd_bar_html(val, color):
    pct = min(max(val, 0), 100) if val is not None else 50
    return (
        '<div class="kd-bar-wrap">'
        '<div class="kd-bar-fill" style="'
        "--bar-width:" + f"{pct:.0f}%" + ";"
        "--bar-color:" + color + ";"
        '"></div>'
        '</div>'
    )


# ══════════════════════════════════════════════════════════
# 渲染單張卡片
# ══════════════════════════════════════════════════════════
def render_card(row, idx):
    card_cls, price_cls, arrow = direction_class(row["change"])

    ohlc_items = ""
    for lbl, val in [("昨收", row["prev_close"]), ("開盤", row["open"]),
                     ("最高", row["high"]),       ("最低", row["low"])]:
        ohlc_items += (
            '<div class="ohlc-item">'
            f'<div class="ohlc-label">{lbl}</div>'
            f'<div class="ohlc-val">{fmt(val)}</div>'
            '</div>'
        )

    if row["K"] is not None:
        kd_section = (
            '<div class="kd-row">'
            '<div class="kd-chip">'
            '<div class="kd-chip-label">K 值</div>'
            f'<div class="kd-chip-val">{fmt(row["K"])}</div>'
            + kd_bar_html(row["K"], "#38bdf8") +
            '</div>'
            '<div class="kd-chip">'
            '<div class="kd-chip-label">D 值</div>'
            f'<div class="kd-chip-val">{fmt(row["D"])}</div>'
            + kd_bar_html(row["D"], "#f472b6") +
            '</div>'
            '</div>'
        )
        mom_color = "#22c55e" if row["Momentum"] > 0 else "#ef4444"
        momentum_section = (
            '<div class="momentum-row">'
            '<span class="momentum-label">動能指標 (10日)</span>'
            f'<span class="momentum-val" style="color:{mom_color};">{fmt(row["Momentum"])}</span>'
            '</div>'
        )
        sig_text   = row["signal"]
        trend_text = row["trend"]
    else:
        kd_section = '<div class="no-data">歷史資料不足，無法計算技術指標</div>'
        momentum_section = ""
        sig_text   = "資料不足"
        trend_text = ""

    sig_cls = signal_badge_class(sig_text)
    trend_badge = ""
    if trend_text:
        trend_badge = f'<span class="badge {trend_badge_class(trend_text)}">{trend_text}</span>'

    change_str = (
        f"{arrow} {abs(row['change']):.2f} ({abs(row['change_pct']):.2f}%)"
        if row["change"] else "－"
    )

    st.markdown(
        f'<div class="stock-card {card_cls}">'
        '<div class="card-top">'
        '<div>'
        f'<div class="stock-name">{row["name"]}</div>'
        f'<div class="stock-code">{row["code"]} · TW</div>'
        '</div>'
        '<div class="price-block">'
        f'<div class="price-main">{fmt(row["price"])}</div>'
        f'<div class="price-change {price_cls}">{change_str}</div>'
        '</div>'
        '</div>'
        f'<div class="ohlc-row">{ohlc_items}</div>'
        '<div class="card-divider"></div>'
        '<div class="tech-section-title">技術指標</div>'
        f'{kd_section}'
        f'{momentum_section}'
        '<div class="signal-row">'
        '<div style="display:flex;gap:0.4rem;flex-wrap:wrap;">'
        f'<span class="badge {sig_cls}">{sig_text}</span>'
        f'{trend_badge}'
        '</div>'
        '</div>'
        '</div>'
        '<div class="card-gap"></div>',
        unsafe_allow_html=True,
    )

    if st.button(f"移除  {row['name']} ({row['code']})", key=f"del_{row['code']}_{idx}"):
        st.session_state.watchlist = [
            s for s in st.session_state.watchlist if s["id"] != row["code"]
        ]
        persist_watchlist()
        st.rerun()


# ══════════════════════════════════════════════════════════
# 主程式
# ══════════════════════════════════════════════════════════
init_watchlist()

if "add_msg"  not in st.session_state: st.session_state.add_msg  = ""
if "add_type" not in st.session_state: st.session_state.add_type = ""

now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

# 頂部標題
st.markdown(
    '<div class="app-header">'
    '<div class="app-title">📊 台股<span>看盤</span></div>'
    f'<div class="app-time"><span class="live-dot"></span>即時更新<br>{now}</div>'
    '</div>',
    unsafe_allow_html=True,
)

# 新增股票
with st.expander("➕ 新增關注股票", expanded=False):
    st.markdown(
        '<div class="add-section-title">輸入台股代碼（如：0050）</div>',
        unsafe_allow_html=True,
    )
    new_id = st.text_input(
        "股票代碼",
        placeholder="輸入代碼，例如 0050",
        label_visibility="collapsed",
        key="new_stock_input",
    )
    if st.button("查詢並加入", key="add_btn"):
        new_id_clean = new_id.strip()
        if not new_id_clean:
            st.session_state.add_msg  = "請輸入股票代碼"
            st.session_state.add_type = "err"
        elif any(s["id"] == new_id_clean for s in st.session_state.watchlist):
            st.session_state.add_msg  = f"{new_id_clean} 已在關注清單中"
            st.session_state.add_type = "err"
        else:
            with st.spinner("驗證股票代碼中…"):
                valid, name = verify_stock(new_id_clean)
            if valid:
                st.session_state.watchlist.append({"id": new_id_clean, "name": name})
                persist_watchlist()
                st.session_state.add_msg  = f"已加入 {name}（{new_id_clean}）"
                st.session_state.add_type = "ok"
                st.rerun()
            else:
                st.session_state.add_msg  = f"找不到代碼 {new_id_clean}，請確認是否為台股上市代碼"
                st.session_state.add_type = "err"

    if st.session_state.add_msg:
        css_cls = "success-msg" if st.session_state.add_type == "ok" else "error-msg"
        st.markdown(
            f'<div class="{css_cls}">{st.session_state.add_msg}</div>',
            unsafe_allow_html=True,
        )

# 空清單提示
if not st.session_state.watchlist:
    st.markdown(
        '<div style="text-align:center;padding:3rem 1rem;color:#475569;">'
        '<div style="font-size:2.5rem;margin-bottom:0.75rem;">📭</div>'
        '<div style="font-size:0.9rem;font-weight:700;color:#64748b;">關注清單是空的</div>'
        '<div style="font-size:0.75rem;margin-top:0.4rem;">點上方「新增關注股票」來加入</div>'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    stock_ids = [s["id"] for s in st.session_state.watchlist]
    twse_data = fetch_twse(stock_ids)
    rows = [get_stock_data(twse_data, s) for s in st.session_state.watchlist]
    for idx, row in enumerate(rows):
        render_card(row, idx)

# 頁尾
st.markdown(
    '<div class="footer-note">'
    "資料來源：TWSE 即時 API + Yahoo Finance<br>"
    "關注清單儲存於網址，加入書籤下次開啟即可還原<br>"
    "每 15 秒自動更新 ／ 僅供參考，不構成投資建議"
    "</div>",
    unsafe_allow_html=True,
)

time.sleep(15)
st.rerun()
