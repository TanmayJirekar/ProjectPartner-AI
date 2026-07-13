import json
import streamlit as st
from frontend.components.api_client import get, post, put

def render_profile(user):
    st.subheader("My Profile")
    with st.form("profile_form"):
        bio = st.text_area("Bio", value=user.get("bio") or "")
        skills = st.text_input("Skills (comma-separated)", value=", ".join(user.get("skills", [])))
        interests = st.text_input("Interests (comma-separated)", value=", ".join(user.get("interests", [])))
        experience = st.text_area("Experience", value=user.get("experience") or "")
        col1, col2 = st.columns(2)
        with col1:
            github = st.text_input("GitHub", value=user.get("github") or "")
            portfolio = st.text_input("Portfolio", value=user.get("portfolio") or "")
        with col2:
            linkedin = st.text_input("LinkedIn", value=user.get("linkedin") or "")
            availability = st.selectbox(
                "Availability", ["Available", "Partially Available", "Busy"],
                index=max(0, ["Available", "Partially Available", "Busy"].index(user.get("availability", "Available"))
                        if user.get("availability", "Available") in ["Available", "Partially Available", "Busy"] else 0),
            )
        if st.form_submit_button("Save Profile"):
            data = {
                "bio": bio,
                "skills": [s.strip() for s in skills.split(",") if s.strip()],
                "interests": [i.strip() for i in interests.split(",") if i.strip()],
                "experience": experience, "github": github, "linkedin": linkedin,
                "portfolio": portfolio, "availability": availability,
            }
            result = put(f"/auth/profile/{user['id']}", data)
            if result.get("user"):
                st.session_state.user = result["user"]
                st.success("Profile updated!")
            else:
                st.error("Update failed")

    st.markdown("### Resume Upload")
    resume = st.file_uploader("Upload PDF Resume", type=["pdf"])
    if resume and st.button("Extract Skills from Resume"):
        files = {"file": (resume.name, resume.getvalue(), "application/pdf")}
        import requests
        r = requests.post(f"http://localhost:5001/api/resume/upload/{user['id']}", files=files, timeout=30)
        if r.ok:
            data = r.json()
            st.success(f"Extracted skills: {', '.join(data.get('extracted', {}).get('skills', []))}")
            updated = get(f"/auth/profile/{user['id']}")
            if updated.get("id"):
                st.session_state.user = updated
        else:
            st.error("Upload failed")

    role = get(f"/ai/recommend-role/{user['id']}")
    if role.get("recommended_role"):
        st.info(f"AI Recommended Role: **{role['recommended_role']}** ({role.get('confidence', 0)}% confidence)")
