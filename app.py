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
st.set_page_config(page_title="牠眼中的他眼中的牠", page_icon="🐈")

st.markdown(
    """
<style>
    .stApp {
        background-color: #2F5245;
    }
    h1, h2, h3, p, div, span, label, li {
        color: #F0F0F0 !important;
        font-family: "Microsoft JhengHei", sans-serif;
    }

    /* 避免使用易變動的 class 名稱，改用 data-testid */
    div[data-testid="stChatMessage"] {
        border-radius: 14px;
    }

    /* 輸入區域像展場裝置的面板 */
    div[data-testid="stChatInput"] {
        background: rgba(0,0,0,0.25);
        border-radius: 14px;
    }

    /* TextInput label */
    div[data-testid="stTextInput"] label {
        color: #E89B3D !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

APP_DIR = Path(__file__).parent
IMG_DIR = APP_DIR / "images"
FALLBACK_DIR = APP_DIR / "fallback_messages"
FALLBACK_DIR.mkdir(exist_ok=True)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# ==========================================
# 2. 寄信功能（穩定版 + 防重送 + 保底存檔）
# ==========================================
def _sanitize_single_line(s: str) -> str:
    """防止 header injection：去掉換行"""
    if not s:
        return ""
    return s.replace("\r", " ").replace("\n", " ").strip()

def _is_valid_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip()
    if len(email) > 254:
        return False
    return bool(EMAIL_RE.match(email))

def _fallback_save(display_name: str, email: str, user_message: str) -> str:
    ts = time.strftime("%Y%m%d-%H%M%S")
    rid = uuid.uuid4().hex[:10]
    fp = FALLBACK_DIR / f"{ts}_{rid}.txt"
    fp.write_text(
        f"Name: {display_name}\nEmail: {email or '-'}\n\n{user_message}\n",
        encoding="utf-8",
    )
    return str(fp)

def send_email(display_name: str, email: str, user_message: str) -> bool:
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

    # 觀眾要副本才寄；不合法就不寄副本但仍寄主辦
    if email and _is_valid_email(email):
        msg["Cc"] = email
        msg["Reply-To"] = email
        recipients.append(email)

    body = f"""Naicoco 您好，

在「牠眼中的他眼中的牠」展覽現場，
{display_name} ({email if email else "未留信箱"}) 留下了這段話：

---------------------------
{user_message}
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
        _fallback_save(display_name, email, user_message)
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
# 3. 互動內容
# ==========================================
st.title("🐈 牠眼中的他眼中的牠")
st.caption("生活在他方 | 夜貓店 1/1 - 1/31")

# session state init
if "stage" not in st.session_state:
    st.session_state.stage = 0

# 防重送／冷卻
if "last_send_ts" not in st.session_state:
    st.session_state.last_send_ts = 0.0
if "sent_message_ids" not in st.session_state:
    st.session_state.sent_message_ids = set()

# 儲存第一段（供 stage2 合併）
if "first_message" not in st.session_state:
    st.session_state.first_message = ""
if "first_name" not in st.session_state:
    st.session_state.first_name = ""
if "first_email" not in st.session_state:
    st.session_state.first_email = ""

COOLDOWN_SECONDS = 8

# --- 階段 0: 凝視 (直式海報) ---
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

# --- 階段 1: 交換 (橫式海報 + 第一段留言) ---
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

        # ✅ 蜜罐：完全隱藏（觀眾看不到）
        st.text_input("bot_trap", key="hp_field", label_visibility="collapsed")

    # 只在 stage 1 接第一段輸入
    if st.session_state.stage == 1:
        user_input_1 = st.chat_input("寫下你眼中的世界...", key="chat1")

        if user_input_1:
            # honeypot 有值 → 直接忽略（擋 bot）
            if st.session_state.get("hp_field"):
                st.stop()

            final_name = visitor_name.strip() if visitor_name else "匿名訪客"
            final_email = (visitor_email or "").strip()

            # 防重送：同一段留言生成 id
            msg_id = uuid.uuid5(
                uuid.NAMESPACE_DNS,
                f"stage1|{final_name}|{final_email}|{user_input_1}",
            ).hex

            now = time.time()
            if (now - st.session_state.last_send_ts) < COOLDOWN_SECONDS:
                with st.chat_message("assistant", avatar="🍊"):
                    st.write("我收到了，但我需要一點時間把訊號送出去。你可以稍等一下再送一次。")
                st.stop()

            if msg_id in st.session_state.sent_message_ids:
                with st.chat_message("assistant", avatar="🍊"):
                    st.write("這段視角我已經收過了，謝謝你。🐈")
                st.stop()

            with st.chat_message("user"):
                st.write(f"我是 {final_name}：")
                st.write(user_input_1)

            with st.chat_message("assistant", avatar="🍊"):
                with st.spinner("正在將你的視角傳遞過去..."):
                    success = send_email(final_name, final_email, user_input_1)

                st.session_state.last_send_ts = time.time()
                st.session_state.sent_message_ids.add(msg_id)

                if success:
                    st.write("收到了。這份視角已經安全送達。")

                    if final_email and _is_valid_email(final_email):
                        st.caption(f"（備份信件已同步寄至：{final_email}，若沒收到請檢查垃圾信箱）")
                    elif final_email:
                        st.caption("（你留的信箱格式看起來不太像 email，所以我沒有寄副本；但主辦人已收到你的視角。）")

                    # ====== 進入 A：續寫一次 ======
                    st.write("如果你願意，再補一句。")
                    st.caption("（下一步只寫一句就好，像把視角再往內推一點。）")

                    # 存第一段，供 stage2 合併
                    st.session_state.first_message = user_input_1
                    st.session_state.first_name = final_name
                    st.session_state.first_email = final_email

                    st.session_state.stage = 2
                    st.rerun()
                else:
                    st.write("訊號好像稍微卡住了…")
                    st.caption("（不用擔心，你的內容已被保留，主辦人仍能在系統中取回。）")

# --- 階段 2: 續寫一次（第二段） ---
if st.session_state.stage >= 2:
    with st.chat_message("assistant", avatar="🐈"):
        st.write("你剛剛的話，是你眼中的世界。")
        st.write("那「你眼中的你」是什麼？")
        st.caption("可短可長，但我會把它當成『第二層視角』。")

    followup = st.chat_input("再補一句（寫完就送出）", key="chat2")

    if followup:
        final_name = st.session_state.first_name or "匿名訪客"
        final_email = st.session_state.first_email or ""
        first_msg = st.session_state.first_message or ""

        merged = f"【第一段】\n{first_msg}\n\n【第二段】\n{followup}"

        msg_id2 = uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"stage2|{final_name}|{final_email}|{first_msg}|{followup}",
        ).hex

        now = time.time()
        if (now - st.session_state.last_send_ts) < COOLDOWN_SECONDS:
            with st.chat_message("assistant", avatar="🍊"):
                st.write("我正在送出上一段訊號，等一下再送一次就好。")
            st.stop()

        if msg_id2 in st.session_state.sent_message_ids:
            with st.chat_message("assistant", avatar="🍊"):
                st.write("這段我已經收到了。謝謝你把它放進來。🐈")
            st.stop()

        with st.chat_message("user"):
            st.write(f"我是 {final_name}：")
            st.write(followup)

        with st.chat_message("assistant", avatar="🍊"):
            with st.spinner("把第二層視角也送過去..."):
                success2 = send_email(final_name, final_email, merged)

            st.session_state.last_send_ts = time.time()
            st.session_state.sent_message_ids.add(msg_id2)

            if success2:
                st.write("第二段也收到了。謝謝你把視角再往內推了一步。")
                st.write("你可以慢慢離開畫裡。🐈")
                st.balloons()
            else:
                st.write("訊號又卡住了…")
                st.caption("（不用擔心，你的內容已被保留，主辦人仍能在系統中取回。）")
