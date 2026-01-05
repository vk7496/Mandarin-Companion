import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- تنظیمات اولیه ---
HOTEL_WHATSAPP = "96891278434" 

st.set_page_config(page_title="MO Muscat | Digital Concierge", page_icon="🏮", layout="wide")

# --- استایل ظاهری ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1e2630 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stButton>button { 
        width: 100%; border-radius: 8px; border: none; 
        background-color: #8D734A; color: white; font-weight: bold; padding: 12px;
    }
    .wa-link {
        display: block; background-color: #25D366 !important; color: white !important;
        text-align: center; padding: 12px; border-radius: 8px;
        text-decoration: none; font-weight: bold; margin-top: 20px;
    }
    h1 { color: #8D734A; text-align: center; font-family: 'serif'; margin-top: -50px; }
    .status-box { padding: 10px; border-radius: 10px; background-color: #f0f2f6; text-align: center; border: 1px solid #d1d9e6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- تابع ذخیره آنالیز با جزئیات دقیق (Log) ---
def save_analytics(room, request_type, details):
    file_path = "mo_analytics.csv"
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    
    # ساخت دیتای جدید مطابق خواسته شما
    new_data = pd.DataFrame([[date_str, time_str, room, request_type, details]], 
                            columns=['Date', 'Time', 'Room', 'Type', 'Description'])
    
    if not os.path.isfile(file_path):
        new_data.to_csv(file_path, index=False)
    else:
        new_data.to_csv(file_path, mode='a', header=False, index=False)

# --- منوی سمت چپ ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    st.title("Admin Dashboard")
    st.write("---")
    
    # بخش مدیریت آنالیزها
    with st.expander("📊 Weekly Analytics Report"):
        pwd = st.text_input("Admin Password:", type="password")
        if pwd == "MO2026":
            if os.path.isfile("mo_analytics.csv"):
                df = pd.read_csv("mo_analytics.csv")
                st.write("### Guest Interactions")
                st.dataframe(df)
                # دکمه دانلود برای ذخیره هفتگی توسط مدیر
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Weekly Report (CSV)", data=csv, file_name=f"MO_Report_{datetime.now().strftime('%Y%m%d')}.csv")
            else:
                st.info("No data recorded for this week yet.")

# --- رابط کاربری مسافر ---
if "guest_identified" not in st.session_state:
    st.session_state.guest_identified = False

if os.path.exists("logo.png"):
    st.image("logo.png", width=120)
st.markdown("<h1>MANDARIN ORIENTAL</h1>", unsafe_allow_html=True)

if not st.session_state.guest_identified:
    room_no = st.text_input("Room Number:", placeholder="e.g. 211")
    if st.button("Connect"):
        if room_no:
            st.session_state.room_number = room_no
            st.session_state.guest_identified = True
            save_analytics(room_no, "System", "Guest Logged In")
            st.rerun()
else:
    st.markdown(f"<div class='status-box'>Welcome, Room <b>{st.session_state.room_number}</b></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        wa_rs = urllib.parse.quote(f"Room {st.session_state.room_number}: Room Service Request")
        if st.markdown(f'<a href="https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text={wa_rs}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#8D734A; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer;">🛎️ Room Service</button></a>', unsafe_allow_html=True):
            save_analytics(st.session_state.room_number, "WhatsApp", "Clicked Room Service")
            
    with col2:
        wa_tx = urllib.parse.quote(f"Room {st.session_state.room_number}: Taxi Booking Request")
        if st.markdown(f'<a href="https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text={wa_tx}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#8D734A; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer;">🚕 Book Taxi</button></a>', unsafe_allow_html=True):
            save_analytics(st.session_state.room_number, "WhatsApp", "Clicked Taxi Booking")

    # چت‌بوت هوشمند
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if prompt := st.chat_input("How can I help you?"):
        save_analytics(st.session_state.room_number, "AI Chat", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
