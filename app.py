import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import json

st.set_page_config(page_title="台股看盤", layout="centered")

LS_KEY = "twstock_wl_v4"

# =========================
# localStorage Bridge
# =========================
def ls_bridge():
    components.html(f"""
    <script>
    (function(){{
        const LS_KEY = "{LS_KEY}";

        function sendToStreamlit(val){{
            const input = window.parent.document.querySelector('input[aria-label="ls-bridge"]');
            if(!input) return;

            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, 'value'
            ).set;

            setter.call(input, val);
            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}

        // 等 DOM 穩定後再執行（關鍵）
        setTimeout(() => {{
            try {{
                const data = localStorage.getItem(LS_KEY);
                if(data) sendToStreamlit(data);
            }} catch(e) {{}}
        }}, 300);

        // 接收寫入
        window.addEventListener("message", (e) => {{
            if(e.data?.type === "ls-save"){{
                localStorage.setItem(LS_KEY, e.data.value);
            }}
        }});
    }})();
    </script>
    """, height=0)

def ls_save(data):
    val = json.dumps(data, ensure_ascii=False)
    components.html(f"""
    <script>
    window.parent.postMessage({{
        type: "ls-save",
        value: {json.dumps(val)}
    }}, "*");
    </script>
    """, height=0)

# =========================
# 啟動 bridge
# =========================
ls_bridge()

ls_data = st.text_input("ls-bridge", key="ls-bridge")

DEFAULT_STOCKS = [
    {"id": "2330", "name": "台積電"},
    {"id": "2002", "name": "中鋼"},
]

# =========================
# 初始化（修正版🔥）
# =========================
if "init_done" not in st.session_state:

    # 第一次沒有資料 → 等 JS
    if not ls_data:
        st.stop()

    try:
        st.session_state.watchlist = json.loads(ls_data)
    except:
        st.session_state.watchlist = DEFAULT_STOCKS

    st.session_state.init_done = True
    st.rerun()

# =========================
# 股票資料
# =========================
def fetch_price(stock_id):
    try:
        ticker = yf.Ticker(f"{stock_id}.TW")
        df = ticker.history(period="2d")
        if df.empty:
            return None, None
        return float(df["Close"].iloc[-1]), float(df["Close"].iloc[-2])
    except:
        return None, None

# =========================
# UI
# =========================
st.title("📈 台股看盤")

# 新增
new_id = st.text_input("輸入股票代碼")

if st.button("新增股票"):
    if new_id:
        if not any(s["id"] == new_id for s in st.session_state.watchlist):
            st.session_state.watchlist.append({
                "id": new_id,
                "name": new_id
            })
            ls_save(st.session_state.watchlist)
            st.rerun()

# =========================
# 顯示
# =========================
for i, stock in enumerate(st.session_state.watchlist):
    price, prev = fetch_price(stock["id"])

    if price and prev:
        change = price - prev
        pct = change / prev * 100
        color = "green" if change > 0 else "red" if change < 0 else "gray"

        st.markdown(f"""
        ### {stock['name']} ({stock['id']})
        <span style='color:{color};font-size:24px'>
        {price:.2f} ({change:+.2f}, {pct:+.2f}%)
        </span>
        """, unsafe_allow_html=True)
    else:
        st.write(f"{stock['id']} 無資料")

    # 刪除
    if st.button(f"刪除 {stock['id']}", key=f"del_{i}"):
        st.session_state.watchlist.pop(i)
        ls_save(st.session_state.watchlist)
        st.rerun()