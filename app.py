import streamlit as st
import streamlit.components.v1 as components
import requests
import yfinance as yf
from datetime import datetime
import json

st.set_page_config(page_title="台股看盤", layout="centered", initial_sidebar_state="collapsed")

# ── CSS ──────────────────────────────────────────────────
CSS = r""" ... (你的 CSS 完全不變，我這裡省略以節省篇幅，請保留你原本的 CSS) ... """
st.markdown(CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# localStorage 橋接（不變）
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
            });
        })();
        </script>
        """,
        height=0,
    )

def ls_save(data_list):
    val = json.dumps(data_list, ensure_ascii=False)
    components.html(
        "<script>window.parent.postMessage({type: 'ls-save', value: " + json.dumps(val) + "}, '*');</script>",
        height=0,
    )

# ══════════════════════════════════════════════════════════
# 預設股票 + 你原本的所有函式（fetch_twse_name_list \~ kd_bar_html）全部保留
# ══════════════════════════════════════════════════════════
DEFAULT_STOCKS = [
    {"id": "2330", "name": "台積電"},
    {"id": "2002", "name": "中鋼"},
    {"id": "1326", "name": "台化"},
    {"id": "6505", "name": "台塑化"},
]

# ...（把你原本從 @st.cache_data 到 kd_bar_html 的所有函式貼在這裡，保持不變）...

# ══════════════════════════════════════════════════════════
# 修正後的 render_card（這是重點！）
# ══════════════════════════════════════════════════════════
def render_card(row):
    card_cls, price_cls, arrow = direction_class(row["change"])

    ohlc_items = ""
    for lbl, val in [("昨收", row["prev_close"]), ("開盤", row["open"]),
                     ("最高", row["high"]),       ("最低", row["low"])]:
        ohlc_items += f'''
        <div class="ohlc-item">
            <div class="ohlc-label">{lbl}</div>
            <div class="ohlc-val">{fmt(val)}</div>
        </div>
        '''

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

# 隱藏的 localStorage 橋接
ls_data = st.text_input("ls-bridge", value="", label_visibility="collapsed", key="ls-bridge-input")

# === 使用 session_state 讓新增/刪除穩定 ===
if "watchlist" not in st.session_state:
    st.session_state.watchlist = DEFAULT_STOCKS[:]

# 從 localStorage 載入（只在有資料且不同時更新）
if ls_data:
    try:
        loaded = json.loads(ls_data)
        if isinstance(loaded, list) and loaded != st.session_state.watchlist:
            st.session_state.watchlist = loaded
    except:
        pass

watchlist = st.session_state.watchlist

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
                    new_list = watchlist + [{"id": code, "name": name}]
                    st.session_state.watchlist = new_list
                    ls_save(new_list)
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
            new_list = [s for s in watchlist if s["id"] != stock["id"]]
            st.session_state.watchlist = new_list
            ls_save(new_list)
            st.rerun()

st.markdown('<div class="footer-note">資料來源：TWSE + Yahoo Finance<br>技術指標僅供參考，非投資建議</div>', unsafe_allow_html=True)