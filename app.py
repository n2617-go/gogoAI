import streamlit as st
import streamlit.components.v1 as components
import requests
import yfinance as yf
from datetime import datetime
import json

st.set_page_config(
    page_title="台股看盤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── CSS ──────────────────────────────────────────────────
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
    display: flex; align-items: center;
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
    align-items: center;
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
# localStorage 橋接
# ══════════════════════════════════════════════════════════
LS_KEY = "twstock_wl_v2"

def ls_bridge():
    components.html(
        """
        <script>
        (function(){
            var LS_KEY = '""" + LS_KEY + """';
            function injectToStreamlit(val) {
                var inputs = window.parent.document.querySelectorAll('input[data-testid="stTextInput"]');
                for (var i = 0; i < inputs.length; i++) {
                    if (inputs[i].id === 'ls-bridge-input' || inputs[i].getAttribute('aria-label') === 'ls-bridge') {
                        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        nativeInputValueSetter.call(inputs[i], val);
                        inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                        break;
                    }
                }
            }
            try {
                var stored = localStorage.getItem(LS_KEY);
                if (stored) { injectToStreamlit(stored); }
            } catch(e) {}
            window.addEventListener('message', function(e) {
                if (e.data && e.data.type === 'ls-save') {
                    try { localStorage.setItem(LS_KEY, e.data.value); } catch(err) {}
                }
                if (e.data && e.data.type === 'ls-delete') {
                    try { localStorage.removeItem(LS_KEY); } catch(err) {}
                }
            });
        })();
        </script>
        """,
        height=0,
    )

def ls_save(data_list):
    val = json.dumps(data_list, ensure_ascii=False)
    components.html(
        "<script>"
        "window.parent.postMessage({"
        "  type: 'ls-save',"
        "  value: " + json.dumps(val) +
        "}, '*');"
        "</script>",
        height=0,
    )

# ══════════════════════════════════════════════════════════
# 預設股票
# ══════════════════════════════════════════════════════════
DEFAULT_STOCKS = [
    {"id": "2330", "name": "台積電"},
    {"id": "2002", "name": "中鋼"},
    {"id": "1326", "name": "台化"},
    {"id": "6505", "name": "台塑化"},
]

# ══════════════════════════════════════════════════════════
# 以下為你原本的所有函式（已完整保留）
# ══════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def fetch_twse_name_list():
    url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.encoding = "big5"
        import re
        result = {}
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', r.text, re.S)
        for row in rows:
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
            if not tds:
                continue
            first = re.sub(r'<[^>]+>', '', tds[0]).strip()
            if '\u3000' in first:
                parts = first.split('\u3000')
                code = parts[0].strip()
                name = parts[1].strip() if len(parts) > 1 else ""
                if code and name and len(code) >= 4:
                    result[code] = name
        return result
    except Exception:
        return {}

def get_chinese_name(stock_id):
    name_map = fetch_twse_name_list()
    if stock_id in name_map:
        return name_map[stock_id]
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    try:
        url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw&json=1"
        r = requests.get(url, headers=headers, timeout=6)
        arr = r.json().get("msgArray", [])
        if arr and arr[0].get("n"):
            return arr[0]["n"]
    except Exception:
        pass
    try:
        url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=otc_{stock_id}.tw&json=1"
        r = requests.get(url, headers=headers, timeout=6)
        arr = r.json().get("msgArray", [])
        if arr and arr[0].get("n"):
            return arr[0]["n"]
    except Exception:
        pass
    return stock_id

def verify_stock(stock_id):
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://mis.twse.com.tw/"}
    try:
        url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_id}.tw&json=1"
        r = requests.get(url, headers=headers, timeout=8)
        arr = r.json().get("msgArray", [])
        if arr and arr[0].get("n"):
            return True, arr[0]["n"]
    except Exception:
        pass
    try:
        url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=otc_{stock_id}.tw&json=1"
        r = requests.get(url, headers=headers, timeout=8)
        arr = r.json().get("msgArray", [])
        if arr and arr[0].get("n"):
            return True, arr[0]["n"]
    except Exception:
        pass
    name_map = fetch_twse_name_list()
    if stock_id in name_map:
        return True, name_map[stock_id]
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        df = ticker.history(period="5d")
        if not df.empty:
            name = name_map.get(stock_id, stock_id)
            return True, name
    except Exception:
        pass
    return False, ""

def fetch_twse_realtime(stock_ids):
    parts = [f"tse_{sid}.tw" for sid in stock_ids]
    otc_parts = [f"otc_{sid}.tw" for sid in stock_ids]
    ex_ch = "|".join(parts + otc_parts)
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1"
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
    low_min = df["Low"].rolling(window=period).min()
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
    tw = next((x for x in twse_data if x.get("c") == code), None)
    df = fetch_yf_hist(code)

    if df is not None and len(df) >= 2:
        prev_close = float(df["Close"].iloc[-2])
        open_price = float(df["Open"].iloc[-1])
        high = float(df["High"].iloc[-1])
        low = float(df["Low"].iloc[-1])
        yf_close = float(df["Close"].iloc[-1])
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
        k = float(latest["K"])
        d = float(latest["D"])
        momentum = float(latest["Momentum"])
    else:
        signal = trend = "無資料"
        k = d = momentum = None

    change = (price - prev_close) if (prev_close and price) else 0.0
    change_pct = (change / prev_close * 100) if prev_close else 0.0

    return {
        "name": name, "code": code,
        "price": price, "prev_close": prev_close,
        "open": open_price, "high": high, "low": low,
        "change": change, "change_pct": change_pct,
        "K": k, "D": d, "Momentum": momentum,
        "signal": signal, "trend": trend,
    }

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
        f'<div class="kd-bar-fill" style="--bar-width:{pct:.0f}%; --bar-color:{color};">'
        '</div></div>'
    )

