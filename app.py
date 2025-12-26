import streamlit as st
from groq import Groq

# تنظیمات اصلی صفحه
st.set_page_config(page_title="Mandarin Oriental Concierge", page_icon="🏮", layout="centered")

# طراحی ظاهری (CSS) برای ایجاد حس لوکس
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    /* استایل دکمه‌های سایدبار */
    .stButton>button { 
        border-radius: 4px; 
        background-color: #8D734A; 
        color: white;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #705a38;
        border: none;
        color: white;
    }
    /* رنگ تیره برای سایدبار */
    section[data-testid="stSidebar"] {
        background-color: #1a1a1a;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# اتصال به Groq از طریق Secrets
# در پنل استریم‌لیت کلمه GROQ_API_KEY را تعریف کنید
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Error: Please set GROQ_API_KEY in Streamlit Secrets.")

# بارگذاری دانش هتل از فایل محلی
try:
    with open("knowledge.txt", "r", encoding="utf-8") as f:
        hotel_context = f.read()
except FileNotFoundError:
    hotel_context = "Mandarin Oriental Muscat is a luxury hotel in Shatti Al Qurum, Oman."

# بخش هدر برنامه
try:
    # اگر فایل header.jpg را در گیت‌هاب آپلود کرده‌اید:
    st.image("header.jpg", use_container_width=True)
except:
    # در غیر این صورت فقط متن نمایش داده می‌شود
    st.title("🏮 Mandarin Oriental, Muscat")

st.markdown("### Welcome to your Digital Companion")
st.write("How may I assist you with your stay or your journey in Oman today?")

# مدیریت حافظه چت (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []

# نمایش پیام‌های قبلی چت
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# دریافت ورودی جدید از کاربر
if prompt := st.chat_input("Ask me about the spa, dining, or local tours..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # فراخوانی هوش مصنوعی Groq
    with st.chat_message("assistant"):
        try:
            # استفاده از قدرتمندترین مدل رایگان Groq
            chat_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a luxury concierge for Mandarin Oriental Muscat. Use this knowledge: {hotel_context}. Be extremely polite, professional, and helpful. Respond in the same language as the guest."
                    },
                    *st.session_state.messages
                ],
            )
            full_response = chat_completion.choices[0].message.content
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error("I apologize, but I am experiencing a brief connection issue. Please try again or contact our reception.")

# سایدبار برای درخواست‌های سریع و واتس‌اپ
st.sidebar.header("Quick Services")
st.sidebar.write("Instant requests via WhatsApp:")

# شماره شما برای دمو (بدون + یا صفر اول)
YOUR_NUMBER = "96891278434" 

def create_wa_link(text):
    import urllib.parse
    encoded_text = urllib.parse.quote(text)
    return f"https://wa.me/{YOUR_NUMBER}?text={encoded_text}"

if st.sidebar.button("🧹 Request Housekeeping"):
    st.sidebar.markdown(f"[Confirm on WhatsApp]({create_wa_link('Hello, please send housekeeping to my room (Room 302).')})")

if st.sidebar.button("☕ Order Room Service"):
    st.sidebar.markdown(f"[Confirm on WhatsApp]({create_wa_link('I would like to order breakfast/coffee to Room 302.')})")

if st.sidebar.button("🚕 Book a Private Tour"):
    st.sidebar.markdown(f"[Confirm on WhatsApp]({create_wa_link('I am interested in a private tour to Nizwa or Jebel Akhdar.')})")

st.sidebar.divider()
st.sidebar.caption("Mandarin Oriental Muscat AI Companion v1.0")
