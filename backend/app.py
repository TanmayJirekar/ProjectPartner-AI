import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from backend.config import UPLOAD_FOLDER
from backend.utils.db import execute_query
from backend.utils.resume_parser import extract_skills_from_resume
from backend.routes.auth_routes import auth_bp
from backend.routes.project_routes import projects_bp
from backend.routes.application_routes import applications_bp, teams_bp
from backend.routes.task_routes import tasks_bp
from backend.routes.message_routes import messages_bp, notifications_bp
from backend.routes.ai_routes import ai_bp
from backend.routes.admin_routes import admin_bp, hackathon_bp, analytics_bp

app = Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(projects_bp, url_prefix="/api/projects")
app.register_blueprint(applications_bp, url_prefix="/api/applications")
app.register_blueprint(teams_bp, url_prefix="/api/teams")
app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
app.register_blueprint(messages_bp, url_prefix="/api/messages")
app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
app.register_blueprint(ai_bp, url_prefix="/api/ai")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(hackathon_bp, url_prefix="/api/hackathons")
app.register_blueprint(analytics_bp, url_prefix="/api/analytics")


@app.route("/api/health")
def health():
    return {"status": "ok", "service": "ProjectPartner AI Backend"}


@app.route("/api/resume/upload/<int:user_id>", methods=["POST"])
def upload_resume(user_id):
    if "file" not in request.files:
        return {"error": "No file"}, 400
    file = request.files["file"]
    filename = secure_filename(f"resume_{user_id}_{file.filename}")
    filepath = UPLOAD_FOLDER / filename
    file.save(str(filepath))

    extracted = extract_skills_from_resume(str(filepath))
    existing = execute_query("SELECT skills FROM users WHERE id = %s", (user_id,), fetch_one=True)
    if existing:
        current_skills = json.loads(existing["skills"]) if existing.get("skills") else []
        merged = list(set(current_skills + extracted["skills"]))
        execute_query(
            "UPDATE users SET resume_path = %s, skills = %s, experience = %s WHERE id = %s",
            (filename, json.dumps(merged), extracted.get("experience", ""), user_id),
            commit=True,
        )
    return {"message": "Resume uploaded", "extracted": extracted}


@app.route("/api/milestones/project/<int:project_id>", methods=["GET"])
def get_milestones(project_id):
    milestones = execute_query("SELECT * FROM milestones WHERE project_id = %s", (project_id,), fetch=True)
    return milestones


@app.route("/api/milestones", methods=["POST"])
def create_milestone():
    data = request.get_json() or {}
    mid = execute_query(
        "INSERT INTO milestones (project_id, title, description, due_date) VALUES (%s, %s, %s, %s)",
        (data["project_id"], data["title"], data.get("description"), data.get("due_date")),
        commit=True,
    )
    return {"id": mid}, 201


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
