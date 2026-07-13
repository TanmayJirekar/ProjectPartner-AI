import streamlit as st
from frontend.components.api_client import get, post, put

def render_project_discovery(user):
    st.subheader("Discover Projects")

    col1, col2, col3 = st.columns(3)
    with col1:
        domain = st.selectbox("Domain", ["All", "AI/ML", "Web Development", "Mobile", "IoT", "Blockchain", "Data Science"])
    with col2:
        difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard", "Expert"])
    with col3:
        skill_filter = st.text_input("Filter by Skill")

    params = {"status": "Open"}
    if domain != "All":
        params["domain"] = domain
    if difficulty != "All":
        params["difficulty"] = difficulty
    if skill_filter:
        params["skill"] = skill_filter

    projects = get("/projects/", params)
    recommendations = get(f"/ai/recommend-projects/{user['id']}")

    if isinstance(recommendations, list) and recommendations:
        st.markdown("### AI Recommended Projects")
        for rec in recommendations[:3]:
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <h4>{rec['title']}</h4>
                    <p>Match Score: <strong>{rec['match_score']}%</strong> | {rec.get('recommendation', '')}</p>
                    <p>Skill Gap: {', '.join(rec.get('skill_gap', [])) or 'None'}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("### All Projects")
    if isinstance(projects, list):
        for p in projects:
            with st.expander(f"{p['title']} — {p.get('domain', 'N/A')} ({p.get('difficulty', 'N/A')})"):
                st.write(p.get("description", ""))
                st.write(f"**Skills:** {', '.join(p.get('required_skills', []))}")
                st.write(f"**Team Size:** {p.get('team_size')} | **Duration:** {p.get('duration', 'N/A')}")
                role = get(f"/ai/recommend-role/{user['id']}")
                if role.get("recommended_role"):
                    st.info(f"Suggested Role: {role['recommended_role']} ({role.get('confidence', 0)}% confidence)")
                if st.button("Apply to Join", key=f"apply_{p['id']}"):
                    result = post("/applications/", {
                        "project_id": p["id"], "user_id": user["id"],
                        "message": "I would like to join this project.", "role_applied": role.get("recommended_role"),
                    })
                    if result.get("message"):
                        st.success(result["message"])
                    else:
                        st.error(result.get("error", "Failed to apply"))
    else:
        st.warning("No projects found or backend unavailable.")
