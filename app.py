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

    h1, h2, h3, p, div, span, label, li {
        color: #F0F0F0 !important;
        font-family: "Microsoft JhengHei", sans-serif;
    }

    div[data-testid="stChatMessage"] { border-radius: 14px; }

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
# 2. Honeypot
# ==========================================
with st.sidebar:
    st.text_input("bot_trap", key="hp_field", label_visibility="collapsed")

# ==========================================
# 3. 功能函式
# ==========================================
def _sanitize_single_line(s: str) -> str:
    if not s: return ""
    return s.replace("\r", " ").replace("\n", " ").strip()

def _is_valid_email(email: str) -> bool:
    if not email: return False
    email = email.strip()
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def send_email(display_name: str, email: str, payload: str) -> bool:
    if "email" not in st.secrets: return False
    sender = st.secrets["email"].get("sender", "").strip()
    password = st.secrets["email"].get("password", "").strip()
    receiver = st.secrets["email"].get("receiver", "").strip()
    
    display_name = _sanitize_single_line(display_name) or "一位觀眾"
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
    except Exception:
        return False

def show_image(path: Path):
    if path.exists():
        st.image(Image.open(path), use_container_width=True)

# ==========================================
# 4. 狀態管理
# ==========================================
if "stage" not in st.session_state: st.session_state.stage = 0
if "scroll_to_bottom" not in st.session_state: st.session_state.scroll_to_bottom = False
if "last_send_ts" not in st.session_state: st.session_state.last_send_ts = 0.0
if "sent_payload_ids" not in st.session_state: st.session_state.sent_payload_ids = set()
if "draft_name" not in st.session_state: st.session_state.draft_name = ""
if "draft_email" not in st.session_state: st.session_state.draft_email = ""
if "draft_1" not in st.session_state: st.session_state.draft_1 = ""
if "draft_2" not in st.session_state: st.session_state.draft_2 = ""

COOLDOWN_SECONDS = 8

# ==========================================
# 5. UI 流程
# ==========================================
st.title("🐱 牠眼中的 他眼中的牠")
st.caption("生活在他方｜夜貓店 Elsewhere Cafe | 2026/1/1 - 1/31")

# --- 階段 0: 花娜開場 ---
with st.chat_message("hana", avatar="🐱"):
    st.markdown("""
    你看見我了嗎？  
    我是被凝視的「牠」，  
    也是凝視著你的「牠」。
    """)
    show_image(IMG_DIR / "poster_vertical.jpg")
    st.markdown("""
    奈可可 用畫筆記下了這個瞬間。  
    在這個空間裡，  
    我們是怎麼互相觀看的？
    """)

if st.session_state.stage == 0:
    if st.button("繼續走入畫中...", type="primary"):
        st.session_state.stage = 1
        st.rerun()

# --- 階段 1: 泡芙引導 ---
if st.session_state.stage >= 1:
    with st.chat_message("puff", avatar="🐱"):
        st.markdown("""
        他眼中有我，  
        我眼中有橘子，  
        那你眼中看到了什麼？
        """)
        show_image(IMG_DIR / "poster_horizontal.jpg")
        st.markdown("---")
        st.markdown("""
        我想幫你把這份視角，傳遞給奈可可。  
          
        若是願意，請留下你的稱呼；  
        若想收到這封信的備份（或期待回信），  
        也可以留下信箱。  
          
        展覽結束後會在所有留言裡  
        隨機抽出三位，  
        可以獲得奈可可親筆創作小禮🎁。
        """)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            visitor_name = st.text_input("你的稱呼 (例如：夜貓常客)", key="v_name")
        with col2:
            visitor_email = st.text_input("你的信箱 (選填)", key="v_email")

    if st.session_state.stage == 1:
        user_input_1 = st.chat_input("寫下你眼中的世界...", key="chat1")
        if user_input_1:
            if st.session_state.get("hp_field"): st.stop()
            st.session_state.draft_name = visitor_name.strip() if visitor_name else "匿名訪客"
            st.session_state.draft_email = (visitor_email or "").strip()
            st.session_state.draft_1 = user_input_1.strip()
            st.session_state.stage = 2
            st.session_state.scroll_to_bottom = True
            st.rerun()

# --- 階段 2: 花娜結尾 ---
if st.session_state.stage >= 2:
    with st.chat_message("user"):
        st.write(f"我是 {st.session_state.draft_name}：")
        st.write(st.session_state.draft_1)

    with st.chat_message("hana", avatar="🐱"):
        st.markdown("""
        你剛剛的話，  
        是你眼中的世界。  
          
        那「你眼中的你」是什麼？  
          
        你可以補一句；  
        也可以直接送出第一段。
        """)

    draft2 = st.text_area("第二段（選填）", value=st.session_state.draft_2, height=120, key="draft2_box")
    st.session_state.draft_2 = (draft2 or "").strip()

    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("送出給 奈可可", type="primary"):
            if st.session_state.get("hp_field"): st.stop()
            
            payload = f"【第一段】\n{st.session_state.draft_1}"
            if st.session_state.draft_2:
                payload += f"\n\n【第二段】\n{st.session_state.draft_2}"
            
            with st.chat_message("puff", avatar="🐱"):
                with st.spinner("正在傳遞視角..."):
                    ok = send_email(st.session_state.draft_name, st.session_state.draft_email, payload)
                if ok:
                    st.markdown("收到了。  \n這份視角已經安全送達。  \n謝謝你成為這場凝視的一部分。🐱")
                    st.balloons()
                else:
                    st.write("訊號好像稍微卡住了…")
    with colB:
        if st.button("重新開始"):
            for key in ["stage", "draft_name", "draft_email", "draft_1", "draft_2"]:
                st.session_state[key] = 0 if key=="stage" else ""
            st.rerun()

# ==========================================
# 6. 自動捲動
# ==========================================
components.html('<div id="bottom-anchor"></div>', height=0)
if st.session_state.scroll_to_bottom:
    components.html("""
        <script>
          const el = window.parent.document.getElementById("bottom-anchor");
          if (el) { el.scrollIntoView({behavior: "instant", block: "end"}); }
        </script>
        """, height=0)
    st.session_state.scroll_to_bottom = False
