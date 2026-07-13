import streamlit as st
import plotly.express as px
from frontend.components.api_client import get, post

def render_hackathon(user):
    st.subheader("Hackathon Hub")
    tab1, tab2, tab3 = st.tabs(["Events", "Create Team", "AI Team Builder"])

    with tab1:
        hackathons = get("/hackathons/")
        if isinstance(hackathons, list) and hackathons:
            for h in hackathons:
                st.markdown(f"""
                <div class="glass-card">
                    <h4>{h['name']}</h4>
                    <p>{h.get('description', '')}</p>
                    <p>Domain: {h.get('domain', 'N/A')} | {h.get('start_date')} — {h.get('end_date')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hackathons yet.")

        with st.expander("Create Hackathon Event"):
            name = st.text_input("Hackathon Name")
            desc = st.text_area("Description")
            domain = st.text_input("Domain")
            if st.button("Create Event") and name:
                post("/hackathons/", {"name": name, "description": desc, "domain": domain, "created_by": user["id"]})
                st.success("Hackathon created!")
                st.rerun()

    with tab2:
        hackathons = get("/hackathons/")
        if isinstance(hackathons, list) and hackathons:
            h = st.selectbox("Select Hackathon", hackathons, format_func=lambda x: x["name"])
            team_name = st.text_input("Team Name")
            if st.button("Create Team") and team_name:
                post("/hackathons/teams", {
                    "hackathon_id": h["id"], "team_name": team_name,
                    "leader_id": user["id"], "members": [user["id"]],
                })
                st.success("Team created!")

    with tab3:
        st.markdown("Select candidates for AI team combination analysis:")
        users = get("/auth/users")
        if isinstance(users, list):
            selected = st.multiselect("Select Members", users, format_func=lambda u: u["name"])
            if st.button("Analyze Team") and len(selected) >= 2:
                members = [{"skills": u.get("skills", []), "interests": u.get("interests", []),
                            "experience": u.get("experience", ""), "availability": u.get("availability", "Available"),
                            "preferred_role": u.get("preferred_role", "")} for u in selected]
                result = post("/hackathons/suggest-team", {"candidates": members})
                if result.get("compatibility"):
                    st.metric("Compatibility", f"{result['compatibility']}%")
                    st.success(f"Team Fit: {result.get('team_fit', 'N/A')}")

def render_leaderboard():
    st.subheader("Leaderboard & Achievements")
    leaders = get("/analytics/leaderboard")
    if isinstance(leaders, list):
        for i, u in enumerate(leaders):
            badges = ", ".join(u.get("badges", [])) or "No badges yet"
            st.markdown(f"""
            <div class="glass-card">
                <h4>#{i+1} {u['name']}</h4>
                <p>Contributions: {u.get('contributions', 0)} | Completed: {u.get('completed_projects', 0)} | Rating: {u.get('team_rating', 0)}</p>
                <p>Badges: {badges}</p>
            </div>
            """, unsafe_allow_html=True)

        fig = px.bar(
            x=[u["name"] for u in leaders[:10]],
            y=[u.get("contributions", 0) for u in leaders[:10]],
            labels={"x": "User", "y": "Contributions"},
            color=[u.get("contributions", 0) for u in leaders[:10]],
            color_continuous_scale=["#3b82f6", "#8b5cf6"],
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
        st.plotly_chart(fig, use_container_width=True)
