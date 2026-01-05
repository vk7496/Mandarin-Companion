import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- تنظیمات اولیه ---
# شماره واتس‌اپ هتل را اینجا وارد کنید (بدون + یا 00، مثلاً برای عمان با 968 شروع شود)
HOTEL_WHATSAPP = "96891278434" 

st.set_page_config(page_title="MO Muscat | Digital Concierge", page_icon="🏮", layout="wide")

# --- استایل اختصاصی برای ظاهر داشبورد ---
st.markdown("""
    <style>
    /* منوی سمت چپ تیره */
    [data-testid="stSidebar"] { background-color: #1e2630 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* دکمه‌های طلایی ماندارین */
    .stButton>button { 
        width: 100%; border-radius: 8px; border: none; 
        background-color: #8D734A; color: white; font-weight: bold; padding: 12px;
    }
    .stButton>button:hover { background-color: #705b3a; color: white; }
    
    /* دکمه سبز واتس‌اپ در سایدبار */
    .wa-sidebar-btn {
        display: block; background-color: #25D366; color: white !important;
        text-align: center; padding: 12px; border-radius: 8px;
        text-decoration: none; font-weight: bold; margin-top: 25px;
    }
    
    h1 { color: #8D734A; text-align: center; font-family: 'serif'; margin-top: -50px; }
    .status-box { 
        padding: 10px; border-radius: 10px; background-color: #f0f2f6; 
        color: #1e2630; text-align: center; margin-bottom: 20px; border: 1px solid #d1d9e6;
    }
    </style>
    """, unsafe_allow_html=True)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- سیستم آنالیز پیشرفته ---
def log_analytics(room, activity):
    file_name = "mo_analytics.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_row = pd.DataFrame([[now, room, activity]], columns=['Timestamp', 'RoomNumber', 'Activity'])
    if not os.path.isfile(file_name):
        new_row.to_csv(file_name, index=False)
    else:
        new_row.to_csv(file_name, mode='a', header=False, index=False)

# --- داشبورد سمت چپ (Sidebar) ---
with st.sidebar:
    # فراخوانی مستقیم فایل logo.png از ریشه گیت‌هاب شما
    if os.path.exists("logo.png"):
        st.image("logo.png", width=160)
    st.title("Dashboard")
    st.write("---")
    st.button("🏠 Home")
    st.button("🛎️ Room Service")
    st.button("🚗 Transportation")
    
    # دکمه واتس‌اپ در منوی سمت چپ
    wa_general_text = urllib.parse.quote("سلام، من از طریق اپلیکیشن با شما تماس می‌گیرم.")
    st.markdown(f'<a href="https://wa.me/{HOTEL_WHATSAPP}?text={wa_general_text}" target="_blank" class="wa-sidebar-btn">💬 Connect on WhatsApp</a>', unsafe_allow_html=True)
    
    st.write("---")
    with st.expander("📊 Management Panel"):
        pwd = st.text_input("Admin Password:", type="password")
        if pwd == "MO2026":
            if os.path.isfile("mo_analytics.csv"):
                df = pd.read_csv("mo_analytics.csv")
                st.write(f"Total Requests: {len(df)}")
                st.dataframe(df)
                if st.button("🗑️ Clear Analytics"):
                    os.remove("mo_analytics.csv")
                    st.rerun()
            else:
                st.info("No logs yet.")

# --- محتوای اصلی ---
if "guest_identified" not in st.session_state:
    st.session_state.guest_identified = False

# لوگوی اصلی در وسط صفحه
if os.path.exists("logo.png"):
    st.image("logo.png", width=120)
st.markdown("<h1>MANDARIN ORIENTAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; margin-top:-20px;'>MUSCAT</p>", unsafe_allow_html=True)

if not st.session_state.guest_identified:
    room_input = st.text_input("Enter Room Number:", placeholder="e.g. 302")
    if st.button("Start Experience"):
        if room_input:
            st.session_state.room_number = room_input
            st.session_state.guest_identified = True
            log_analytics(room_input, "Guest Logged In")
            st.rerun()
else:
    st.markdown(f"<div class='status-box'>Connected: <b>Room {st.session_state.room_number}</b></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # متصل به واتس‌اپ با متن فارسی و شماره اتاق
        msg_rs = urllib.parse.quote(f"سلام، درخواست روم سرویس برای اتاق {st.session_state.room_number}")
        st.markdown(f'<a href="https://wa.me/{HOTEL_WHATSAPP}?text={msg_rs}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#8D734A; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold;">🛎️ Room Service</button></a>', unsafe_allow_html=True)
    
    with col2:
        msg_taxi = urllib.parse.quote(f"سلام، درخواست رزرو تاکسی برای اتاق {st.session_state.room_number}")
        st.markdown(f'<a href="https://wa.me/{HOTEL_WHATSAPP}?text={msg_taxi}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#8D734A; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold;">🚕 Book Taxi</button></a>', unsafe_allow_html=True)

    # چت‌بات با پشتیبانی عالی از فارسی
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Welcome. I am your AI Concierge. How can I help you today?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("سوال خود را بپرسید..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        # ثبت متن درخواست در آنالیز
        log_analytics(st.session_state.room_number, f"Chat: {prompt}")
        
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are a luxury concierge for Mandarin Oriental Muscat. Always be formal and polite. If the guest speaks Persian, respond in fluent, respectful Persian. Guest Room: {st.session_state.room_number}"},
                    *st.session_state.messages
                ]
            ).choices[0].message.content
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
