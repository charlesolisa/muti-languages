import streamlit as st
from gtts import gTTS
import tempfile
import os
from googletrans import Translator

# === State Initialization ===
def setup_state():
    defaults = {
        "logged_in": False, "username": "", "auth_choice": "Login",
        "registered_users": {"admin": "admin"},  # Example default user
        "wallpaper": None, "page": "Language App"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

setup_state()

# === Backgrounds ===
wallpapers = {
    "None": None,
    "Beach": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1350&q=80",
    "Mountains": "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1350&q=80",
    "Forest": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1350&q=80"
}

def set_background(url):
    if url:
        st.markdown(f"""
            <style>
            .stApp {{
              background-image: url("{url}");
              background-size: cover;
              background-position: center;
              background-repeat: no-repeat;
              background-attachment: fixed;
            }}
            </style>""", unsafe_allow_html=True)

def add_styles():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #B2BEB5;
        }
        </style>""", unsafe_allow_html=True)

# === Sidebar Navigation ===
st.sidebar.title("🔐 Authentication")
st.session_state.auth_choice = st.sidebar.radio("Choose:", ["Login", "Sign Up"])

if st.session_state.logged_in:
    st.sidebar.title("⚙️ Navigation")
    st.session_state.page = st.sidebar.radio("Go to:", ["Language App", "Settings"])
    if st.sidebar.button("Log Out"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# === Authentication Pages ===
def show_auth_page():
    add_styles()
    st.title("👋 Welcome to the Language Translator App")

    if st.session_state.auth_choice == "Login":
        st.subheader("🔑 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Log In"):
            if username in st.session_state.registered_users and \
               st.session_state.registered_users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    elif st.session_state.auth_choice == "Sign Up":
        st.subheader("📝 Sign Up")
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if not new_user or not new_pass:
                st.error("Username and password cannot be empty.")
            elif new_user in st.session_state.registered_users:
                st.warning("Username already exists. Please log in.")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match.")
            else:
                st.session_state.registered_users[new_user] = new_pass
                st.success("Account created! You can now log in.")

# === Translator with Audio ===
lang_map = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Russian': 'ru',
    'Japanese': 'ja',
    'Chinese (Simplified)': 'zh-cn',
    'Hindi': 'hi',
    'Arabic': 'ar',
    'Portuguese': 'pt',
    'Korean': 'ko',
    'Turkish': 'tr',
    'Dutch': 'nl'
}

def generate_tts(text, lang_code='en'):
    tts = gTTS(text=text, lang=lang_code)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name

def show_language_app():
    set_background(st.session_state.wallpaper)
    add_styles()
    st.title(f"🌍 Language Translator — Hello, {st.session_state.username}!")
    language = st.selectbox("Choose a language:", list(lang_map.keys()))

    st.subheader("🌐 Translate Anything")
    user_input = st.text_area("Enter text", height=100)

    if st.button("Translate"):
        translator = Translator()
        try:
            lang_code = lang_map[language]
            result = translator.translate(user_input, dest=lang_code)
            translated = result.text

            st.success(f"Translation in {language}:")
            st.markdown(f"""
                <div style="background-color: white; padding: 15px;
                            border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);
                            font-size: 18px;">
                  <strong>{translated}</strong>
                </div>""", unsafe_allow_html=True)

            audio_path = generate_tts(translated, lang_code)
            with open(audio_path, "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")
            os.remove(audio_path)

        except Exception as e:
            st.error(f"Translation failed. Error: {e}")

# === Settings Page ===
def show_settings_page():
    set_background(st.session_state.wallpaper)
    add_styles()
    st.title("⚙️ Settings")
    sel_wallpaper = st.selectbox("Choose Background Wallpaper", list(wallpapers.keys()))
    st.session_state.wallpaper = wallpapers[sel_wallpaper]
    st.success("Wallpaper applied!")

# === Routing ===
if not st.session_state.logged_in:
    show_auth_page()
else:
    if st.session_state.page == "Language App":
        show_language_app()
    elif st.session_state.page == "Settings":
        show_settings_page()
