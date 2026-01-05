import streamlit as st
from groq import Groq
import pandas as pd
from datetime import datetime
import os
import urllib.parse

# --- تنظیمات اولیه ---
# شماره واتس‌اپ هتل (حتماً با کد کشور و بدون صفر شروع شود)
HOTEL_WHATSAPP = "96891278434" 

st.set_page_config(page_title="MO Muscat | Digital Concierge", page_icon="🏮", layout="wide")

# --- طراحی ظاهری حرفه‌ای (Sidebar تیره و تم طلایی) ---
st.markdown("""
    <style>
    /* منوی سمت چپ تیره */
    [data-testid="stSidebar"] { background-color: #1e2630 !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    
    /* دکمه‌های اصلی طلایی ماندارین */
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

# اتصال به Groq (API KEY باید در استریم‌لیت ست شده باشد)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- تابع ذخیره دائمی آنالیز (اتاق + تاریخ + ساعت + جزئیات) ---
def log_activity(room, category, details):
    file_path = "mo_analytics_data.csv"
    now = datetime.now()
    new_entry = pd.DataFrame([{
        'Date': now.strftime("%Y-%m-%d"),
        'Time': now.strftime("%H:%M:%S"),
        'Room': room,
        'Category': category,
        'Request_Details': details
    }])
    
    if not os.path.isfile(file_path):
        new_entry.to_csv(file_path, index=False)
    else:
        new_entry.to_csv(file_path, mode='a', header=False, index=False)

# --- منوی سمت چپ (Sidebar) ---
with st.sidebar:
    # لود لوگو از فایل گیت‌هاب شما
    if os.path.exists("logo.png"):
        st.image("logo.png", width=160)
    
    st.title("Admin Dashboard")
    st.write("---")
    if st.button("🏠 Refresh App"): st.rerun()
    
    # دکمه واتس‌اپ در سایدبار
    wa_sidebar_msg = urllib.parse.quote("Hello, I am using the Digital Concierge and need help.")
    st.markdown(f'<a href="https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text={wa_sidebar_msg}" target="_blank" class="wa-sidebar-btn">💬 Connect on WhatsApp</a>', unsafe_allow_html=True)
    
    st.write("---")
    # بخش مدیریت داده‌ها (Admin)
    with st.expander("📊 Management Analytics"):
        pwd = st.text_input("Password:", type="password")
        if pwd == "MO2026":
            if os.path.isfile("mo_analytics_data.csv"):
                df = pd.read_csv("mo_analytics_data.csv")
                st.write(f"**Total interactions logged:** {len(df)}")
                st.dataframe(df)
                
                # دکمه دانلود گزارش برای محمد
                csv_file = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Weekly Report",
                    data=csv_file,
                    file_name=f"MO_Muscat_Report_{datetime.now().strftime('%Y-%m-%d')}.csv",
                    mime='text/csv'
                )
                
                if st.button("🗑️ Clear Local Logs"):
                    os.remove("mo_analytics_data.csv")
                    st.rerun()
            else:
                st.info("No data recorded yet.")

# --- محتوای اصلی (UI مسافر) ---
if "guest_identified" not in st.session_state:
    st.session_state.guest_identified = False

# هدر صفحه اصلی
if os.path.exists("logo.png"):
    st.image("logo.png", width=120)
st.markdown("<h1>MANDARIN ORIENTAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; margin-top:-20px;'>MUSCAT</p>", unsafe_allow_html=True)

# مرحله ۱: ورود شماره اتاق
if not st.session_state.guest_identified:
    room_input = st.text_input("Please enter your Room Number to begin:", placeholder="e.g. 211")
    if st.button("Access Services"):
        if room_input:
            st.session_state.room_number = room_input
            st.session_state.guest_identified = True
            log_activity(room_input, "SYSTEM", "Guest Logged In")
            st.rerun()
        else:
            st.warning("Room number is required.")

# مرحله ۲: خدمات اصلی
else:
    st.markdown(f"<div class='status-box'>Welcome, Room <b>{st.session_state.room_number}</b></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # واتس‌اپ انگلیسی (Room Service)
        rs_msg = urllib.parse.quote(f"Room {st.session_state.room_number}: Requesting Room Service.")
        st.markdown(f'<a href="https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text={rs_msg}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#8D734A; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold;">🛎️ Room Service</button></a>', unsafe_allow_html=True)
        # ثبت در آنالیز با کلیک (اختیاری: چون استریم‌لیت با لینک خارج می‌شود، معمولاً اولین چت را ثبت می‌کنیم)
    
    with col2:
        # واتس‌اپ انگلیسی (Taxi)
        tx_msg = urllib.parse.quote(f"Room {st.session_state.room_number}: Requesting Taxi/Transportation.")
        st.markdown(f'<a href="https://api.whatsapp.com/send?phone={HOTEL_WHATSAPP}&text={tx_msg}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#8D734A; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold;">🚕 Book Taxi</button></a>', unsafe_allow_html=True)

    # سیستم چت‌بوت هوشمند
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": f"Hello Room {st.session_state.room_number}, I am your AI Concierge. How can I assist you today?"}]

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Ask anything (Farsi/English)..."):
        # ثبت دقیق درخواست در فایل آنالیز
        log_activity(st.session_state.room_number, "GUEST_QUERY", prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are a luxury concierge for Mandarin Oriental Muscat. Be elite and formal. If the guest speaks Persian, respond in formal Persian. Otherwise, use English. Guest in Room {st.session_state.room_number}."},
                    *st.session_state.messages
                ]
            ).choices[0].message.content
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("<div style='text-align:center; color:#999; font-size:11px; margin-top:50px;'>© 2026 | Digital Concierge Concept for Mandarin Oriental Muscat</div>", unsafe_allow_html=True)
