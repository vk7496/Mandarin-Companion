import streamlit as st
from groq import Groq
import urllib.parse
from datetime import datetime

# ---------------------------------------------------------
# 1. تنظیمات اولیه
# ---------------------------------------------------------
st.set_page_config(
    page_title="Mandarin Oriental AI Concierge",
    page_icon="🏮",
    layout="centered"
)

# ---------------------------------------------------------
# 2. استایل لوکس (تم طلایی، سفید و مشکی)
# ---------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Vazirmatn', sans-serif; }
    
    .stApp { background-color: #ffffff; }
    
    /* سایدبار تیره و شیک */
    section[data-testid="stSidebar"] {
        background-color: #111111;
        color: #ffffff;
    }

    /* دکمه‌های طلایی */
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        border: 1px solid #8D734A !important;
        color: #8D734A !important;
        background-color: transparent !important;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #8D734A !important;
        color: white !important;
    }

    /* فیلدهای ورودی سایدبار */
    [data-testid="stSidebar"] label { color: #8D734A !important; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. راه‌اندازی API و دانش هتل
# ---------------------------------------------------------
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Missing GROQ_API_KEY in Secrets.")

try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        hotel_context = f.read()
except:
    hotel_context = "Mandarin Oriental Muscat: Luxury hotel in Oman."

# ---------------------------------------------------------
# 4. هدر اصلی (وسط‌چین کردن لوگو)
# ---------------------------------------------------------
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h1 style='text-align: center; color: #8D734A;'>🏮</h1>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #8D734A; letter-spacing: 2px; font-family: serif; margin-bottom: 0;'>MANDARIN ORIENTAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 14px; letter-spacing: 4px; margin-top: -10px;'>MUSCAT</p>", unsafe_allow_html=True)
st.write("---")

# ---------------------------------------------------------
# 5. سیستم چت (هوش مصنوعی)
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I assist you today?"):
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
                        "content": f"You are the professional AI Concierge for Mandarin Oriental Muscat. Use: {hotel_context}. Always reply in the same language as the guest. Be elegant and helpful."
                    },
                    *st.session_state.messages
                ],
                temperature=0.3
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except:
            st.error("I am currently experiencing a high volume of requests. Please try again.")

# ---------------------------------------------------------
# 6. سایدبار (سرویس‌ها و تاکسی)
# ---------------------------------------------------------
with st.sidebar:
    try:
        st.image("logo.png", width=120)
    except:
        pass
    
    st.markdown("### 🚕 VIP Otaxi Service")
    st.caption("No SIM required. Charge to room.")
    
    with st.form("taxi_form"):
        dest = st.selectbox("Destination", ["Airport", "Mutrah Souq", "Grand Mosque", "Opera House"])
        tm = st.time_input("Pickup Time", value=datetime.now().time())
        if st.form_submit_button("Request Taxi"):
            msg = f"🚖 TAXI REQUEST\nRoom: 302\nTo: {dest}\nAt: {tm}\nPayment: Room Charge"
            encoded_msg = urllib.parse.quote(msg)
            # شماره خود را اینجا جایگزین کنید
            st.markdown(f"[✅ Confirm on WhatsApp](https://wa.me/968XXXXXXXX?text={encoded_msg})")

    st.divider()
    st.markdown("### 🛎️ Quick Actions")
    
    # دکمه‌های سریع واتس‌اپ
    def wa_btn(label, text):
        url = f"https://wa.me/968XXXXXXXX?text={urllib.parse.quote(text)}"
        if st.button(label):
            st.markdown(f"[Send to Concierge]({url})")

    wa_btn("🧹 Housekeeping", "Please send housekeeping to Room 302.")
    wa_btn("☕ Room Service", "I would like to order breakfast in Room 302.")
    
    st.divider()
    if st.button("📍 Share My Location"):
        msg = "I am outside and need assistance. (Attach location in WhatsApp)"
        st.markdown(f"[Open WhatsApp](https://wa.me/968XXXXXXXX?text={urllib.parse.quote(msg)})")

    st.caption("v2.5 • Mandarin Oriental Muscat")
