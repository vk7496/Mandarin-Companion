import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime
import os

# --- تنظیمات صفحه ---
st.set_page_config(page_title="MO Muscat | Digital Concierge", page_icon="🏮", layout="wide")

# --- استایل CSS برای شبیه سازی تصویر ارسالی ---
st.markdown("""
    <style>
    /* استایل منوی سمت چپ */
    [data-testid="stSidebar"] {
        background-color: #1e2630;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        border: 1px solid #8D734A;
        background-color: #8D734A;
        color: white;
    }
    .whatsapp-btn {
        background-color: #25D366 !important;
        color: white !important;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        text-decoration: none;
        display: block;
        margin-top: 20px;
    }
    h1 { color: #8D734A; text-align: center; font-family: 'serif'; }
    .status-box { 
        padding: 10px; 
        border-radius: 10px; 
        background-color: #e8f0fe; 
        color: #1e2630; 
        text-align: center; 
        margin-bottom: 20px;
        border: 1px solid #d1d9e6;
    }
    </style>
    """, unsafe_allow_html=True)

# مقداردهی Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# تابع ذخیره آمار (اصلاح شده)
def log_analytics(room):
    file_name = "mo_analytics.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[now, room]], columns=['Timestamp', 'RoomNumber'])
    
    if not os.path.isfile(file_name):
        new_data.to_csv(file_name, index=False)
    else:
        new_data.to_csv(file_name, mode='a', header=False, index=False)

# --- Sidebar (داشبورد) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/43/Mandarin_Oriental_Logo.svg/1200px-Mandarin_Oriental_Logo.svg.png", width=150)
    st.title("Dashboard")
    st.write("---")
    st.button("🏠 Home")
    st.button("🛎️ Room Service")
    st.button("🚗 Book Transportation")
    st.button("🍴 Dining")
    st.button("✨ Local Experiences")
    
    # دکمه واتس‌اپ در انتهای منو
    st.markdown("""
        <a href="https://wa.me/96812345678" class="whatsapp-btn">
            💬 Connect on WhatsApp
        </a>
    """, unsafe_allow_html=True)
    
    st.write("---")
    # بخش آنالیز در انتهای داشبورد
    with st.expander("📊 Management Analytics"):
        pwd = st.text_input("Password:", type="password")
        if pwd == "MO2026":
            if os.path.isfile("mo_analytics.csv"):
                df = pd.read_csv("mo_analytics.csv")
                st.write(f"Total Uses: {len(df)}")
                st.dataframe(df)
                if st.button("🗑️ Clear Data"):
                    os.remove("mo_analytics.csv")
                    st.rerun()
            else:
                st.write("No data recorded.")

# --- محتوای اصلی صفحه ---
if "guest_identified" not in st.session_state:
    st.session_state.guest_identified = False

st.image("https://upload.wikimedia.org/wikipedia/en/thumb/4/43/Mandarin_Oriental_Logo.svg/1200px-Mandarin_Oriental_Logo.svg.png", width=100)
st.markdown("<h1>MANDARIN ORIENTAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-top:-20px;'>MUSCAT</p>", unsafe_allow_html=True)

if not st.session_state.guest_identified:
    with st.container():
        st.write("### Welcome to your Digital Concierge")
        room_num = st.text_input("Please enter your Room Number to begin:", placeholder="e.g. 302")
        if st.button("Start Experience"):
            if room_num:
                st.session_state.room_number = room_num
                st.session_state.guest_identified = True
                log_analytics(room_num) # ثبت در فایل
                st.rerun()
            else:
                st.error("Room number is required.")

else:
    st.markdown(f"<div class='status-box'>Connected: <b>Room {st.session_state.room_number}</b></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    # لینک‌های واتس‌اپ با متن آماده
    with col1:
        wa_room_service = f"https://wa.me/96812345678?text=Hello, I am in Room {st.session_state.room_number} and I would like to request Room Service."
        st.markdown(f'<a href="{wa_room_service}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#8D734A; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">🛎️ Room Service</button></a>', unsafe_allow_html=True)
    
    with col2:
        wa_taxi = f"https://wa.me/96812345678?text=Hello, I am in Room {st.session_state.room_number} and I need to book a taxi."
        st.markdown(f'<a href="{wa_taxi}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#8D734A; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">🚕 Book Transportation</button></a>', unsafe_allow_html=True)

    # سیستم چت
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": f"Welcome. I am your AI Concierge for Room {st.session_state.room_number}. How may I assist you today?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"You are a luxury concierge for Mandarin Oriental Muscat. The guest is in room {st.session_state.room_number}."}, *st.session_state.messages]
            ).choices[0].message.content
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("<div style='text-align:center; color:#999; font-size:10px; margin-top:50px;'>Developed by Vista Kaviani for Mandarin Oriental</div>", unsafe_allow_html=True)
