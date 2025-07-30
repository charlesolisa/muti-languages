import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import uuid
import json
import hashlib
from datetime import datetime, timedelta

USER_DATA_FILE = "users.json"

# -------------------- User Handling --------------------
def load_users():
    if not os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(USER_DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

users = load_users()

# -------------------- Session Defaults --------------------
if "font_size" not in st.session_state:
    st.session_state.font_size = 16

if "font_color" not in st.session_state:
    st.session_state.font_color = "#333333"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.login_time = None

# -------------------- Language Options --------------------
language_options = {
    'English': 'en',
    'French': 'fr',
    'Spanish': 'es',
    'German': 'de',
    'Arabic': 'ar',
    'Chinese (Simplified)': 'zh-CN'
}

# -------------------- Dynamic Styles --------------------
def set_styles():
    font_size = st.session_state.get("font_size", 16)
    font_color = st.session_state.get("font_color", "#333333")

    st.markdown(f"""
    <style>
    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
        font-size: {font_size}px;
        color: {font_color};
    }}

    .stApp {{
        background-color: #f4f6f7;
    }}

    .white-box {{
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin: 20px 0;
    }}

    .even-box {{
        background-color: #d0f0c0;
        padding: 10px;
        border-left: 5px solid #4caf50;
        margin-bottom: 10px;
        border-radius: 10px;
    }}

    .odd-box {{
        background-color: #ffcccb;
        padding: 10px;
        border-left: 5px solid #e53935;
        margin-bottom: 10px;
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# -------------------- Sidebar Settings --------------------
def settings_panel():
    st.sidebar.markdown("## ⚙️ Settings")
    st.session_state.font_size = st.sidebar.slider("Font Size", 12, 30, st.session_state.font_size)
    st.session_state.font_color = st.sidebar.color_picker("Font Color", st.session_state.font_color)

# -------------------- Auth Pages --------------------
def register_page():
    st.markdown("<div class='white-box'><h2>📝 Register</h2></div>", unsafe_allow_html=True)
    new_username = st.text_input("Choose a username", max_chars=20)
    new_password = st.text_input("Choose a password", type="password")
    if st.button("Register"):
        if new_username in users:
            st.warning("Username already exists.")
        elif not new_username or not new_password:
            st.warning("All fields required.")
        elif not new_username.isalpha():
            st.error("Username should only contain letters.")
        else:
            users[new_username] = {
                "password": hash_password(new_password),
                "role": "user"
            }
            save_users(users)
            st.success("✅ Registration successful! You can now log in.")

def login_page():
    st.markdown("<div class='white-box'><h1>🔐 Login to Continue</h1></div>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]["password"] == hash_password(password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = users[username].get("role", "user")
            st.session_state.login_time = datetime.now().isoformat()
            st.success(f"✅ Welcome back, {username.title()}!")
            st.rerun()
        else:
            st.error("Invalid credentials.")

def logout():
    for key in ['logged_in', 'username', 'role', 'login_time']:
        st.session_state.pop(key, None)
    st.rerun()

# -------------------- Main Feature --------------------
def even_odd_app():
    name = st.text_input("Enter your name")
    num = st.number_input("Enter a number", step=1, format="%i")
    selected_language = st.selectbox("Translate to", list(language_options.keys()))

    if st.button("🚀 Check & Translate"):
        if not name or not name.isalpha():
            st.warning("Please enter a valid name.")
            return

        result = f"{name}, {num} is an even number 💯" if num % 2 == 0 else f"{name}, {num} is an odd number ✌️"
        box_class = "even-box" if num % 2 == 0 else "odd-box"
        st.markdown(f"<div class='{box_class}'><strong>{result}</strong></div>", unsafe_allow_html=True)

        lang_code = language_options[selected_language]
        try:
            translated = GoogleTranslator(source='auto', target=lang_code).translate(result)
            st.markdown(f"🌍 <b>{selected_language}:</b> {translated}", unsafe_allow_html=True)

            with st.spinner("🔊 Generating audio..."):
                tts = gTTS(text=translated, lang=lang_code)
                filename = f"{uuid.uuid4()}.mp3"
                tts.save(filename)
                audio_data = open(filename, 'rb').read()
                st.audio(audio_data, format='audio/mp3')
                os.remove(filename)

        except Exception as e:
            st.error(f"Translation/audio failed: {e}")

# -------------------- Main App --------------------
def main_app():
    settings_panel()  # show sidebar settings

    st.markdown(f"""
    <div class='white-box'>
        <h1>👋 Hello, {st.session_state.username.title()}!</h1>
        <p>Welcome to the <b>Even & Odd Checker</b> 🌟</p>
    </div>
    """, unsafe_allow_html=True)

    even_odd_app()

    st.markdown("---")
    if st.button("🔒 Logout"):
        logout()

# -------------------- Run App --------------------
set_styles()

# Session timeout after 30 minutes
if st.session_state.get("login_time"):
    login_time = datetime.fromisoformat(st.session_state["login_time"])
    if datetime.now() - login_time > timedelta(minutes=30):
        st.warning("Session expired. Please log in again.")
        logout()

if st.session_state.logged_in:
    main_app()
else:
    menu = st.radio("Navigation", ["Login", "Register"])
    if menu == "Register":
        register_page()
    else:
        login_page()
