import json
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from backend.utils.db import execute_query, parse_json_field
from backend.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from backend.ai.skill_matcher import match_skills
from backend.ai.role_recommender import recommend_role

projects_bp = Blueprint("projects", __name__)


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _serialize_project(project):
    for field in ("required_skills", "technology_stack", "team_requirements", "images"):
        project[field] = parse_json_field(project.get(field))
    return project


@projects_bp.route("/", methods=["GET"])
def list_projects():
    domain = request.args.get("domain")
    skill = request.args.get("skill")
    difficulty = request.args.get("difficulty")
    status = request.args.get("status", "Open")

    query = "SELECT p.*, u.name as owner_name FROM projects p JOIN users u ON p.owner_id = u.id WHERE 1=1"
    params = []
    if status:
        query += " AND p.status = %s"
        params.append(status)
    if domain:
        query += " AND p.domain = %s"
        params.append(domain)
    if difficulty:
        query += " AND p.difficulty = %s"
        params.append(difficulty)

    projects = execute_query(query, tuple(params) if params else None, fetch=True)
    results = []
    for p in projects:
        p = _serialize_project(p)
        if skill:
            skills = [s.lower() for s in p.get("required_skills", [])]
            if skill.lower() not in skills and not any(skill.lower() in s for s in skills):
                continue
        results.append(p)
    return jsonify(results)


@projects_bp.route("/<int:project_id>", methods=["GET"])
def get_project(project_id):
    project = execute_query(
        "SELECT p.*, u.name as owner_name FROM projects p JOIN users u ON p.owner_id = u.id WHERE p.id = %s",
        (project_id,), fetch_one=True,
    )
    if not project:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(_serialize_project(project))


@projects_bp.route("/", methods=["POST"])
def create_project():
    data = request.json or {}
    if not data.get("title") or not data.get("owner_id"):
        return jsonify({"error": "Title and owner_id required"}), 400

    project_id = execute_query(
        """INSERT INTO projects (owner_id, title, description, problem_statement, objectives,
           expected_outcome, technology_stack, required_skills, team_size, team_requirements,
           difficulty, duration, domain, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            data["owner_id"], data["title"], data.get("description"), data.get("problem_statement"),
            data.get("objectives"), data.get("expected_outcome"),
            json.dumps(data.get("technology_stack", [])),
            json.dumps(data.get("required_skills", [])),
            data.get("team_size", 4),
            json.dumps(data.get("team_requirements", {})),
            data.get("difficulty", "Medium"), data.get("duration"), data.get("domain"),
            data.get("status", "Open"),
        ),
        commit=True,
    )

    execute_query(
        "INSERT INTO teams (project_id, user_id, role) VALUES (%s, %s, %s)",
        (project_id, data["owner_id"], "Project Owner"), commit=True,
    )
    project = execute_query("SELECT * FROM projects WHERE id = %s", (project_id,), fetch_one=True)
    return jsonify({"message": "Project created", "project": _serialize_project(project)}), 201


@projects_bp.route("/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    data = request.json or {}
    fields, values = [], []
    json_fields = {"technology_stack", "required_skills", "team_requirements", "images"}
    allowed = {"title", "description", "problem_statement", "objectives", "expected_outcome",
               "team_size", "difficulty", "duration", "domain", "status", "completion_percent"}
    for field in allowed:
        if field in data:
            fields.append(f"{field} = %s")
            values.append(data[field])
    for field in json_fields:
        if field in data:
            fields.append(f"{field} = %s")
            values.append(json.dumps(data[field]))

    if fields:
        values.append(project_id)
        execute_query(f"UPDATE projects SET {', '.join(fields)} WHERE id = %s", tuple(values), commit=True)

    project = execute_query("SELECT * FROM projects WHERE id = %s", (project_id,), fetch_one=True)
    return jsonify({"project": _serialize_project(project)})


@projects_bp.route("/<int:project_id>/upload", methods=["POST"])
def upload_media(project_id):
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if not file.filename or not _allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(f"project_{project_id}_{file.filename}")
    filepath = UPLOAD_FOLDER / filename
    file.save(str(filepath))

    project = execute_query("SELECT images FROM projects WHERE id = %s", (project_id,), fetch_one=True)
    images = parse_json_field(project.get("images") if project else None)
    images.append(filename)
    execute_query("UPDATE projects SET images = %s WHERE id = %s", (json.dumps(images), project_id), commit=True)
    return jsonify({"message": "File uploaded", "filename": filename})


@projects_bp.route("/contributors/<int:project_id>", methods=["GET"])
def rank_contributors(project_id):
    project = execute_query("SELECT * FROM projects WHERE id = %s", (project_id,), fetch_one=True)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    required_skills = parse_json_field(project.get("required_skills"))
    users = execute_query(
        "SELECT id, name, skills, interests, experience, availability, preferred_role FROM users WHERE is_admin = 0",
        fetch=True,
    )

    ranked = []
    for user in users:
        user_skills = parse_json_field(user.get("skills"))
        result = match_skills(user_skills, required_skills)
        role = recommend_role(user_skills, user.get("experience", ""), parse_json_field(user.get("interests")))
        ranked.append({
            "user_id": user["id"],
            "name": user["name"],
            "match_score": result["match_score"],
            "role": role["recommended_role"],
            "availability": user.get("availability"),
        })

    ranked.sort(key=lambda x: x["match_score"], reverse=True)
    return jsonify(ranked[:20])
