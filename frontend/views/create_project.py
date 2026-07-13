import streamlit as st
from frontend.components.api_client import get, post

def render_create_project(user):
    st.subheader("Create New Project")
    with st.form("create_project"):
        title = st.text_input("Project Title")
        description = st.text_area("Description")
        problem = st.text_area("Problem Statement")
        objectives = st.text_area("Objectives")
        outcome = st.text_area("Expected Outcome")
        tech = st.text_input("Technology Stack (comma-separated)")
        skills = st.text_input("Required Skills (comma-separated)")
        col1, col2, col3 = st.columns(3)
        with col1:
            team_size = st.number_input("Team Size", min_value=1, max_value=20, value=4)
            domain = st.selectbox("Domain", ["AI/ML", "Web Development", "Mobile", "IoT", "Blockchain", "Data Science", "Other"])
        with col2:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Expert"])
            duration = st.text_input("Duration", placeholder="e.g. 3 months")
        with col3:
            fe = st.number_input("Frontend Devs Needed", 0, 10, 1)
            be = st.number_input("Backend Devs Needed", 0, 10, 1)
            ml = st.number_input("ML Engineers Needed", 0, 10, 0)
            ui = st.number_input("UI Designers Needed", 0, 10, 0)

        if st.form_submit_button("Create Project"):
            if not title:
                st.error("Title is required")
            else:
                result = post("/projects/", {
                    "owner_id": user["id"], "title": title, "description": description,
                    "problem_statement": problem, "objectives": objectives, "expected_outcome": outcome,
                    "technology_stack": [t.strip() for t in tech.split(",") if t.strip()],
                    "required_skills": [s.strip() for s in skills.split(",") if s.strip()],
                    "team_size": team_size, "domain": domain, "difficulty": difficulty,
                    "duration": duration,
                    "team_requirements": {
                        "Frontend Developer": fe, "Backend Developer": be,
                        "ML Engineer": ml, "UI/UX Designer": ui,
                    },
                })
                if result.get("project"):
                    st.success(f"Project '{title}' created!")
                else:
                    st.error(result.get("error", "Failed to create project"))

    st.markdown("### Upload Project Media")
    project_list = get("/projects/")
    if isinstance(project_list, list) and project_list:
        my_projects = [p for p in project_list if p.get("owner_id") == user["id"]]
        if my_projects:
            selected = st.selectbox("Select Project for Upload", my_projects, format_func=lambda p: p["title"])
            uploaded = st.file_uploader("Upload Images/Diagrams/Videos", type=["png", "jpg", "jpeg", "pdf", "pptx", "mp4"])
            if uploaded and st.button("Upload"):
                import requests
                files = {"file": (uploaded.name, uploaded.getvalue())}
                r = requests.post(f"http://localhost:5001/api/projects/{selected['id']}/upload", files=files, timeout=30)
                st.success("Uploaded!" if r.ok else "Upload failed")
