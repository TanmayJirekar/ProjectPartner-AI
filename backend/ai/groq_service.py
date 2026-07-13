"""Groq AI Integration for smart suggestions and chatbot."""

import json
import os

try:
    from groq import Groq
except ImportError:
    Groq = None

from backend.config import GROQ_API_KEY


def _get_client():
    if not GROQ_API_KEY or Groq is None:
        return None
    return Groq(api_key=GROQ_API_KEY)


def _fallback_response(prompt_type, context):
    fallbacks = {
        "project_suggestions": f"Based on your profile, consider exploring projects in {context.get('domain', 'AI/Web Development')}. Your top skills match well with collaborative team projects.",
        "improvements": "Suggestions: Add authentication, implement API documentation, add unit tests, and set up CI/CD pipeline.",
        "collaboration": "Suggested tasks: Define sprint milestones, assign roles clearly, schedule weekly sync meetings, and document decisions.",
        "chatbot": "I can help with project guidance, skill recommendations, and team formation. Set GROQ_API_KEY in your environment for full AI responses.",
    }
    return fallbacks.get(prompt_type, fallbacks["chatbot"])


def groq_chat(system_prompt, user_message, context=None):
    client = _get_client()
    if not client:
        return _fallback_response("chatbot", context or {})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception:
        return _fallback_response("chatbot", context or {})


def smart_project_suggestions(user_profile, projects):
    context = {"domain": user_profile.get("interests", ["Technology"])[0] if isinstance(user_profile.get("interests"), list) else "Technology"}
    project_list = "\n".join(f"- {p.get('title')} ({p.get('domain')})" for p in projects[:5])
    prompt = f"User skills: {user_profile.get('skills')}. Interests: {user_profile.get('interests')}.\nAvailable projects:\n{project_list}\nSuggest top 3 projects with brief reasons."
    return groq_chat("You are ProjectPartner AI assistant. Give concise project recommendations.", prompt, context)


def project_improvement_suggestions(project):
    prompt = f"Project: {project.get('title')}\nDescription: {project.get('description')}\nTech: {project.get('technology_stack')}\nSuggest 5 improvements."
    return groq_chat("You are a project mentor. Give actionable improvement suggestions.", prompt)


def team_collaboration_assist(project, team_info):
    prompt = f"Project: {project.get('title')}\nTeam size: {len(team_info)}\nSuggest tasks, milestones, and conflict resolution tips."
    return groq_chat("You are a team collaboration assistant.", prompt)


def ai_chatbot(message, user_context=None):
    ctx = json.dumps(user_context or {})
    return groq_chat(
        "You are ProjectPartner AI chatbot. Help with project guidance, skill recommendations, team recommendations, and learning resources. Be concise and helpful.",
        f"User context: {ctx}\nQuestion: {message}",
        user_context,
    )
