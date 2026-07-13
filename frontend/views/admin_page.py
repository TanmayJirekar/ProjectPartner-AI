import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from frontend.components.api_client import get, delete

def render_admin():
    st.subheader("Admin Dashboard")
    analytics = get("/analytics/dashboard")
    if analytics.get("total_users") is not None:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Users", analytics["total_users"])
        col2.metric("Total Projects", analytics["total_projects"])
        col3.metric("Completion Rate", f"{analytics['completion_rate']}%")
        col4.metric("Avg Progress", f"{analytics['avg_completion']}%")

        col1, col2 = st.columns(2)
        with col1:
            skills = analytics.get("top_skills", [])
            if skills:
                fig = px.bar(x=[s["skill"] for s in skills], y=[s["count"] for s in skills],
                             labels={"x": "Skill", "y": "Count"}, color=[s["count"] for s in skills],
                             color_continuous_scale=["#3b82f6", "#8b5cf6"])
                fig.update_layout(title="Most Popular Skills", plot_bgcolor="rgba(0,0,0,0)",
                                  paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            domains = analytics.get("top_domains", [])
            if domains:
                fig2 = go.Figure(data=[go.Pie(labels=[d["domain"] for d in domains],
                                              values=[d["count"] for d in domains], hole=0.4,
                                              marker_colors=["#3b82f6", "#8b5cf6", "#6366f1", "#a855f7"])])
                fig2.update_layout(title="Most Active Domains", paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig2, use_container_width=True)

    tab1, tab2 = st.tabs(["Manage Users", "Manage Projects"])
    with tab1:
        users = get("/admin/users")
        if isinstance(users, list):
            for u in users:
                if not u.get("is_admin"):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"**{u['name']}** — {u['email']}")
                    with col2:
                        if st.button("Remove", key=f"del_u_{u['id']}"):
                            delete(f"/admin/users/{u['id']}")
                            st.rerun()
    with tab2:
        projects = get("/admin/projects")
        if isinstance(projects, list):
            for p in projects:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{p['title']}** by {p.get('owner_name', 'Unknown')} — {p.get('status')}")
                with col2:
                    if st.button("Remove", key=f"del_p_{p['id']}"):
                        delete(f"/admin/projects/{p['id']}")
                        st.rerun()
