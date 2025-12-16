import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ==========================================
# 1. 頁面設定與氛圍營造
# ==========================================
st.set_page_config(page_title="牠眼中的他眼中的牠", page_icon="🐈")

# CSS 魔術：設定夜貓店風格的深綠色背景 (#2F5245) 與文字顏色
st.markdown("""
<style>
    .stApp {
        background-color: #2F5245;
    }
    h1, h2, h3, p, div, span, label {
        color: #F0F0F0 !important;
        font-family: "Microsoft JhengHei", sans-serif;
    }
    /* 調整對話框背景色：讓它像夜晚的燈光 */
    .stChatMessage.st-emotion-cache-1c7y2kd {
        background-color: #E89B3D20; /* 淡淡的橘色透明背景 */
        border: 1px solid #E89B3D50;
    }
    /* 輸入框優化 */
    .stChatInput {
        background-color: #00000040 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 功能函式：Gmail 傳信差
# ==========================================
def send_email(user_message):
    try:
        # 檢查是否已設定 Secrets
        if "email" not in st.secrets:
            st.error("⚠️ 系統設定缺漏：請確認 secrets.toml 中的 email 資訊")
            return False
            
        sender = st.secrets["email"]["sender"]
        password = st.secrets["email"]["password"]
        receiver = st.secrets["email"]["receiver"]

        msg = MIMEMultipart()
        msg['From'] = "展覽視角收集器"
        msg['To'] = receiver
        msg['Subject'] = "【展覽留言】有人在「牠眼中的...」留下了視角"

        body = f"""
        Naicoco 您好，
        
        在「牠眼中的他眼中的牠」展覽現場，
        有一個靈魂留下了這段話：
        
        ---------------------------
        {user_message}
        ---------------------------
        
        (此信件由 Streamlit 自動傳送)
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, receiver, text)
        server.quit()
        return True
    except Exception as e:
        # 在正式展覽時，這裡可以改為 st.error("傳送失敗，請洽工作人員") 避免跳出太技術的錯誤
        print(f"Error: {e}") 
        return False

# ==========================================
# 3. 互動腳本邏輯
# ==========================================

st.title("🐈 牠眼中的他眼中的牠")
st.caption("生活在他方 | 夜貓店 1/1 - 1/31")

# 使用 Session State 紀錄使用者的閱讀進度
if "stage" not in st.session_state:
    st.session_state.stage = 0

# --- 階段 0: 凝視 (第一張海報) ---
with st.chat_message("assistant", avatar="🐈"):
    st.write("你看見我了嗎？")
    st.write("我是被凝視的「牠」，也是凝視著你的「牠」。")
    
    # 顯示直式海報 (請確保檔名正確)
    if os.path.exists("images/poster_main.jpg"):
        st.image("images/poster_main.jpg", use_container_width=True)
    
    st.write("naicoco 用畫筆記下了這個瞬間。")
    st.write("在這個空間裡，我們是怎麼互相觀看的？")

# 按鈕：進入下一階段
if st.session_state.stage == 0:
    if st.button("繼續走入畫中...", type="primary"):
        st.session_state.stage = 1
        st.rerun()

# --- 階段 1: 交換 (第二張海報 + 留言) ---
if st.session_state.stage >= 1:
    with st.chat_message("assistant", avatar="🍊"):
        st.write("他眼中有我，我眼中有橘子，那你眼中看到了什麼？")
        
        # 顯示橫式海報
        if os.path.exists("images/poster_sub.jpg"):
            st.image("images/poster_sub.jpg", use_container_width=True)
            
        st.markdown("---")
        st.write("留下一句話給 naicoco 吧。")
        st.write("告訴她，**在你眼中的這場展覽，是什麼樣子的？**")

    # 輸入框
    user_input = st.chat_input("寫下你眼中的世界...")
    
    if user_input:
        # 1. 顯示使用者留言
        with st.chat_message("user"):
            st.write(user_input)
            
        # 2. 觸發寄信
        with st.chat_message("assistant", avatar="🍊"):
            with st.spinner("正在將你的視角傳遞過去..."):
                success = send_email(user_input)
                
            if success:
                st.write("收到了。這份視角已經安全送達。")
                st.write("謝謝你成為這場凝視的一部分。🐈")
                st.balloons() # 撒花效果
            else:
                st.write("訊號好像稍微卡住了... 不過沒關係，你的心意我們感受到了。")
