import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from frontend.styles.theme import CUSTOM_CSS
from frontend.views.auth_page import render_auth
from frontend.views.profile_page import render_profile
from frontend.views.skill_dashboard import render_skill_dashboard
from frontend.views.create_project import render_create_project
from frontend.views.project_discovery import render_project_discovery
from frontend.views.contributor_discovery import render_contributor_discovery
from frontend.views.team_workspace import render_team_workspace
from frontend.views.hackathon_page import render_hackathon, render_leaderboard
from frontend.views.admin_page import render_admin
from frontend.views.chatbot_page import render_chatbot
from frontend.components.api_client import get

st.set_page_config(
    page_title="ProjectPartner AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None

    st.markdown('<p class="gradient-text">ProjectPartner AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">Intelligent Project Collaboration & Team Formation Platform</p>', unsafe_allow_html=True)

    if not st.session_state.logged_in:
        render_auth()
        st.markdown("""
        <div class="glass-card" style="margin-top:2rem;">
            <h3>Why ProjectPartner AI?</h3>
            <ul>
                <li>AI-powered skill matching & project recommendations</li>
                <li>Smart team compatibility analysis</li>
                <li>Real-time collaboration workspace</li>
                <li>Hackathon team formation</li>
                <li>Role & success prediction engines</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return

    user = st.session_state.user

    with st.sidebar:
        st.markdown(f"### Welcome, {user['name']}")
        st.caption(f"{user.get('college', '')} | {user.get('branch', '')}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

        notifs = get(f"/notifications/user/{user['id']}")
        if isinstance(notifs, list):
            unread = sum(1 for n in notifs if not n.get("is_read"))
            if unread:
                st.warning(f"{unread} unread notifications")

        page = st.radio("Navigation", [
            "Dashboard", "My Profile", "Discover Projects", "Create Project",
            "Find Contributors", "Team Workspace", "Hackathons", "Leaderboard",
            "AI Assistant", "Admin Panel",
        ])

    if page == "Dashboard":
        render_skill_dashboard(user)
    elif page == "My Profile":
        render_profile(user)
    elif page == "Discover Projects":
        render_project_discovery(user)
    elif page == "Create Project":
        render_create_project(user)
    elif page == "Find Contributors":
        render_contributor_discovery(user)
    elif page == "Team Workspace":
        render_team_workspace(user)
    elif page == "Hackathons":
        render_hackathon(user)
    elif page == "Leaderboard":
        render_leaderboard()
    elif page == "AI Assistant":
        render_chatbot(user)
    elif page == "Admin Panel":
        if user.get("is_admin"):
            render_admin()
        else:
            st.warning("Admin access required. Login as admin@projectpartner.ai / admin123")


if __name__ == "__main__":
    main()
