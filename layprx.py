import streamlit as st
import requests
import streamlit.components.v1 as components
from concurrent.futures import ThreadPoolExecutor, as_completed
import time as tm

# ========================
# CONFIG
# ========================
st.set_page_config(
    page_title="🔥 PROXY XOAY TOOL",
    page_icon="🔥",
    layout="wide"
)

# ========================
# STYLE
# ========================
st.markdown("""
<style>
html, body, [class*="css"] {
    background: linear-gradient(135deg,#0f0f0f,#1a1a1a);
    color: white;
    font-family: Arial;
}
h1 {
    text-align:center;
    color:#00ff99;
}
textarea {
    border-radius:12px !important;
}
.stButton>button {
    width:100%;
    background: linear-gradient(90deg,#00c853,#00e676);
    color:white;
    font-size:18px;
    font-weight:bold;
    border:none;
    border-radius:12px;
    padding:12px;
}
.stButton>button:hover{
    transform:scale(1.02);
}
</style>
""", unsafe_allow_html=True)

# ========================
# TITLE
# ========================
st.markdown("<h1>🔥 TOOL LẤY NHIỀU API PROXY XOAY 🔥</h1>", unsafe_allow_html=True)

# ========================
# INPUT
# ========================
cooldown = st.number_input("⏳ Thời gian chờ mặc định (giây)", min_value=1, value=8)

apis = st.text_area(
    "📌 Dán nhiều API (mỗi dòng 1 link)",
    height=220,
    placeholder="""https://api.proxyxoay.org/api/key_xoay.php?key=abc&live=5
https://api.proxyxoay.org/api/key_xoay.php?key=xyz&live=5"""
)

# ========================
# FUNCTION
# ========================
def get_proxy(url):
    try:
        r = requests.get(url, timeout=15)
        data = r.json()

        proxy = None

        if "proxyhttp" in data:
            proxy = data["proxyhttp"]
        elif "proxysocks5" in data:
            proxy = data["proxysocks5"]

        wait_time = data.get("next_allowed_in_seconds", cooldown)

        return proxy, wait_time

    except:
        return None, cooldown

# ========================
# BUTTON
# ========================
if st.button("🚀 LẤY PROXY NGAY"):

    lines = [x.strip() for x in apis.split("\n") if x.strip()]

    if not lines:
        st.warning("⚠️ Chưa nhập API")
        st.stop()

    raw_result = []
    wait_times = []
    progress = st.progress(0)

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(get_proxy, url): url for url in lines}

        done = 0
        total = len(lines)

        for future in as_completed(futures):
            proxy, wait_time = future.result()

            if proxy:
                raw_result.append(proxy)

            wait_times.append(wait_time)

            done += 1
            progress.progress(done / total)

    # ========================
    # UNIQUE
    # ========================
    total_proxy = len(raw_result)

    unique_result = list(dict.fromkeys(raw_result))
    unique_count = len(unique_result)

    duplicate_count = total_proxy - unique_count

    output = "\n".join(unique_result)

    # lấy thời gian từ API, nếu không có thì dùng cooldown
    max_wait = max(wait_times) if wait_times else cooldown

    # ========================
    # RESULT
    # ========================
    st.success("✅ Xử lý hoàn tất!")

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Tổng Proxy", total_proxy)
    col2.metric("✅ Unique", unique_count)
    col3.metric("♻️ Trùng", duplicate_count)

    # ========================
    # TIMER RESET MỖI LẦN BẤM
    # ========================
    timer_id = int(tm.time() * 1000)

    timer_html = f"""
    <style>
    .big-timer {{
        background: linear-gradient(90deg,#111,#1f1f1f);
        border: 3px solid #00ff99;
        border-radius: 18px;
        padding: 18px;
        text-align:center;
        box-shadow: 0 0 20px rgba(0,255,153,.35);
        margin-bottom:15px;
    }}

    .big-title {{
        font-size:24px;
        color:#ffffff;
        font-weight:bold;
        margin-bottom:8px;
    }}

    .big-count {{
        font-size:64px;
        font-weight:900;
        color:#00ff99;
        line-height:1;
    }}

    .big-note {{
        font-size:18px;
        color:#bbbbbb;
        margin-top:8px;
    }}
    </style>

    <div class="big-timer">
        <div class="big-title">⏳ THỜI GIAN CHỜ XOAY PROXY</div>
        <div class="big-count" id="count_{timer_id}">{max_wait}</div>
        <div class="big-note">Giây còn lại trước khi lấy proxy mới</div>
    </div>

    <script>
    (function(){{
        let time = {max_wait};
        let el = document.getElementById("count_{timer_id}");

        let timer = setInterval(function(){{
            time--;

            if(time > 0){{
                el.innerText = time;
            }} else {{
                clearInterval(timer);
                el.innerText = "OK";
                el.style.color = "#ffeb3b";
            }}

        }},1000);
    }})();
    </script>
    """

    components.html(timer_html, height=220)

    # ========================
    # OUTPUT
    # ========================
    st.markdown("### 📄 DANH SÁCH PROXY")
    st.text_area("", output, height=320)

    # ========================
    # COPY BUTTON
    # ========================
    copy_html = f"""
    <textarea id="copyText" style="display:none;">{output}</textarea>

    <button onclick="copyNow()" 
    style="
        width:100%;
        padding:12px;
        font-size:18px;
        font-weight:bold;
        background:#2962ff;
        color:white;
        border:none;
        border-radius:12px;
        cursor:pointer;
        margin-top:10px;
    ">
    📋 SAO CHÉP TOÀN BỘ
    </button>

    <script>
    function copyNow() {{
        var copyText = document.getElementById("copyText");
        copyText.style.display = "block";
        copyText.select();
        document.execCommand("copy");
        copyText.style.display = "none";
        alert("Đã sao chép!");
    }}
    </script>
    """

    components.html(copy_html, height=80)

    # ========================
    # DOWNLOAD
    # ========================
    st.download_button(
        "💾 TẢI FILE TXT",
        output,
        file_name="proxy_unique.txt"
    )