# ══════════════════════════════════════════════════════════
# 渲染卡片（已補完整）
# ══════════════════════════════════════════════════════════
def render_card(row):
    card_cls, price_cls, arrow = direction_class(row["change"])

    ohlc_items = ""
    for lbl, val in [("昨收", row["prev_close"]), ("開盤", row["open"]),
                     ("最高", row["high"]),       ("最低", row["low"])]:
        ohlc_items += f"""
        <div class="ohlc-item">
            <div class="ohlc-label">{lbl}</div>
            <div class="ohlc-val">{fmt(val)}</div>
        </div>
        """

    kd_k_color = "#22c55e" if row.get("K") and row["K"] > 50 else "#ef4444" if row.get("K") else "#94a3b8"
    kd_d_color = "#22c55e" if row.get("D") and row["D"] > 50 else "#ef4444" if row.get("D") else "#94a3b8"

    kd_html = f"""
    <div class="kd-row">
        <div class="kd-chip">
            <div class="kd-chip-label">K</div>
            <div class="kd-chip-val">{fmt(row.get("K"), 0)}</div>
            {kd_bar_html(row.get("K"), kd_k_color)}
        </div>
        <div class="kd-chip">
            <div class="kd-chip-label">D</div>
            <div class="kd-chip-val">{fmt(row.get("D"), 0)}</div>
            {kd_bar_html(row.get("D"), kd_d_color)}
        </div>
    </div>
    """

    momentum_html = f"""
    <div class="momentum-row">
        <div class="momentum-label">動能</div>
        <div class="momentum-val {'up-color' if row.get('Momentum', 0) > 0 else 'down-color' if row.get('Momentum', 0) < 0 else 'flat-color'}">
            {fmt(row.get("Momentum"), 0)}
        </div>
    </div>
    """

    signal_cls = signal_badge_class(row["signal"])
    trend_cls = trend_badge_class(row["trend"])

    signal_html = f"""
    <div class="signal-row">
        <div class="badge {signal_cls}"><span>{row["signal"]}</span></div>
        <div class="badge {trend_cls}"><span>{row["trend"]}</span></div>
    </div>
    """

    return f"""
    <div class="stock-card {card_cls}">
        <div class="card-top">
            <div>
                <div class="stock-name">{row["name"]}</div>
                <div class="stock-code">{row["code"]}</div>
            </div>
            <div class="price-block">
                <div class="price-main">{fmt(row["price"])}</div>
                <div class="price-change {price_cls}">
                    {arrow} {fmt(row["change"])} ({fmt(row["change_pct"], 2)}%)
                </div>
            </div>
        </div>
        <div class="ohlc-row">{ohlc_items}</div>
        <div class="card-divider"></div>
        <div class="tech-section-title">技術指標</div>
        {kd_html}
        {momentum_html}
        {signal_html}
    </div>
    """

# ===================== 主程式 =====================
ls_bridge()

# 隱藏的 localStorage 橋接 input
ls_data = st.text_input(
    "ls-bridge",
    value="",
    label_visibility="collapsed",
    key="ls-bridge-input"
)

# 載入自選股
watchlist = DEFAULT_STOCKS[:]
if ls_data:
    try:
        loaded = json.loads(ls_data)
        if isinstance(loaded, list):
            watchlist = loaded
    except:
        pass

# 抓即時資料
stock_ids = [s["id"] for s in watchlist]
twse_data = fetch_twse_realtime(stock_ids)

# 標題
st.markdown(f"""
<div class="app-header">
    <div class="app-title">台股看盤 <span>即時</span></div>
    <div class="app-time">
        <span class="live-dot"></span>
        {datetime.now().strftime("%H:%M:%S")}
    </div>
</div>
""", unsafe_allow_html=True)

# ── 新增股票 ─────────────────────────────────────
st.markdown('<div class="add-section-title">新增自選股</div>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    new_code = st.text_input("股票代碼", placeholder="例如：2330", key="new_code_input")
with col2:
    if st.button("＋ 新增", use_container_width=True):
        code = new_code.strip()
        if code:
            valid, name = verify_stock(code)
            if valid:
                if not any(s["id"] == code for s in watchlist):
                    watchlist.append({"id": code, "name": name})
                    ls_save(watchlist)
                    st.success(f"✅ 已新增 {name}（{code}）")
                    st.rerun()
                else:
                    st.warning("此股票已在自選股中")
            else:
                st.error("❌ 找不到此股票代碼")

# ── 自選股列表 ─────────────────────────────────────
st.markdown(f'<div class="add-section-title">我的自選股（{len(watchlist)} 檔）</div>', unsafe_allow_html=True)

if not watchlist:
    st.markdown('<div class="no-data">目前沒有自選股</div>', unsafe_allow_html=True)

for stock in watchlist[:]:
    row = get_stock_data(twse_data, stock)

    col_card, col_del = st.columns([9, 1])
    with col_card:
        st.markdown(render_card(row), unsafe_allow_html=True)
    with col_del:
        if st.button("×", key=f"del_{stock['id']}", help="刪除此股票"):
            watchlist = [s for s in watchlist if s["id"] != stock["id"]]
            ls_save(watchlist)
            st.rerun()

st.markdown('<div class="footer-note">資料來源：TWSE + Yahoo Finance<br>技術指標僅供參考，非投資建議</div>', unsafe_allow_html=True)