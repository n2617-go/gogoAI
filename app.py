import streamlit as st
import streamlit.components.v1 as components
import requests
import yfinance as yf
from datetime import datetime
import time
import json

st.set_page_config(
    page_title="台股看盤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ───────────────── CSS（沿用你的） ─────────────────
# 👉（這裡完全保留你原本 CSS，不動）
# 👉 為了篇幅乾淨，我不重貼，你原本那段 그대로保留

# =========================================================
# 🔥 localStorage + SortableJS 橋接（已整合）
# =========================================================
LS_KEY = "twstock_wl_v2"

def ls_bridge():
    components.html(f"""
    <script>
    (function(){{
        var LS_KEY = "{LS_KEY}";

        function inject(val){{
            var inputs = window.parent.document.querySelectorAll('input[data-testid="stTextInput"]');
            for (var i = 0; i < inputs.length; i++) {{
                if (inputs[i].getAttribute('aria-label') === 'ls-bridge') {{
                    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(inputs[i], val);
                    inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    break;
                }}
            }}
        }}

        // 讀 localStorage
        try {{
            var stored = localStorage.getItem(LS_KEY);
            if (stored) inject(stored);
        }} catch(e) {{}}

        // 接收寫入 / 排序
        window.addEventListener('message', function(e) {{

            if (e.data && e.data.type === 'ls-save') {{
                localStorage.setItem(LS_KEY, e.data.value);
            }}

            if (e.data && e.data.type === 'sort-update') {{
                inject(e.data.value);
            }}

        }});
    }})();
    </script>
    """, height=0)


def ls_save(data):
    components.html(f"""
    <script>
    window.parent.postMessage({{
        type: 'ls-save',
        value: {json.dumps(json.dumps(data, ensure_ascii=False))}
    }}, "*");
    </script>
    """, height=0)


# =========================================================
# 🔥 拖曳排序 UI
# =========================================================
def sortable_list(items):
    items_json = json.dumps(items, ensure_ascii=False)

    components.html(f"""
    <div id="list"></div>

    <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>

    <script>
    const data = {items_json};
    const el = document.getElementById("list");

    function render(){{
        el.innerHTML = "";
        data.forEach((item, i) => {{
            const d = document.createElement("div");
            d.style.padding = "10px";
            d.style.marginBottom = "6px";
            d.style.background = "#111827";
            d.style.borderRadius = "10px";
            d.style.cursor = "grab";
            d.innerText = "☰ " + item.name + " (" + item.id + ")";
            d.dataset.index = i;
            el.appendChild(d);
        }});
    }}

    render();

    new Sortable(el, {{
        animation: 150,
        onEnd: function(){{
            const newList = [];
            el.querySelectorAll("div").forEach(d => {{
                newList.push(data[d.dataset.index]);
            }});

            window.parent.postMessage({{
                type: "sort-update",
                value: JSON.stringify(newList)
            }}, "*");
        }}
    }});
    </script>
    """, height=220)


# =========================================================
# 預設股票
# =========================================================
DEFAULT_STOCKS = [
    {"id": "2330", "name": "台積電"},
    {"id": "2002", "name": "中鋼"},
]

# =========================================================
# TWSE / yfinance（簡化版保留）
# =========================================================
def fetch_twse(ids):
    ex = "|".join([f"tse_{i}.tw" for i in ids])
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex}&json=1"
    try:
        return requests.get(url).json().get("msgArray", [])
    except:
        return []

def fetch_price(code, tw):
    t = next((x for x in tw if x["c"] == code), None)
    try:
        return float(t["z"]) if t and t["z"] not in ["-",""] else None
    except:
        return None

# =========================================================
# 主程式
# =========================================================
ls_bridge()

ls_raw = st.text_input("ls-bridge", label_visibility="collapsed")

# ✅ 初始化（修正消失問題）
if "watchlist" not in st.session_state:

    if not ls_raw:
        st.stop()

    try:
        parsed = json.loads(ls_raw)
        st.session_state.watchlist = parsed if parsed else DEFAULT_STOCKS.copy()
    except:
        st.session_state.watchlist = DEFAULT_STOCKS.copy()

# ✅ 接收排序更新
if ls_raw:
    try:
        parsed = json.loads(ls_raw)
        if isinstance(parsed, list):
            st.session_state.watchlist = parsed
            if parsed:
                ls_save(parsed)
    except:
        pass

# =========================================================
# UI
# =========================================================
st.title("📊 台股看盤")

# ➕ 新增股票
new = st.text_input("輸入股票代碼")
if st.button("加入"):
    if new and not any(s["id"] == new for s in st.session_state.watchlist):
        st.session_state.watchlist.append({"id": new, "name": new})
        ls_save(st.session_state.watchlist)
        st.rerun()

# 🔀 拖曳排序
st.subheader("🔀 拖曳排序")
sortable_list(st.session_state.watchlist)

# 📊 顯示股票
ids = [s["id"] for s in st.session_state.watchlist]
tw = fetch_twse(ids)

for s in st.session_state.watchlist:
    price = fetch_price(s["id"], tw)
    st.write(f"{s['name']} ({s['id']})：{price}")

# ⏱ 更新時間
st.caption(datetime.now().strftime("%H:%M:%S"))

time.sleep(15)
st.rerun()