# ... (前面的 import 和設定維持不變) ...

# 引入 PIL 來做圖片檢查
from PIL import Image 

# ... (中間的 send_email 函式維持不變) ...

# ==========================================
# 3. 互動內容 (修改圖片讀取邏輯)
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
    
    # ✅ 安全讀取圖片：先用 try-except 測試
    if os.path.exists(img_path_main):
        try:
            # 試著打開圖片，如果不是圖片，這裡會報錯並被 catch 抓到
            image = Image.open(img_path_main)
            st.image(image, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ 圖片檔案損壞或格式錯誤: {img_path_main}")
            st.caption(f"錯誤訊息: {e}")
            st.info("💡 請回到 GitHub 刪除此圖片，並使用 'Upload files' 按鈕重新上傳原圖。")
    else:
        st.warning(f"⚠️ 找不到圖片路徑：{img_path_main}")
    
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
        
        # ✅ 同樣加上防護罩
        if os.path.exists(img_path_sub):
            try:
                image = Image.open(img_path_sub)
                st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"⚠️ 圖片檔案損壞: {img_path_sub}")
        
        st.markdown("---")
        st.write("留下一句話給 naicoco 吧。")
        st.write("告訴她，**在你眼中的這場展覽，是什麼樣子的？**")

    # ... (後面的輸入框和寄信邏輯維持不變) ...
