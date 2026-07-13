import streamlit as st
from frontend.components.api_client import get, post

def render_chatbot(user):
    st.subheader("AI Assistant")
    st.markdown("Ask about project guidance, skill recommendations, team formation, or learning resources.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input("Ask ProjectPartner AI...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        context = {"name": user.get("name"), "skills": user.get("skills"), "interests": user.get("interests")}
        result = post("/ai/chatbot", {"message": prompt, "context": context})
        response = result.get("response", "Sorry, I could not process that.")
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    st.markdown("---")
    st.markdown("### Quick AI Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Get Project Suggestions"):
            result = get(f"/ai/groq/suggestions/{user['id']}")
            st.info(result.get("suggestions", "No suggestions available."))
    with col2:
        projects = get("/projects/")
        if isinstance(projects, list):
            my = [p for p in projects if p.get("owner_id") == user["id"]]
            if my and st.button("Get Improvement Tips"):
                result = get(f"/ai/groq/improve/{my[0]['id']}")
                st.info(result.get("suggestions", "No suggestions."))
