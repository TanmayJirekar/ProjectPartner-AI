import streamlit as st
from frontend.components.api_client import get, post, put

def render_team_workspace(user):
    st.subheader("Team Workspace")
    projects = get("/projects/")
    if not isinstance(projects, list) or not projects:
        st.info("No projects available.")
        return

    my_projects = []
    for p in projects:
        members = get(f"/teams/project/{p['id']}")
        if isinstance(members, list) and any(m.get("user_id") == user["id"] for m in members):
            my_projects.append(p)
        elif p.get("owner_id") == user["id"]:
            my_projects.append(p)

    if not my_projects:
        st.info("Join a project to access team workspace.")
        return

    project = st.selectbox("Select Project", my_projects, format_func=lambda p: p["title"])
    if not project:
        return

    pid = project["id"]
    tabs = st.tabs(["Dashboard", "Tasks", "Kanban", "Messages", "Progress"])

    with tabs[0]:
        members = get(f"/teams/project/{pid}")
        if isinstance(members, list):
            for m in members:
                st.markdown(f"**{m.get('name')}** — {m.get('role', 'Member')}")

    with tabs[1]:
        new_task = st.text_input("New Task Title")
        if st.button("Create Task") and new_task:
            post("/tasks/", {"project_id": pid, "title": new_task, "created_by": user["id"]})
            st.success("Task created!")
            st.rerun()

        tasks = get(f"/tasks/project/{pid}")
        if isinstance(tasks, list):
            for t in tasks:
                st.write(f"**{t['title']}** — {t['status']} (Priority: {t.get('priority', 'Medium')})")

    with tabs[2]:
        tasks = get(f"/tasks/project/{pid}")
        if isinstance(tasks, list):
            cols = st.columns(3)
            statuses = ["To Do", "Doing", "Done"]
            for i, status in enumerate(statuses):
                with cols[i]:
                    st.markdown(f"### {status}")
                    for t in [t for t in tasks if t["status"] == status]:
                        st.markdown(f"<div class='glass-card'>{t['title']}</div>", unsafe_allow_html=True)
                        new_status = st.selectbox("Move to", statuses, key=f"move_{t['id']}", index=statuses.index(status))
                        if new_status != status and st.button("Update", key=f"upd_{t['id']}"):
                            put(f"/tasks/{t['id']}", {"status": new_status})
                            st.rerun()

    with tabs[3]:
        msg = st.text_input("Team Message")
        if st.button("Send") and msg:
            post("/messages/", {"sender_id": user["id"], "project_id": pid, "content": msg})
            st.success("Message sent!")
        messages = get(f"/messages/user/{user['id']}", {"project_id": pid})
        if isinstance(messages, list):
            for m in messages:
                st.write(f"**{m.get('sender_name', 'User')}:** {m['content']}")

    with tabs[4]:
        success = get(f"/ai/predict-success/{pid}")
        if success.get("success_probability"):
            st.metric("Success Probability", f"{success['success_probability']}%")
            st.metric("Risk Level", success.get("risk", "N/A"))
            if success.get("risk_factors"):
                st.warning("Risk Factors: " + ", ".join(success["risk_factors"]))
        st.progress(project.get("completion_percent", 0) / 100, text=f"Completion: {project.get('completion_percent', 0)}%")
