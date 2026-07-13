import json
from flask import Blueprint, request, jsonify
from backend.utils.db import execute_query, parse_json_field

applications_bp = Blueprint("applications", __name__)
teams_bp = Blueprint("teams", __name__)


@applications_bp.route("/", methods=["POST"])
def apply():
    data = request.json or {}
    if not all(data.get(f) for f in ("project_id", "user_id")):
        return jsonify({"error": "project_id and user_id required"}), 400

    existing = execute_query(
        "SELECT id FROM applications WHERE project_id = %s AND user_id = %s",
        (data["project_id"], data["user_id"]), fetch_one=True,
    )
    if existing:
        return jsonify({"error": "Already applied"}), 409

    app_id = execute_query(
        "INSERT INTO applications (project_id, user_id, message, role_applied) VALUES (%s, %s, %s, %s)",
        (data["project_id"], data["user_id"], data.get("message"), data.get("role_applied")),
        commit=True,
    )

    project = execute_query("SELECT owner_id, title FROM projects WHERE id = %s", (data["project_id"],), fetch_one=True)
    if project:
        execute_query(
            "INSERT INTO notifications (user_id, title, message, type) VALUES (%s, %s, %s, %s)",
            (project["owner_id"], "New Join Request", f"Someone applied to join {project['title']}", "application"),
            commit=True,
        )
    return jsonify({"message": "Application submitted", "id": app_id}), 201


@applications_bp.route("/<int:app_id>/status", methods=["PUT"])
def update_status(app_id):
    data = request.json or {}
    status = data.get("status")
    if status not in ("Accepted", "Rejected", "Pending", "Withdrawn"):
        return jsonify({"error": "Invalid status"}), 400

    app = execute_query("SELECT * FROM applications WHERE id = %s", (app_id,), fetch_one=True)
    if not app:
        return jsonify({"error": "Application not found"}), 404

    execute_query("UPDATE applications SET status = %s WHERE id = %s", (status, app_id), commit=True)

    if status == "Accepted":
        execute_query(
            "INSERT IGNORE INTO teams (project_id, user_id, role) VALUES (%s, %s, %s)",
            (app["project_id"], app["user_id"], app.get("role_applied", "Member")), commit=True,
        )
        execute_query(
            "INSERT INTO notifications (user_id, title, message, type) VALUES (%s, %s, %s, %s)",
            (app["user_id"], "Application Accepted", "Your join request was accepted!", "success"), commit=True,
        )

    return jsonify({"message": f"Application {status.lower()}"})


@applications_bp.route("/project/<int:project_id>", methods=["GET"])
def project_applications(project_id):
    apps = execute_query(
        """SELECT a.*, u.name, u.email, u.skills FROM applications a
           JOIN users u ON a.user_id = u.id WHERE a.project_id = %s""",
        (project_id,), fetch=True,
    )
    for a in apps:
        a["skills"] = parse_json_field(a.get("skills"))
    return jsonify(apps)


@applications_bp.route("/user/<int:user_id>", methods=["GET"])
def user_applications(user_id):
    apps = execute_query(
        """SELECT a.*, p.title as project_title FROM applications a
           JOIN projects p ON a.project_id = p.id WHERE a.user_id = %s""",
        (user_id,), fetch=True,
    )
    return jsonify(apps)


@teams_bp.route("/project/<int:project_id>", methods=["GET"])
def get_team(project_id):
    members = execute_query(
        """SELECT t.*, u.name, u.email, u.skills, u.github FROM teams t
           JOIN users u ON t.user_id = u.id WHERE t.project_id = %s""",
        (project_id,), fetch=True,
    )
    for m in members:
        m["skills"] = parse_json_field(m.get("skills"))
    return jsonify(members)
