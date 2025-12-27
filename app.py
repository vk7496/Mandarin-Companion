import streamlit as st
from groq import Groq
import urllib.parse
import os

# 1. تنظیمات صفحه
st.set_page_config(
    page_title="MO Muscat AI Concierge",
    page_icon="🏮",
    layout="centered"
)

# 👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇
# شماره واتس‌اپ خودت (بدون +)
WHATSAPP_NUMBER = "96891278454" 
# 👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆

# 2. استایل سفارشی
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
    .stButton>button:hover { background-color: #8D734A !important; color: white !important; }
    
    /* استایل مخصوص برای کپی‌رایت که حتما دیده شود */
    .footer-container {
        position: static;
        bottom: 0;
        width: 100%;
        text-align: center;
        color: #8D734A;
        font-family: serif;
        padding: 40px 10px;
        margin-top: 50px;
        border-top: 1px solid #eee;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. اتصال به API
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.warning("API Key not found. Please check Streamlit Secrets.")

try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        hotel_context = f.read()
except:
    hotel_context = "Mandarin Oriental Muscat context."

# 4. هدر و لوگو
col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    # تلاش برای نمایش لوگو، اگر نبود متن نشان می‌دهد
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #8D734A;'>🏮</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: #8D734A; letter-spacing: 2px; margin-bottom: 0;'>MANDARIN ORIENTAL</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 14px; letter-spacing: 4px; margin-top: -10px;'>MUSCAT</p>", unsafe_allow_html=True)
st.write("---")

# 5. منطق تضمینی برای پیام خوش‌آمدگویی
# اگر حافظه خالی بود یا کلا پیام‌ها پاک شده بود، خوش‌آمدگویی اضافه شود
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = []
    welcome_msg = """Welcome to Mandarin Oriental, Muscat. I am your AI Concierge, fluent in over 20 languages. How may I assist you with your stay, dining, or transportation?
    
مرحباً بكم في ماندارين أورینتال، مسقط. أنا مساعدكم الذکی. كيف يمكنني مساعدتكم اليوم؟"""
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# نمایش پیام‌ها
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ورودی چت
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are the Elite AI Concierge for Mandarin Oriental Muscat. Context: {hotel_context}. You speak 20+ languages. Respond ONLY in the user's language. Be brief and elegant."
                    },
                    *st.session_state.messages
                ],
                temperature=0.3
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error("Connection error. Please try again.")

# 6. سایدبار
with st.sidebar:
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", width=120)
    
    st.markdown("### 🚕 VIP Otaxi")
    with st.form("taxi_form"):
        dest = st.selectbox("Destination", ["Airport", "Mutrah Souq", "Grand Mosque", "Opera House"])
        if st.form_submit_button("Request via WhatsApp"):
            msg = f"Requesting Otaxi to {dest}. Charge to room."
            st.markdown(f"[✅ Confirm](https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)})")

    st.divider()
    if st.button("🧹 Housekeeping"):
        st.markdown(f"[Send Request](https://wa.me/{WHATSAPP_NUMBER}?text=Housekeeping%20Request)")
    if st.button("📍 Share Location"):
        st.markdown(f"[Share Location](https://wa.me/{WHATSAPP_NUMBER}?text=Location%20Request)")

# 7. بخش کپی‌رایت (با طراحی جدید برای دیده شدن)
st.markdown("<br><br>", unsafe_allow_html=True) # ایجاد فاصله
st.markdown(
    """
    <div class="footer-container">
        <p style='margin-bottom: 5px; font-size: 14px;'>Designed & Developed by <strong>Vista Kaviani</strong></p>
        <p style='font-size: 10px; color: #999; letter-spacing: 2px;'>© 2024 AI INNOVATION PARTNERSHIP</p>
    </div>
    """, 
    unsafe_allow_html=True
)
