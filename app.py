import streamlit as st
import json
import os
from transformers import BlenderbotForConditionalGeneration, BlenderbotTokenizer
import datetime

# Set page configuration
st.set_page_config(page_title="AI Chatbot", layout="wide", initial_sidebar_state="collapsed")

# Styling for Login/Register Form and Sidebar
st.markdown("""
    <style>
        body {
            font-family: Arial, sans-serif;
        }

        .chat-message {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 10px;
            max-width: 70%;
            word-wrap: break-word;
        }

        .user-message {
            background-color: #d1ecf1;
            align-self: flex-end;
            margin-left: auto;
        }

        .bot-message {
            background-color: #f8d7da;
            align-self: flex-start;
        }

        .message-time {
            font-size: 0.8em;
            margin-top: 5px;
        }

        .form-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
        }

        .form-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            max-width: 400px;
            width: 100%;
            transition: transform 0.5s ease-in-out;
        }

        .form-card.slide-in {
            transform: translateX(0);
        }

        .form-card.slide-out {
            transform: translateX(100%);
        }

        .form-field {
            margin-bottom: 20px;
        }

        .form-field input {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }

        .form-field label {
            margin-bottom: 5px;
            font-weight: bold;
            display: block;
        }

        .chat-input-container {
            display: flex;
            gap: 10px;
        }

        .chat-input-container input {
            flex-grow: 1;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }

        .chat-input-container button {
            padding: 10px 20px;
            background-color: #6f42c1;
            color: white;
            border: none;
            border-radius: 5px;
        }

        /* Purple color theme */
        .purple-bg {
            background-color: #6f42c1;
            color: white;
        }

        /* Avatar styling */
        .avatar {
            width: 150px;
            height: 150px;
            margin: 0 auto;
            border-radius: 50%;
            background: linear-gradient(145deg, #6f42c1, #9b59b6);
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 60px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }

        .profile-card {
            margin: 0 auto;
            max-width: 400px;
            text-align: center;
        }

        .profile-card p {
            color: #6c757d;
            font-size: 1.2em;
        }

        /* Horizontal navigation bar styling */
        .horizontal-nav {
            display: flex;
            justify-content: space-evenly;
            background-color: #6f42c1;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 10px;
            color: white;
        }

        .horizontal-nav button {
            background-color: #6f42c1;
            color: white;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            border-radius: 5px;
            font-size: 16px;
        }

        .horizontal-nav button:hover {
            background-color: #9b59b6;
        }
    </style>
""", unsafe_allow_html=True)

# Session state variables
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'username' not in st.session_state:
    st.session_state.username = None

USER_DATA_PATH = 'user_data.json'

# Helper functions
def save_user_data(username, password, email, dob, phone):
    user_data = {"password": password, "email": email, "dob": dob, "phone": phone}
    if os.path.exists(USER_DATA_PATH):
        try:
            with open(USER_DATA_PATH, 'r') as f:
                all_users = json.load(f)
        except json.JSONDecodeError:
            all_users = {}
    else:
        all_users = {}

    all_users[username] = user_data

    with open(USER_DATA_PATH, 'w') as f:
        json.dump(all_users, f, indent=4)

def get_user_data(username):
    if os.path.exists(USER_DATA_PATH):
        with open(USER_DATA_PATH, 'r') as f:
            all_users = json.load(f)
        return all_users.get(username)
    return None

def validate_user(username, password):
    user = get_user_data(username)
    return user and user["password"] == password

def get_bot_response(user_input):
    try:
        model_name = "facebook/blenderbot-400M-distill"
        model = BlenderbotForConditionalGeneration.from_pretrained(model_name)
        tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
        inputs = tokenizer([user_input], return_tensors="pt")
        reply_ids = model.generate(**inputs)
        return tokenizer.decode(reply_ids[0], skip_special_tokens=True)
    except Exception as e:
        return "Sorry, I couldn't process that. Please try again."

# Pages
def auth_form():
    st.markdown("<h2 class='purple-bg' style='text-align: center;'>Welcome to AI Chatbot</h2>", unsafe_allow_html=True)
    form_mode = st.radio("", ["Login", "Register"], horizontal=True, label_visibility="collapsed")

    if form_mode == "Register":
        st.markdown("<div class='form-container'><div class='form-card slide-in'>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        email = st.text_input("Email")
        dob = st.date_input("Date of Birth")
        phone = st.text_input("Phone Number")

        if st.button("Register"):
            if not username or not password or not email or not phone:
                st.error("All fields are required!")
            else:
                save_user_data(username, password, email, str(dob), phone)
                st.success("Registration successful! Please log in.")
        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='form-container'><div class='form-card slide-in'>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if validate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
            else:
                st.error("Invalid credentials")
        st.markdown("</div></div>", unsafe_allow_html=True)

def chat_interface():
    st.markdown("<h1 style='text-align: center;'>AI Chat Bot 🤖</h1>", unsafe_allow_html=True)
    with st.container():
        user_input = st.text_input("Your Message", key="user_input", placeholder="Type here...")
        if st.button("Send"):
            if user_input:
                response = get_bot_response(user_input)
                st.session_state.chat_history.append({
                    "user": user_input,
                    "bot": response,
                    "time": datetime.datetime.now().strftime("%H:%M:%S"),
                })

    for message in st.session_state.chat_history:
        st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message['user']}
                <div class="message-time">{message['time']}</div>
            </div>
            <div class="chat-message bot-message">
                <strong>Bot:</strong> {message['bot']}
                <div class="message-time">{message['time']}</div>
            </div>
        """, unsafe_allow_html=True)

def profile_page():
    user_data = get_user_data(st.session_state.username)
    if user_data:
        st.markdown("""<div class="avatar">🧑‍💻</div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <h2 style="margin-top: 10px; color: #495057;">Hello, {st.session_state.username}!</h2>
        <p style="color: #6c757d; font-size: 1.2em;">Welcome to your profile page</p>
        <div class="profile-card">
            <p><strong>Email:</strong> {user_data['email']}</p>
            <p><strong>Date of Birth:</strong> {user_data['dob']}</p>
            <p><strong>Phone Number:</strong> {user_data['phone']}</p>
        </div>
    """, unsafe_allow_html=True)

def main():
    if st.session_state.logged_in:
        # Create Horizontal Nav Bar
        st.markdown("""
            <div class="horizontal-nav">
                <button onclick="window.location.href='/chat'">Chat</button>
                <button onclick="window.location.href='/profile'">Profile</button>
                <button onclick="window.location.href='/logout'">Logout</button>
            </div>
        """, unsafe_allow_html=True)
        page = st.experimental_get_query_params().get('page', ['chat'])[0]

        if page == 'chat':
            chat_interface()
        elif page == 'profile':
            profile_page()
    else:
        auth_form()

if __name__ == "__main__":
    main()
