import streamlit as st
import smtplib
import re
import time
import uuid
from email.message import EmailMessage
from pathlib import Path
from PIL import Image
import streamlit.components.v1 as components

# ==========================================
# 1. 頁面設定與氛圍
# ==========================================
st.set_page_config(
    page_title="牠眼中的 他眼中的牠",
    page_icon="🐱",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    .stApp { background-color: #2F5245; }

    h1, h2, p, div, span, label, li {
        color: #F0F0F0 !important;
        font-family: "Microsoft JhengHei", sans-serif;
    }
    
    /* 專門設定 h3 (角色名字) 的樣式：橘金色、字體加大 */
    h3 {
        color: #E89B3D !important;
        font-family: "Microsoft JhengHei", sans-serif;
        font-size: 1.3rem !important;
        margin-bottom: 0.5rem !important;
        padding-top: 0.5rem !important;
    }

    /* 調整對話文字行距 */
    div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        line-height: 1.7;
        margin-bottom: 2px; 
    }

    div[data-testid="stChatInput"] {
        background: rgba(0,0,0,0.25);
        border-radius: 14px;
    }

    div[data-testid="stTextInput"] label { color: #E89B3D !important; }
    div.stButton > button { border-radius: 14px; }
</style>
""",
    unsafe_allow_html=True,
)

APP_DIR = Path(__file__).parent
IMG_DIR = APP_DIR / "images"
FALLBACK_DIR = APP_DIR / "fallback_messages"
FALLBACK_DIR.mkdir(exist_ok=True)

# ==========================================
# 3. 功能函式
# ==========================================
def _is_valid_email(email: str) -> bool:
    if not email: return False
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))

def send_email(display_name: str, email: str, payload: str) -> bool:
    if "email" not in st.secrets: return False
    sender = st.secrets["email"].get("sender", "").strip()
    password = st.secrets["email"].get("password", "").strip()
    receiver = st.secrets["email"].get("receiver", "").strip()
    
    msg = EmailMessage()
    msg["Subject"] = f"【展覽留言】{display_name} 在「牠眼中的...」留下了視角"
    msg["From"] = f"展覽視角收集器 <{sender}>"
    msg["To"] = receiver

    recipients = [receiver]
    if email and _is_valid_email(email):
        msg["Cc"] = email
        msg["Reply-To"] = email
        recipients.append(email)

    body = f"奈可可 您好，\n\n在「牠眼中的 他眼中的牠」展覽現場，\n{display_name} ({email or '未留信箱'}) 留下了這段話：\n\n---------------------------\n{payload}\n---------------------------\n\n(此信件由 Streamlit 自動傳送)"
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender, password)
            server.send_message(msg, from_addr=sender, to_addrs=recipients)
        return True
    except:
        return False

def show_image(path: Path):
    if path.exists():
        st.image(Image.open(path), use_container_width=True)

# ==========================================
# 4. 狀態管理
# ==========================================
if "stage" not in st.session_state: st.session_state.stage = 0
if "scroll_target" not in st.session_state: st.session_state.scroll_target = None
if "draft_name" not in st.session_state: st.session_state.draft_name = ""
if "draft_email" not in st.session_state: st.session_state.draft_email = ""
if "draft_1" not in st.session_state: st.session_state.draft_1 = ""
if "draft_2" not in st.session_state: st.session_state.draft_2 = ""

# ==========================================
# 5. UI 流程
# ==========================================
st.title("🐱 牠眼中的 他眼中的牠")
st.caption("生活在他方｜夜貓店 Elsewhere Cafe | 2026/1/1 - 1/31")

# --- 階段 0: 花娜說 ---
with st.chat_message("assistant", avatar="🐱"):
    st.markdown("### 三花貓 花娜 說：")
    
    st.write("你看見我了嗎？")
    st.write("我是被凝視的「牠」，")
    st.write("也是凝視著你的「牠」。")
    
    show_image(IMG_DIR / "poster_vertical.jpg")
    
    st.write("奈可可 用畫筆記下了這個瞬間。")
    st.write("在這個空間裡，")
    st.write("我們是怎麼互相觀看的？")

if st.session_state.stage == 0:
    if st.button("繼續走入畫中...", type="primary"):
        st.session_state.stage = 1
        st.session_state.scroll_target = "puff-start"
        st.rerun()

# --- 階段 1: 泡芙說 ---
if st.session_state.stage >= 1:
    # 這裡埋設錨點 id="puff-start"
    st.markdown('<div id="puff-start" style="padding-top: 20px;"></div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant", avatar="🐱"):
        st.markdown("### 橘白貓 泡芙 說：")
        
        st.write("他眼中有我，")
        st.write("我眼中有橘子，")
        st.write("那你眼中看到了什麼？")
        
        show_image(IMG_DIR / "poster_horizontal.jpg")
        st.markdown("---")
        
        st.write("我想幫你把這份視角，傳遞給奈可可。")
        st.write(" ")
        st.write("若是願意，請留下你的稱呼；")
        st.write("若想收到這封信的備份（或期待回信），")
        st.write("也可以留下信箱。")
        st.write(" ")
        st.write("展覽結束後會在所有留言裡")
        st.write("隨機抽出三位，")
        st.write("可以獲得奈可可親筆創作小禮🎁。")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            visitor_name = st.text_input("你的稱呼 (例如：夜貓常客)", key="v_name")
        with col2:
            visitor_email = st.text_input("你的信箱 (選填)", key="v_email")

    if st.session_state.stage == 1:
        user_input_1 = st.chat_input("寫下你眼中的世界...", key="chat1")
        if user_input_1:
            st.session_state.draft_name = visitor_name.strip() if visitor_name else "匿名訪客"
            st.session_state.draft_email = (visitor_email or "").strip()
            st.session_state.draft_1 = user_input_1.strip()
            st.session_state.stage = 2
            st.session_state.scroll_target = "hana-end"
            st.rerun()

# --- 階段 2: 花娜再說 ---
if st.session_state.stage >= 2:
    with st.chat_message("user"):
        st.write(f"我是 {st.session_state.draft_name}：")
        st.write(st.session_state.draft_1)

    with st.chat_message("assistant", avatar="🐱"):
        st.markdown("### 三花貓 花娜 說：")
        st.write("你剛剛的話，")
        st.write("是你眼中的世界。")
        st.write(" ")
        st.write("那「你眼中的你」是什麼？")
        st.write(" ")
        st.write("你可以補一句；")
        st.write("也可以直接送出第一段。")

    draft2 = st.text_area("第二段（選填）", value=st.session_state.draft_2, height=120, key="draft2_box")
    st.session_state.draft_2 = (draft2 or "").strip()

    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("送出給 奈可可", type="primary"):
            payload = f"【第一段】\n{st.session_state.draft_1}"
            if st.session_state.draft_2:
                payload += f"\n\n【第二段】\n{st.session_state.draft_2}"
            
            with st.chat_message("assistant", avatar="🐱"):
                st.markdown("### 橘白貓 泡芙 說：")
                with st.spinner("正在傳遞視角..."):
                    ok = send_email(st.session_state.draft_name, st.session_state.draft_email, payload)
                if ok:
                    st.write("收到了。")
                    st.write("這份視角已經安全送達。")
                    st.write("謝謝你成為這場凝視的一部分。🐱")
                    st.balloons()
                else:
                    st.write("訊號好像稍微卡住了…")
    with colB:
        if st.button("重新開始"):
            for key in ["stage", "draft_name", "draft_email", "draft_1", "draft_2"]:
                st.session_state[key] = 0 if key=="stage" else ""
            st.session_state.scroll_target = None
            st.rerun()

# ==========================================
# 6. 智慧捲動控制 (關鍵修改：加入 setTimeout)
# ==========================================
st.markdown('<div id="hana-end"></div>', unsafe_allow_html=True)

if st.session_state.scroll_target:
    target_id = st.session_state.scroll_target
    # 這裡的 setTimeout 是關鍵，延遲 350 毫秒執行捲動
    # 讓 Streamlit 先完成它的自動排版，我們再強制捲到指定位置
    js_code = f"""
        <script>
            setTimeout(function() {{
                const target = window.parent.document.getElementById("{target_id}");
                if (target) {{
                    target.scrollIntoView({{ behavior: "smooth", block: "start" }});
                }}
            }}, 350);
        </script>
    """
    components.html(js_code, height=0)
    st.session_state.scroll_target = None
