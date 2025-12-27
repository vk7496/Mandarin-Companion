import streamlit as st
from groq import Groq
import urllib.parse
from datetime import datetime
import os

# 1. تنظیمات صفحه
st.set_page_config(
    page_title="MO Muscat AI Concierge",
    page_icon="🏮",
    layout="centered"
)

# ---------------------------------------------------------
# تنظیمات شماره واتس‌اپ (فقط عدد داخل گیومه را تغییر بده)
# ---------------------------------------------------------
# 👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇
WHATSAPP_NUMBER = "96891278434" 
# 👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆
# نکته: شماره را با کد کشور (968) و بدون + وارد کن.
# ---------------------------------------------------------

# 2. استایل سفارشی (لوکس و مینیمال)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Vazirmatn', sans-serif; }
    .stApp { background-color: #ffffff; }
    
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        border: 1px solid #8D734A !important;
        color: #8D734A !important;
        background-color: transparent !important;
    }
    .stButton>button:hover {
        background-color: #8D734A !important;
        color: white !important;
    }
    
    .footer-text {
        text-align: center;
        color: #8D734A;
        font-family: serif;
        padding: 30px;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. اتصال به API (Groq)
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# بارگذاری دانش هتل
try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        hotel_context = f.read()
except:
    hotel_context = "Mandarin Oriental Muscat: A luxury hotel in Oman."

# 4. هدر و لوگو
col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #8D734A;'>🏮</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #8D734A; letter-spacing: 2px; margin-bottom: 0;'>MANDARIN ORIENTAL</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 14px; letter-spacing: 4px; margin-top: -10px;'>MUSCAT</p>", unsafe_allow_html=True)
st.write("---")

# 5. مدیریت چت و پیام خوش‌آمدگویی (۲۰ زبان)
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome_msg = """Welcome to Mandarin Oriental, Muscat. I am your AI Concierge, capable of communicating in over 20 languages. How may I assist you today?
    
مرحباً بكم في ماندارين أورینتال، مسقط. أنا مساعدكم الذکی، أتقن أكثر من ٢٠ لغة لخدمتكم. كيف يمكنني مساعدتكم اليوم؟"""
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are the Elite AI Concierge for Mandarin Oriental Muscat. Context: {hotel_context}. You support 20+ languages. Respond in the same language as the guest. Be elegant and formal."
                },
                *st.session_state.messages
            ],
            temperature=0.3
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# 6. سایدبار (واتس‌اپ هوشمند متصل به شماره شما)
with st.sidebar:
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", width=120)
    
    st.markdown("### 🚕 VIP Otaxi Service")
    st.caption("No Local SIM Required")
    
    with st.form("taxi_form"):
        dest = st.selectbox("Destination", ["Airport", "Mutrah Souq", "Grand Mosque", "Opera House", "Royal Opera House"])
        if st.form_submit_button("Request via WhatsApp"):
            msg = f"Hello MO Concierge, I would like to request an Otaxi to: {dest}. Please charge this to my room. (Requested via AI Companion)"
            st.markdown(f"[✅ Confirm on WhatsApp](https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)})")

    st.divider()
    st.markdown("### 🛎️ Quick Requests")
    
    if st.button("🧹 Request Housekeeping"):
        hk_msg = "Dear Housekeeping, I would like to request room cleaning for my suite. Thank you."
        st.markdown(f"[Send to WhatsApp](https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(hk_msg)})")
        
    if st.button("🍽️ Room Service"):
        rs_msg = "Hello, I would like to view the In-Room Dining menu or place an order."
        st.markdown(f"[Send to WhatsApp](https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(rs_msg)})")

    st.divider()
    if st.button("📍 Share My Location"):
        loc_msg = "I am currently outside the hotel and need assistance. (I will attach my location in the next message)"
        st.markdown(f"[Contact Concierge](https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(loc_msg)})")

# 7. بخش کپی‌رایت نهایی
st.write("---")
st.markdown(
    """
    <div class="footer-text">
        <p style='margin-bottom: 5px;'>Designed & Developed by <strong>Vista Kaviani</strong></p>
        <p style='font-size: 10px; color: #999; letter-spacing: 2px;'>© 2024 AI INNOVATION PARTNERSHIP | MO MUSCAT</p>
    </div>
    """, 
    unsafe_allow_html=True
)
