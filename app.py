import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- تنظیمات اصلی ---
HOTEL_WHATSAPP = "96891278434" 

st.set_page_config(page_title="MO Muscat | Digital Concierge", page_icon="🏮", layout="wide")

# --- استایل ظاهری لوکس ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1e2630 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stButton>button { 
        width: 100%; border-radius: 8px; border: none; 
        background-color: #8D734A; color: white; font-weight: bold; padding: 12px;
    }
    h1 { color: #8D734A; text-align: center; font-family: 'serif'; margin-top: -50px; }
    .status-box { padding: 10px; border-radius: 10px; background-color: #f0f2f6; text-align: center; margin-bottom: 20px; border: 1px solid #d1d9e6; }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- تابع ثبت آنالیز (لاگ سیستم) ---
def log_activity(room, category, details):
    file_path = "mo_analytics.csv"
    now = datetime.now()
    new_entry = pd.DataFrame([{
        'Date': now.strftime("%Y-%m-%d"),
        'Time': now.strftime("%H:%M"),
        'Room': room,
        'Type': category,
        'Content': details
    }])
    if not os.path.isfile(file_path):
        new_entry.to_csv(file_path, index=False)
    else:
        new_entry.to_csv(file_path, mode='a', header=False, index=False)

# --- پنل مدیریت (Sidebar) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    st.title("Management")
    with st.expander("📊 View Analytics"):
        pwd = st.text_input("Password:", type="password")
        if pwd == "MO2026":
            if os.path.isfile("mo_analytics.csv"):
                df = pd.read_csv("mo_analytics.csv")
                st.dataframe(df)
                st.download_button("📥 Download Weekly Report", df.to_csv(index=False), f"MO_Report_{datetime.now().strftime('%Y%m%d')}.csv")

# --- منطق اصلی برنامه ---
if "guest_identified" not in st.session_state:
    st.session_state.guest_identified = False

if os.path.exists("logo.png"):
    st.image("logo.png", width=120)
st.markdown("<h1>MANDARIN ORIENTAL</h1>", unsafe_allow_html=True)

if not st.session_state.guest_identified:
    r_in = st.text_input("Room Number:", placeholder="e.g. 211")
    if st.button("Login"):
        if r_in:
            st.session_state.room_number = r_in
            st.session_state.guest_identified = True
            log_activity(r_in, "System", "Guest Logged In")
            st.rerun()
else:
    st.markdown(f"<div class='status-box'>Welcome, Room <b>{st.session_state.room_number}</b></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # دکمه‌های واتس‌اپ با ثبت در آنالیز
    with col1:
        if st.button("🛎️ Room Service"):
            log_activity(st.session_state.room_number, "WhatsApp Click", "Room Service Button")
            msg = urllib.parse.quote(f"Hello, Room {st.session_state.room_number} requesting Room Service.")
            st.markdown(f'<meta http-equiv="refresh" content="0;url=https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text={msg}">', unsafe_allow_html=True)
            
    with col2:
        if st.button("🚕 Book Taxi"):
            log_activity(st.session_state.room_number, "WhatsApp Click", "Taxi Button")
            msg = urllib.parse.quote(f"Hello, Room {st.session_state.room_number} requesting Taxi.")
            st.markdown(f'<meta http-equiv="refresh" content="0;url=https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text={msg}">', unsafe_allow_html=True)

    # --- رابط چت با گراک ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("How can I assist you?"):
        log_activity(st.session_state.room_number, "AI Chat", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            # دستور سیستمی برای هدایت مسافر به دکمه‌های واتس‌اپ
            sys_prompt = (
                f"You are a luxury concierge at Mandarin Oriental Muscat. "
                f"1. Detect and respond in the guest's language. "
                f"2. IMPORTANT: If the guest asks for 'Room Service', 'Taxi', 'Food', or 'Transportation', "
                f"inform them that for immediate action, they should click on the 'Room Service' or 'Book Taxi' buttons "
                f"located right above this chat to connect with our team via WhatsApp. "
                f"Be formal and elite. Room: {st.session_state.room_number}"
            )
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_prompt}] + st.session_state.messages
            ).choices[0].message.content
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
