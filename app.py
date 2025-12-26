import streamlit as st
from openai import OpenAI

# تنظیمات ظاهری
st.set_page_config(page_title="Mandarin Oriental AI Concierge", page_icon="🏮")

# استایل اختصاصی برای برند Mandarin Oriental (رنگ طلایی و مشکی)
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stButton>button { 
        border-radius: 5px; 
        background-color: #8D734A; 
        color: white;
        border: none;
        height: 3em;
    }
    .user-msg { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# مقداردهی اولیه OpenAI
# نکته: در نسخه نهایی API Key را در Streamlit Secrets بگذارید
client = OpenAI(api_key="YOUR_OPENAI_API_KEY") 

# شماره واتس‌اپ شما برای دمو (با کد کشور عمان 968 یا ایران 98)
YOUR_WHATSAPP_NUMBER = "96891278434" 

# بارگذاری دانش هتل
try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        hotel_context = f.read()
except FileNotFoundError:
    hotel_context = "Information about Mandarin Oriental Muscat."

st.image("https://images.luxuryhotelsmag.com/hotels/75333/75333_1.jpg", use_column_width=True) # یک تصویر لوکس از هتل
st.title("Welcome to Mandarin Oriental, Muscat")
st.write("I am your digital companion. How can I help you enjoy your stay?")

# مدیریت حافظه چت
if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایش پیام‌های قبلی
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# دریافت سوال کاربر
if prompt := st.chat_input("Ask me about the spa, dinner, or Muscat tours..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ارسال به OpenAI با در نظر گرفتن کانتکست هتل
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a luxury concierge for Mandarin Oriental Muscat. Use this info: {hotel_context}. Be polite, professional and helpful."},
                *st.session_state.messages
            ]
        )
        full_response = response.choices[0].message.content
        st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# دکمه‌های عملیاتی برای دمو
st.sidebar.header("Quick Requests")
st.sidebar.write("Try these direct services:")

# تابع ساخت لینک واتس‌اپ
def create_wa_link(text):
    return f"https://wa.me/{YOUR_WHATSAPP_NUMBER}?text={text.replace(' ', '%20')}"

if st.sidebar.button("🧹 Request Room Cleaning"):
    st.sidebar.markdown(f"[Confirm on WhatsApp]({create_wa_link('Hello, please send housekeeping to Room 302.')})")

if st.sidebar.button("☕ Order Morning Coffee"):
    st.sidebar.markdown(f"[Confirm on WhatsApp]({create_wa_link('I would like to order 2 Double Espressos to Room 302.')})")

if st.sidebar.button("🚗 Private Tour to Nizwa"):
    st.sidebar.markdown(f"[Confirm on WhatsApp]({create_wa_link('I am interested in booking a private tour to Nizwa for tomorrow.')})")
