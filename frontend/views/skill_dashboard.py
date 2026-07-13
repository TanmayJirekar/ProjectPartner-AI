import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from frontend.components.api_client import get, post, put

def render_skill_dashboard(user):
    st.subheader("Skill Dashboard")
    skills = user.get("skills", [])
    if not skills:
        st.info("Add skills to your profile to see the dashboard.")
        return

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(x=skills, y=[1]*len(skills), labels={"x": "Skill", "y": ""},
                     title="Your Skills", color=skills, color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", yaxis_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        interests = user.get("interests", [])
        if interests:
            fig2 = go.Figure(data=[go.Pie(labels=interests, hole=0.4,
                                          marker_colors=["#3b82f6", "#8b5cf6", "#6366f1", "#a855f7", "#2563eb"])])
            fig2.update_layout(title="Domain Expertise", paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig2, use_container_width=True)

    recs = get(f"/ai/recommend-projects/{user['id']}")
    if isinstance(recs, list) and recs:
        st.markdown("**AI Match Scores**")
        for r in recs[:5]:
            st.progress(r["match_score"] / 100, text=f"{r['title']} — {r['match_score']}%")
