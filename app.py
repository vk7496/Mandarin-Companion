import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- Configurations ---
HOTEL_WHATSAPP = "96812345678" # شماره هتل را اینجا اصلاح کنید

st.set_page_config(page_title="MO Muscat | Digital Concierge", page_icon="🏮", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1e2630 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    .stButton>button { 
        width: 100%; border-radius: 8px; border: none; 
        background-color: #8D734A; color: white; font-weight: bold; padding: 12px;
    }
    .wa-sidebar-btn {
        display: block; background-color: #25D366 !important; color: white !important;
        text-align: center; padding: 12px; border-radius: 8px;
        text-decoration: none; font-weight: bold; margin-top: 10px; margin-bottom: 20px;
    }
    h1 { color: #8D734A; text-align: center; font-family: 'serif'; margin-top: -50px; }
    .status-box { padding: 10px; border-radius: 10px; background-color: #f0f2f6; text-align: center; margin-bottom: 20px; color: #1e2630; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Analytics Logic ---
def log_event(room, category, details):
    file_path = "mo_analytics.csv"
    now = datetime.now()
    new_row = pd.DataFrame([{
        'Date': now.strftime("%Y-%m-%d"),
        'Time': now.strftime("%H:%M:%S"),
        'Room': room,
        'Category': category,
        'Content': details
    }])
    if not os.path.isfile(file_path):
        new_row.to_csv(file_path, index=False)
    else:
        new_row.to_csv(file_path, mode='a', header=False, index=False)

# --- Sidebar & Admin ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=150)
    st.title("Concierge Admin")
    
    # دکمه سبز رنگ واتس‌اپ در داشبورد
    wa_help_url = f"https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text=Hello%20Support"
    st.markdown(f'<a href="{wa_help_url}" target="_blank" class="wa-sidebar-btn">🟢 Online Support</a>', unsafe_allow_html=True)
    
    with st.expander("📊 Weekly Analytics"):
        pwd = st.text_input("Admin Password:", type="password")
        if pwd == "MO2026":
            if os.path.isfile("mo_analytics.csv"):
                df = pd.read_csv("mo_analytics.csv")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Report", csv, f"MO_Report_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
            else:
                st.info("No data recorded yet.")

# --- Main Interface ---
if "guest_identified" not in st.session_state:
    st.session_state.guest_identified = False

if os.path.exists("logo.png"):
    st.image("logo.png", width=120)
st.markdown("<h1>MANDARIN ORIENTAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; margin-top:-20px;'>MUSCAT</p>", unsafe_allow_html=True)

# مرحله ورود (کاملاً انگلیسی)
if not st.session_state.guest_identified:
    st.markdown("<h3 style='text-align: center;'>Welcome to Mandarin Oriental Muscat</h3>", unsafe_allow_html=True)
    room_number = st.text_input("Please enter your Room Number to access services:", placeholder="e.g. 211")
    if st.button("Connect to Concierge"):
        if room_number:
            st.session_state.room_number = room_number
            st.session_state.guest_identified = True
            log_event(room_number, "Access", "Guest Logged In")
            st.rerun()
        else:
            st.error("Please enter a valid room number.")

else:
    st.markdown(f"<div class='status-box'>Welcome, Room <b>{st.session_state.room_number}</b></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # دکمه‌های واتس‌اپ با ردیابی
    with col1:
        if st.button("🛎️ Room Service"):
            log_event(st.session_state.room_number, "WhatsApp", "Clicked Room Service")
            msg = urllib.parse.quote(f"Hello Room {st.session_state.room_number}, I would like to order Room Service.")
            link = f"https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text={msg}"
            st.markdown(f'<p style="text-align:center;"><a href="{link}" target="_blank" style="color:#8D734A; font-weight:bold;">Confirm on WhatsApp ➔</a></p>', unsafe_allow_html=True)
            
    with col2:
        if st.button("🚕 Book Taxi"):
            log_event(st.session_state.room_number, "WhatsApp", "Clicked Taxi")
            msg = urllib.parse.quote(f"Hello Room {st.session_state.room_number}, I need to book a taxi.")
            link = f"https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text={msg}"
            st.markdown(f'<p style="text-align:center;"><a href="{link}" target="_blank" style="color:#8D734A; font-weight:bold;">Confirm on WhatsApp ➔</a></p>', unsafe_allow_html=True)

    # --- Chatbot (Groq) ---
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("How can I help you today?"):
        log_event(st.session_state.room_number, "AI Chat", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            # دستور هدایت مسافر به دکمه‌های بالا
            sys_msg = (
                f"You are an elite concierge at Mandarin Oriental Muscat. "
                f"If the guest asks for food, room service, laundry, or transportation (taxi), "
                f"kindly guide them to click the 'Room Service' or 'Book Taxi' buttons at the top of the screen "
                f"to connect with our staff via WhatsApp. Answer in the same language as the guest."
            )
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages
            ).choices[0].message.content
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
