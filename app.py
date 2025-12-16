import streamlit as st
import smtplib
import re
import time
import uuid
from email.message import EmailMessage
from pathlib import Path
from PIL import Image

# ==========================================
# 1. 頁面設定與氛圍
# ==========================================
st.set_page_config(
    page_title="牠眼中的他眼中的牠",
    page_icon="🐈",
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

    /* 小一點的按鈕間距 */
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
# 2. Honeypot（移到 Sidebar，避免出現在主畫面）
# ==========================================
with st.sidebar:
    st.text_input("bot_trap", key="hp_field", label_visibility="collapsed")

# ==========================================
# 3. 寄信功能（穩定版 + 保底存檔）
# ==========================================
def _sanitize_single_line(s: str) -> str:
    if not s:
        return ""
    return s.replace("\r", " ").replace("\n", " ").strip()

def _is_valid_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip()
    if len(email) > 254:
        return False
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

def _fallback_save(display_name: str, email: str, payload: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    rid = uuid.uuid4().hex[:10]
    fp = FALLBACK_DIR / f"{ts}_{rid}.txt"
    fp.write_text(
        f"Name: {display_name}\nEmail: {email or '-'}\n\n{payload}\n",
        encoding="utf-8",
    )
    return str(fp)

def send_email(display_name: str, email: str, payload: str) -> bool:
    if "email" not in st.secrets:
        return False

    sender = st.secrets["email"].get("sender", "").strip()
    password = st.secrets["email"].get("password", "").strip()
    receiver = st.secrets["email"].get("receiver", "").strip()
    if not sender or not password or not receiver:
        return False

    display_name = _sanitize_single_line(display_name) or "一位觀眾"
    email = (email or "").strip()

    msg = EmailMessage()
    msg["Subject"] = f"【展覽留言】{display_name} 在「牠眼中的...」留下了視角"
    msg["From"] = f"展覽視角收集器 <{sender}>"
    msg["To"] = receiver

    recipients = [receiver]
    if email and _is_valid_email(email):
        msg["Cc"] = email
        msg["Reply-To"] = email
        recipients.append(email)

    body = f"""Naicoco 您好，

在「牠眼中的他眼中的牠」展覽現場，
{display_name} ({email if email else "未留信箱"}) 留下了這段話：

---------------------------
{payload}
---------------------------

(此信件由 Streamlit 自動傳送)
"""
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender, password)
            server.send_message(msg, from_addr=sender, to_addrs=recipients)
        return True
    except Exception:
        _fallback_save(display_name, email, payload)
        return False

def show_image(path: Path):
    if path.exists():
        try:
            st.image(Image.open(path), use_container_width=True)
        except Exception:
            st.warning(f"⚠️ 圖片檔案似乎損壞: {path.name}")
    else:
        st.warning(f"⚠️ 找不到圖片：{path.as_posix()}")

# ==========================================
# 4. 狀態
# ==========================================
if "stage" not in st.session_state:
    st.session_state.stage = 0

# 防連點冷卻（避免 SMTP 被狂打）
if "last_send_ts" not in st.session_state:
    st.session_state.last_send_ts = 0.0

# 防重送（同一份最終內容不重寄）
if "sent_payload_ids" not in st.session_state:
    st.session_state.sent_payload_ids = set()

# 暫存內容（直到最後才寄）
if "draft_name" not in st.session_state:
    st.session_state.draft_name = ""
if "draft_email" not in st.session_state:
    st.session_state.draft_email = ""
if "draft_1" not in st.session_state:
    st.session_state.draft_1 = ""
if "draft_2" not in st.session_state:
    st.session_state.draft_2 = ""

COOLDOWN_SECONDS = 8

# ==========================================
# 5. UI
# ==========================================
st.title("🐈 牠眼中的他眼中的牠")
st.caption("生活在他方 | 夜貓店 1/1 - 1/31")

# --- 階段 0: 凝視 ---
with st.chat_message("assistant", avatar="🐈"):
    st.write("你看見我了嗎？")
    st.write("我是被凝視的「牠」，也是凝視著你的「牠」。")
    show_image(IMG_DIR / "poster_vertical.jpg")
    st.write("naicoco 用畫筆記下了這個瞬間。")
    st.write("在這個空間裡，我們是怎麼互相觀看的？")

if st.session_state.stage == 0:
    if st.button("繼續走入畫中...", type="primary"):
        st.session_state.stage = 1
        st.rerun()

# --- 階段 1: 第一段（只收集，不寄信） ---
if st.session_state.stage >= 1:
    with st.chat_message("assistant", avatar="🍊"):
        st.write("他眼中有我，我眼中有橘子，那你眼中看到了什麼？")
        show_image(IMG_DIR / "poster_horizontal.jpg")
        st.markdown("---")
        st.write("我想幫你把這份視角，傳遞給 naicoco。")
        st.write("若是願意，請留下你的稱呼；若想收到這封信的備份（或期待回信），也可以留下信箱。")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            visitor_name = st.text_input("你的稱呼 (例如：夜貓常客)", key="v_name")
        with col2:
            visitor_email = st.text_input("你的信箱 (選填，寄備份用)", key="v_email")

    if st.session_state.stage == 1:
        user_input_1 = st.chat_input("寫下你眼中的世界...", key="chat1")

        if user_input_1:
            # bot → 忽略
            if st.session_state.get("hp_field"):
                st.stop()

            st.session_state.draft_name = visitor_name.strip() if visitor_name else "匿名訪客"
            st.session_state.draft_email = (visitor_email or "").strip()
            st.session_state.draft_1 = user_input_1.strip()
            st.session_state.draft_2 = ""

            with st.chat_message("user"):
                st.write(f"我是 {st.session_state.draft_name}：")
                st.write(st.session_state.draft_1)

            with st.chat_message("assistant", avatar="🍊"):
                st.write("我收到了。")
                st.write("如果你願意，再補一句。")
                st.caption("（最後會只寄出一封信：包含你寫的所有內容。）")

            st.session_state.stage = 2
            st.rerun()

# --- 階段 2: 第二段 + 最終送出（只在此寄一次） ---
if st.session_state.stage >= 2:
    with st.chat_message("assistant", avatar="🐈"):
        st.write("你剛剛的話，是你眼中的世界。")
        st.write("那「你眼中的你」是什麼？")
        st.caption("你可以補一句；也可以直接送出第一段。")

    # 第二段用一般輸入（避免 chat_input 一送就寄）
    draft2 = st.text_area(
        "第二段（選填）",
        value=st.session_state.draft_2,
        height=120,
        placeholder="例如：我其實希望… / 我不敢說的是… / 我想被怎麼看見…",
        key="draft2_box",
    )
    st.session_state.draft_2 = (draft2 or "").strip()

    # 預覽（讓觀眾知道最後會寄出什麼）
    with st.expander("預覽你要送出的內容", expanded=False):
        st.markdown("**【第一段】**")
        st.write(st.session_state.draft_1 or "")
        if st.session_state.draft_2:
            st.markdown("**【第二段】**")
            st.write(st.session_state.draft_2)

    colA, colB = st.columns([1, 1])
    with colA:
        send_btn = st.button("送出給 naicoco", type="primary")
    with colB:
        reset_btn = st.button("重新開始")

    if reset_btn:
        st.session_state.stage = 0
        st.session_state.draft_name = ""
        st.session_state.draft_email = ""
        st.session_state.draft_1 = ""
        st.session_state.draft_2 = ""
        st.rerun()

    if send_btn:
        if st.session_state.get("hp_field"):
            st.stop()

        now = time.time()
        if (now - st.session_state.last_send_ts) < COOLDOWN_SECONDS:
            with st.chat_message("assistant", avatar="🍊"):
                st.write("我正在送出訊號，等一下再按一次就好。")
            st.stop()

        name = st.session_state.draft_name or "匿名訪客"
        email = st.session_state.draft_email or ""

        payload = f"【第一段】\n{st.session_state.draft_1}".strip()
        if st.session_state.draft_2:
            payload += f"\n\n【第二段】\n{st.session_state.draft_2}".strip()

        payload_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{name}|{email}|{payload}").hex
        if payload_id in st.session_state.sent_payload_ids:
            with st.chat_message("assistant", avatar="🍊"):
                st.write("這份內容我已經送過了。謝謝你。🐈")
            st.stop()

        with st.chat_message("assistant", avatar="🍊"):
            with st.spinner("正在把你的視角送過去..."):
                ok = send_email(name, email, payload)

            st.session_state.last_send_ts = time.time()
            st.session_state.sent_payload_ids.add(payload_id)

            if ok:
                st.write("收到了。這份視角已經安全送達。")
                if email and _is_valid_email(email):
                    st.caption(f"（備份信件已同步寄至：{email}，若沒收到請檢查垃圾信箱）")
                elif email:
                    st.caption("（你留的信箱格式看起來不太像 email，所以我沒有寄副本；但主辦人已收到你的視角。）")
                st.write("謝謝你成為這場凝視的一部分。🐈")
                st.balloons()
            else:
                st.write("訊號好像稍微卡住了…")
                st.caption("（不用擔心，你的內容已被保留，主辦人仍能在系統中取回。）")
