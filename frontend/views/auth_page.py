import streamlit as st
from frontend.components.api_client import get, post, put

def render_auth():
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", key="login_btn"):
            result = post("/auth/login", {"email": email, "password": password})
            if result.get("user"):
                st.session_state.user = result["user"]
                st.session_state.logged_in = True
                st.success("Welcome back!")
                st.rerun()
            else:
                st.error(result.get("error", "Login failed"))

    with tab2:
        name = st.text_input("Full Name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_pass")
        col1, col2 = st.columns(2)
        with col1:
            college = st.text_input("College")
            branch = st.text_input("Branch")
        with col2:
            year = st.number_input("Year", min_value=1, max_value=5, value=2)
        if st.button("Register", key="reg_btn"):
            result = post("/auth/register", {
                "name": name, "email": reg_email, "password": reg_pass,
                "college": college, "branch": branch, "year": year,
            })
            if result.get("user"):
                st.session_state.user = result["user"]
                st.session_state.logged_in = True
                st.success("Account created!")
                st.rerun()
            else:
                st.error(result.get("error", "Registration failed"))
