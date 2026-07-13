from flask import Blueprint, request, jsonify
from backend.utils.db import execute_query, parse_json_field
from backend.ai.skill_matcher import match_skills
from backend.ai.team_compatibility import predict_compatibility
from backend.ai.project_recommender import recommend_projects
from backend.ai.role_recommender import recommend_role
from backend.ai.success_predictor import predict_success
from backend.ai.groq_service import (
    smart_project_suggestions, project_improvement_suggestions,
    team_collaboration_assist, ai_chatbot,
)

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/skill-match", methods=["POST"])
def skill_match():
    data = request.json or {}
    result = match_skills(data.get("student_skills", []), data.get("project_skills", []))
    return jsonify(result)


@ai_bp.route("/team-compatibility", methods=["POST"])
def team_compatibility():
    data = request.json or {}
    result = predict_compatibility(data.get("team_members", []))
    return jsonify(result)


@ai_bp.route("/recommend-projects/<int:user_id>", methods=["GET"])
def recommend_user_projects(user_id):
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["skills"] = parse_json_field(user.get("skills"))
    user["interests"] = parse_json_field(user.get("interests"))

    projects = execute_query("SELECT * FROM projects WHERE status = 'Open'", fetch=True)
    apps = execute_query("SELECT user_id, project_id FROM applications", fetch=True)
    recommendations = recommend_projects(user, projects, apps)
    return jsonify(recommendations)


@ai_bp.route("/recommend-role/<int:user_id>", methods=["GET"])
def recommend_user_role(user_id):
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True)
    if not user:
        return jsonify({"error": "User not found"}), 404
    skills = parse_json_field(user.get("skills"))
    interests = parse_json_field(user.get("interests"))
    result = recommend_role(skills, user.get("experience", ""), interests)
    return jsonify(result)


@ai_bp.route("/predict-success/<int:project_id>", methods=["GET"])
def predict_project_success(project_id):
    project = execute_query("SELECT * FROM projects WHERE id = %s", (project_id,), fetch_one=True)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    members = execute_query(
        """SELECT u.* FROM teams t JOIN users u ON t.user_id = u.id WHERE t.project_id = %s""",
        (project_id,), fetch=True,
    )
    for m in members:
        m["skills"] = parse_json_field(m.get("skills"))
        m["interests"] = parse_json_field(m.get("interests"))

    tasks = execute_query("SELECT * FROM tasks WHERE project_id = %s", (project_id,), fetch=True)
    result = predict_success(project, members, tasks)
    return jsonify(result)


@ai_bp.route("/groq/suggestions/<int:user_id>", methods=["GET"])
def groq_suggestions(user_id):
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["skills"] = parse_json_field(user.get("skills"))
    user["interests"] = parse_json_field(user.get("interests"))
    projects = execute_query("SELECT title, domain, description FROM projects WHERE status = 'Open' LIMIT 10", fetch=True)
    suggestions = smart_project_suggestions(user, projects)
    return jsonify({"suggestions": suggestions})


@ai_bp.route("/groq/improve/<int:project_id>", methods=["GET"])
def groq_improve(project_id):
    project = execute_query("SELECT * FROM projects WHERE id = %s", (project_id,), fetch_one=True)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    project["technology_stack"] = parse_json_field(project.get("technology_stack"))
    suggestions = project_improvement_suggestions(project)
    return jsonify({"suggestions": suggestions})


@ai_bp.route("/groq/collaborate/<int:project_id>", methods=["GET"])
def groq_collaborate(project_id):
    project = execute_query("SELECT * FROM projects WHERE id = %s", (project_id,), fetch_one=True)
    team = execute_query("SELECT u.name, u.skills FROM teams t JOIN users u ON t.user_id = u.id WHERE t.project_id = %s", (project_id,), fetch=True)
    suggestions = team_collaboration_assist(project, team)
    return jsonify({"suggestions": suggestions})


@ai_bp.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json or {}
    response = ai_chatbot(data.get("message", ""), data.get("context"))
    return jsonify({"response": response})
