import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from PIL import Image  # 引入 PIL 來做圖片檢查

# ==========================================
# 1. 頁面設定與氛圍
# ==========================================
st.set_page_config(page_title="牠眼中的他眼中的牠", page_icon="🐈")

st.markdown("""
<style>
    .stApp {
        background-color: #2F5245;
    }
    h1, h2, h3, p, div, span, label, li {
        color: #F0F0F0 !important;
        font-family: "Microsoft JhengHei", sans-serif;
    }
    .stChatMessage.st-emotion-cache-1c7y2kd {
        background-color: #E89B3D20;
        border: 1px solid #E89B3D50;
    }
    .stChatInput {
        background-color: #00000040 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 寄信功能
# ==========================================
def send_email(user_message):
    try:
        if "email" not in st.secrets:
            st.error("⚠️ 系統設定缺漏：請確認 Streamlit Secrets 中的 email 資訊")
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
        print(f"Error: {e}") 
        return False

# ==========================================
# 3. 互動內容
# ==========================================

st.title("🐈 牠眼中的他眼中的牠")
st.caption("生活在他方 | 夜貓店 1/1 - 1/31")

if "stage" not in st.session_state:
    st.session_state.stage = 0

# --- 階段 0: 凝視 (直式海報) ---
with st.chat_message("assistant", avatar="🐈"):
    st.write("你看見我了嗎？")
    st.write("我是被凝視的「牠」，也是凝視著你的「牠」。")
    
    # 這裡改成你 GitHub 上正確的檔名
    img_path_main = "images/poster_vertical.jpg"
    
    if os.path.exists(img_path_main):
        try:
            image = Image.open(img_path_main)
            st.image(image, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ 圖片檔案似乎損壞，請重新上傳至 GitHub: {img_path_main}")
    else:
        st.warning(f"⚠️ 找不到圖片：{img_path_main}，請確認 'images' 資料夾內是否有此檔案。")
    
    st.write("naicoco 用畫筆記下了這個瞬間。")
    st.write("在這個空間裡，我們是怎麼互相觀看的？")

if st.session_state.stage == 0:
    if st.button("繼續走入畫中...", type="primary"):
        st.session_state.stage = 1
        st.rerun()

# --- 階段 1: 交換 (橫式海報) ---
if st.session_state.stage >= 1:
    with st.chat_message("assistant", avatar="🍊"):
        st.write("他眼中有我，我眼中有橘子，那你眼中看到了什麼？")
        
        img_path_sub = "images/poster_horizontal.jpg"
        
        if os.path.exists(img_path_sub):
            try:
                image = Image.open(img_path_sub)
                st.image(image, use_container_width=True)
            except Exception as e:
                st.warning(f"⚠️ 圖片檔案似乎損壞: {img_path_sub}")
            
        st.markdown("---")
        st.write("留下一句話給 naicoco 吧。")
        st.write("告訴她，**在你眼中的這場展覽，是什麼樣子的？**")

    user_input = st.chat_input("寫下你眼中的世界...")
    
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
            
        with st.chat_message("assistant", avatar="🍊"):
            with st.spinner("正在將你的視角傳遞過去..."):
                success = send_email(user_input)
                
            if success:
                st.write("收到了。這份視角已經安全送達。")
                st.write("謝謝你成為這場凝視的一部分。🐈")
                st.balloons()
            else:
                st.write("訊號好像稍微卡住了... 不過沒關係，你的心意我們感受到了。")
