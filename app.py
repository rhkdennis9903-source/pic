import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from PIL import Image

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
    /* 調整輸入框的標籤顏色 */
    .stTextInput label {
        color: #E89B3D !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 寄信功能 (升級版：支援姓名與副本)
# ==========================================
def send_email(name, email, user_message):
    try:
        if "email" not in st.secrets:
            st.error("⚠️ 系統設定缺漏：請確認 Streamlit Secrets 中的 email 資訊")
            return False
            
        sender = st.secrets["email"]["sender"]
        password = st.secrets["email"]["password"]
        receiver = st.secrets["email"]["receiver"] # 主辦人信箱

        msg = MIMEMultipart()
        msg['From'] = "展覽視角收集器"
        
        # 設定收件者：一定要有主辦人
        recipients = [receiver]
        
        # 處理標題：如果有填名字，標題就帶入名字
        display_name = name if name else "一位觀眾"
        msg['Subject'] = f"【展覽留言】{display_name} 在「牠眼中的...」留下了視角"

        # 處理副本 (CC)：如果觀眾有填信箱，就加到副本
        if email:
            msg['Cc'] = email
            msg['Reply-To'] = email # 讓主辦人按回覆時，能直接回給觀眾
            recipients.append(email) # 真正寄送的名單也要加入觀眾
        
        msg['To'] = receiver

        # 信件內容
        body = f"""
        Naicoco 您好，
        
        在「牠眼中的他眼中的牠」展覽現場，
        {display_name} ({email if email else '未留信箱'}) 留下了這段話：
        
        ---------------------------
        {user_message}
        ---------------------------
        
        (此信件由 Streamlit 自動傳送)
        """
        msg.attach(MIMEText(body, 'plain'))

        # 連線 SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        
        # 寄送給「收件人清單」 (包含主辦人 + 觀眾)
        server.sendmail(sender, recipients, msg.as_string())
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
    
    img_path_main = "images/poster_vertical.jpg"
    
    if os.path.exists(img_path_main):
        try:
            image = Image.open(img_path_main)
            st.image(image, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ 圖片檔案似乎損壞: {img_path_main}")
    else:
        st.warning(f"⚠️ 找不到圖片：{img_path_main}")
    
    st.write("naicoco 用畫筆記下了這個瞬間。")
    st.write("在這個空間裡，我們是怎麼互相觀看的？")

if st.session_state.stage == 0:
    if st.button("繼續走入畫中...", type="primary"):
        st.session_state.stage = 1
        st.rerun()

# --- 階段 1: 交換 (橫式海報 + 表單) ---
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
        st.write("我想幫你把這份視角，傳遞給 naicoco。")
        st.write("若是願意，請留下你的稱呼；若想收到這封信的備份（或期待回信），也可以留下信箱。")

    # === 新增功能：姓名與信箱輸入區 ===
    # 使用 container 包起來，讓排版整齊
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            visitor_name = st.text_input("你的稱呼 (例如：夜貓常客)", key="v_name")
        with col2:
            visitor_email = st.text_input("你的信箱 (選填，寄備份用)", key="v_email")

    # 文字輸入框
    user_input = st.chat_input("寫下你眼中的世界...")
    
    if user_input:
        # 檢查名字是否為空，若空則給預設值，但不阻擋
        final_name = visitor_name if visitor_name else "匿名訪客"
        
        with st.chat_message("user"):
            st.write(f"我是 {final_name}：")
            st.write(user_input)
            
        with st.chat_message("assistant", avatar="🍊"):
            with st.spinner("正在將你的視角傳遞過去..."):
                # 將名字、信箱、內容一起傳給寄信函式
                success = send_email(final_name, visitor_email, user_input)
                
            if success:
                st.write("收到了。這份視角已經安全送達。")
                if visitor_email:
                    st.caption(f"（備份信件已同步寄至：{visitor_email}，若沒收到請檢查垃圾信箱）")
                st.write("謝謝你成為這場凝視的一部分。🐈")
                st.balloons()
            else:
                st.write("訊號好像稍微卡住了... 不過沒關係，你的心意我們感受到了。")
