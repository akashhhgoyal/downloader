import json
import streamlit as st

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)["users"]

def authenticate(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True
    return False

def login_page():
    st.title("🔐 Login - Call Recording System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state["logged_in"] = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid username or password")
