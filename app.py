import streamlit as st
import streamlit.components.v1 as components
import requests
import yfinance as yf
from datetime import datetime
import time
import json

st.set_page_config(page_title="台股看盤", layout="centered")

# =========================================================
# 🔥 localStorage + 排序橋接
# =========================================================
LS_KEY = "twstock_wl_v3"

def ls_bridge():
    components.html(f"""
    <script>
    (function(){{
        const KEY = "{LS_KEY}";

        function sendToStreamlit(val){{
            const inputs = window.parent.document.querySelectorAll('input[data-testid="stTextInput"]');
            inputs.forEach(input => {{
                if (input.getAttribute('aria-label') === 'ls-bridge') {{
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'value'
                    ).set;
                    setter.call(input, val);
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }});
        }}

        // 初次載入
        const stored = localStorage.getItem(KEY);
        if (stored) sendToStreamlit(stored);

        // 接收寫入 & 排序
        window.addEventListener("message", (e) => {{
            if (e.data?.type === "ls-save") {{
                localStorage.setItem(KEY, e.data.value);
            }}
            if (e.data?.type === "sort-update") {{
                localStorage.setItem(KEY, e.data.value);
                sendToStreamlit(e.data.value);
            }}
        }});
    }})();
    </script>
    """, height=0)


def ls_save(data):
    if not data:
        return
    components.html(f"""
    <script>
    window.parent.postMessage({{
        type: "ls-save",
        value: {json.dumps(json.dumps(data, ensure_ascii=False))}
    }}, "*");
    </script>
    """, height=0)


# =========================================================
# 🔥 拖曳排序 UI（修正版）
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
        data.forEach((item) => {{
            const d = document.createElement("div");
            d.style.padding = "10px";
            d.style.marginBottom = "6px";
            d.style.background = "#111827";
            d.style.borderRadius = "10px";
            d.style.cursor = "grab";
            d.innerText = "☰ " + item.name + " (" + item.id + ")";
            el.appendChild(d);
        }});
    }}

    render();

    new Sortable(el, {{
        animation: 150,
        onEnd: function(){{
            const newList = [];
            const nodes = el.children;

            for (let i = 0; i < nodes.length; i++) {{
                const text = nodes[i].innerText;
                const match = text.match(/\\((\\d+)\\)/);
                if (match) {{
                    const id = match[1];
                    const found = data.find(x => x.id === id);
                    if (found) newList.push(found);
                }}
            }}

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
# API
# =========================================================
def fetch_twse(ids):
    ex = "|".join([f"tse_{i}.tw" for i in ids])
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex}&json=1"
    try:
        return requests.get(url, timeout=10).json().get("msgArray", [])
    except:
        return []

def fetch_price(code, tw):
    t = next((x for x in tw if x.get("c") == code), None)
    try:
        z = t.get("z")
        if z not in ["-", "", None]:
            return float(z)
    except:
        pass
    return None

# =========================================================
# 主程式
# =========================================================
ls_bridge()

ls_raw = st.text_input("ls-bridge", label_visibility="collapsed")

# ✅ 初始化（修正白畫面）
if "watchlist" not in st.session_state:
    if ls_raw:
        try:
            parsed = json.loads(ls_raw)
            if isinstance(parsed, list) and len(parsed) > 0:
                st.session_state.watchlist = parsed
            else:
                st.session_state.watchlist = DEFAULT_STOCKS.copy()
        except:
            st.session_state.watchlist = DEFAULT_STOCKS.copy()
    else:
        st.session_state.watchlist = DEFAULT_STOCKS.copy()

# ✅ 接收排序 / localStorage 更新
if ls_raw:
    try:
        parsed = json.loads(ls_raw)
        if isinstance(parsed, list):
            st.session_state.watchlist = parsed
            if len(parsed) > 0:
                ls_save(parsed)
    except:
        pass

# =========================================================
# UI
# =========================================================
st.title("📊 台股看盤")

# ➕ 新增
new = st.text_input("輸入股票代碼")
if st.button("加入"):
    if new and not any(s["id"] == new for s in st.session_state.watchlist):
        st.session_state.watchlist.append({"id": new, "name": new})
        ls_save(st.session_state.watchlist)
        st.rerun()

# 🔀 排序
st.subheader("🔀 拖曳排序")
sortable_list(st.session_state.watchlist)

# 📊 顯示
ids = [s["id"] for s in st.session_state.watchlist]
tw = fetch_twse(ids)

for s in st.session_state.watchlist:
    price = fetch_price(s["id"], tw)
    st.write(f"{s['name']} ({s['id']})：{price}")

# ⏱ 時間
st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

time.sleep(15)
st.rerun()