import streamlit as st
from frontend.components.api_client import get, put

def render_contributor_discovery(user):
    st.subheader("Find Contributors")
    projects = get("/projects/")
    if not isinstance(projects, list):
        st.warning("Backend unavailable")
        return

    my_projects = [p for p in projects if p.get("owner_id") == user["id"]]
    if not my_projects:
        st.info("Create a project first to discover contributors.")
        return

    project = st.selectbox("Select Your Project", my_projects, format_func=lambda p: p["title"])
    ranked = get(f"/projects/contributors/{project['id']}")

    st.markdown("### AI Contributor Ranking")
    if isinstance(ranked, list):
        for c in ranked[:10]:
            st.markdown(f"""
            <div class="glass-card">
                <h4>{c['name']}</h4>
                <p>Match Score: <strong>{c['match_score']}%</strong></p>
                <p>Recommended Role: {c.get('role', 'N/A')} | Availability: {c.get('availability', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Could not load contributors.")

    st.markdown("### Join Requests")
    apps = get(f"/applications/project/{project['id']}")
    if isinstance(apps, list):
        for app in apps:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{app.get('name')}** — {app.get('status')} — Role: {app.get('role_applied', 'N/A')}")
            with col2:
                if app["status"] == "Pending" and st.button("Accept", key=f"acc_{app['id']}"):
                    put(f"/applications/{app['id']}/status", {"status": "Accepted"})
                    st.rerun()
            with col3:
                if app["status"] == "Pending" and st.button("Reject", key=f"rej_{app['id']}"):
                    put(f"/applications/{app['id']}/status", {"status": "Rejected"})
                    st.rerun()
