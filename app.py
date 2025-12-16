import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# --- 設定頁面與樣式 ---
st.set_page_config(page_title="牛也眼中的...你", page_icon="🐱")

# 自定義 CSS：配合海報的深綠色背景與橘色點綴
st.markdown("""
<style>
    /* 整體背景色 (深綠色) */
    .stApp {
        background-color: #2F5245; 
    }
    /* 標題文字顏色 */
    h1, h2, h3, p, div {
        color: #F0F0F0 !important;
        font-family: "Microsoft JhengHei", sans-serif;
    }
    /* 對話框樣式 - 機器人 (橘色系) */
    .stChatMessage.st-emotion-cache-1c7y2kd {
        background-color: #E89B3D30;
        border-radius: 15px;
    }
    /* 輸入框樣式 */
    .stChatInput {
        background-color: #ffffff20 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 寄信函式 (SMTP) ---
def send_email(user_message):
    try:
        if "email" not in st.secrets:
            st.error("⚠️ 請先設定 secrets.toml 中的 email 資訊")
            return False
            
        sender = st.secrets["email"]["sender"]
        password = st.secrets["email"]["password"]
        receiver = st.secrets["email"]["receiver"]

        msg = MIMEMultipart()
        msg['From'] = "夜貓展覽小精靈"
        msg['To'] = receiver
        msg['Subject'] = "【展覽留言】有人跟貓咪說了悄悄話..."

        body = f"""
        Naicoco 您好，
        
        在「生活在他方-夜貓店」的展覽現場，有一位觀眾留下了這段話：
        
        ---------------------------
        {user_message}
        ---------------------------
        
        (來自 Streamlit 互動留言板)
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
        st.error(f"傳送失敗: {e}")
        return False

# --- 主程式邏輯 ---

st.title("🐱 牛也眼中的...你")
st.caption("生活在他方 | 夜貓店 1/1 - 1/31")

# 初始化狀態
if "step" not in st.session_state:
    st.session_state.step = 0

# 步驟 0: 開場與第一張圖
with st.chat_message("assistant", avatar="🍊"):
    st.write("嗨，你是來看我的嗎？")
    st.write("我是牛也，這裡的時間過得比較慢，你可以慢慢看。")
    
    # 顯示第一張圖 (請確保 images 資料夾有圖，或換成網址)
    # 這裡示範使用本地圖片，若佈署到雲端需確保圖片有一起上傳
    if os.path.exists("images/poster_vertical.jpg"):
        st.image("images/poster_vertical.jpg", use_container_width=True)
    else:
        st.info("(請將展覽直式海報放入 images 資料夾)")
        
    st.write("naicoco 畫下了我們眼中的世界。你覺得，我在看什麼呢？")

# 步驟 1: 等待使用者互動
if st.session_state.step == 0:
    if st.button("繼續聽貓咪說話..."):
        st.session_state.step = 1
        st.rerun()

# 步驟 2: 第二張圖與引導留言
if st.session_state.step >= 1:
    with st.chat_message("assistant", avatar="🍊"):
        st.write("有時候，我覺得人類頭上好像也頂著一顆橘子...")
        st.write("沉甸甸的，但也甜甜的。")
        
        if os.path.exists("images/poster_horizontal.jpg"):
            st.image("images/poster_horizontal.jpg", use_container_width=True)
        
        st.write("既然來了，留下一句話給 naicoco 吧。")
        st.write("不管是關於這個夜晚、關於畫、還是關於你自己。我會幫你把話帶給她。")

    # 處理輸入
    user_input = st.chat_input("在這裡寫下你想說的話...")
    
    if user_input:
        # 顯示使用者說的話
        with st.chat_message("user"):
            st.write(user_input)
            
        # 寄信動作
        with st.chat_message("assistant", avatar="🍊"):
            with st.spinner("正在把話語裝進信封..."):
                success = send_email(user_input)
                
            if success:
                st.write("好，我收到了。這封信已經飛去 naicoco 那裡了。")
                st.write("謝謝你在這個夜晚，願意停留片刻。晚安。🌙")
                st.balloons() # 給一點驚喜
            else:
                st.write("哎呀，訊號好像被貓抓斷了，你要不要截圖直接私訊給畫家？")
