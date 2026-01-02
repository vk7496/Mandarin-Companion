import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime
import os

# --- تنظیمات صفحه ---
st.set_page_config(page_title="MO Muscat | Digital Concierge", page_icon="🏮")

# --- استایل لوکس اختصاصی ---
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stButton>button { 
        width: 100%; border-radius: 8px; border: 1px solid #8D734A; 
        background-color: #8D734A; color: white; font-weight: bold;
    }
    .stButton>button:hover { background-color: #6d5939; color: white; }
    .footer { text-align: center; padding: 20px; color: #8D734A; font-size: 12px; margin-top: 50px; border-top: 1px solid #eee; }
    h1 { color: #8D734A; text-align: center; font-family: 'serif'; }
    .status-box { padding: 10px; border-radius: 5px; background-color: #f0ede9; color: #8D734A; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# اتصال به Groq (مطمئن شوید API Key در Secrets ست شده است)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- مدیریت ورود مسافر (فقط شماره اتاق) ---
if "guest_identified" not in st.session_state:
    st.session_state.guest_identified = False

st.markdown("<h1>MANDARIN ORIENTAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>MUSCAT</p>", unsafe_allow_html=True)

# مرحله ۱: ورود فقط با شماره اتاق (Privacy-First)
if not st.session_state.guest_identified:
    with st.container():
        st.write("### Digital Concierge Access")
        st.write("Please enter your room number to enjoy our personalized AI services.")
        room_num = st.text_input("Room Number:", placeholder="e.g. 402")
        if st.button("Access Services"):
            if room_num:
                st.session_state.room_number = room_num
                st.session_state.guest_identified = True
                
                # ذخیره آمار در فایل CSV
                file_name = "hotel_analytics.csv"
                new_entry = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), room_num]], columns=['DateTime', 'RoomNumber'])
                if not os.path.isfile(file_name):
                    new_entry.to_csv(file_name, index=False)
                else:
                    new_entry.to_csv(file_name, mode='a', header=False, index=False)
                st.rerun()
            else:
                st.error("Please enter a valid room number.")

# مرحله ۲: اینترفیس اصلی خدمات
else:
    st.markdown(f"<div class='status-box'>Connected: <b>Room {st.session_state.room_number}</b></div>", unsafe_allow_html=True)
    
    # دکمه‌های خدمات سریع
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧹 Room Service"):
            st.info(f"Your request for Room {st.session_state.room_number} has been logged.")
    with col2:
        if st.button("🚕 Book Transportation"):
            st.info("Directing your request to the concierge desk...")

    # چت‌بات هوشمند
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
                messages=[{"role": "system", "content": f"You are a luxury concierge for Mandarin Oriental Muscat. The guest is in room {st.session_state.room_number}. Be extremely polite and formal."}, *st.session_state.messages]
            ).choices[0].message.content
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- پنل مدیریت (برای شما و مدیر هتل) ---
with st.expander("📊 Management Analytics (Password Required)"):
    pwd = st.text_input("Admin Password:", type="password")
    if pwd == "MO2026": # پسورد پیشنهادی
        if os.path.isfile("hotel_analytics.csv"):
            data = pd.read_csv("hotel_analytics.csv")
            st.write(f"Total Interactions: **{len(data)}**")
            st.dataframe(data)
            st.download_button("Download Full CSV Report", data.to_csv(index=False), "mo_report.csv")
            if st.button("🗑️ Wipe All Data (End Trial)"):
                os.remove("hotel_analytics.csv")
                st.success("All guest data has been deleted.")
        else:
            st.write("No data recorded yet.")

st.markdown("<div class='footer'>© 2025 | Developed by Vista Kaviani for Mandarin Oriental</div>", unsafe_allow_html=True)
