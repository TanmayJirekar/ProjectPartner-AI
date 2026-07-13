import json
from flask import Blueprint, request, jsonify
from backend.utils.db import execute_query, parse_json_field
from backend.ai.team_compatibility import predict_compatibility

admin_bp = Blueprint("admin", __name__)
hackathon_bp = Blueprint("hackathons", __name__)
analytics_bp = Blueprint("analytics", __name__)


@admin_bp.route("/users", methods=["GET"])
def admin_users():
    users = execute_query("SELECT id, name, email, college, is_admin, created_at FROM users", fetch=True)
    return jsonify(users)


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    execute_query("DELETE FROM users WHERE id = %s AND is_admin = 0", (user_id,), commit=True)
    return jsonify({"message": "User removed"})


@admin_bp.route("/projects", methods=["GET"])
def admin_projects():
    projects = execute_query("SELECT p.*, u.name as owner_name FROM projects p JOIN users u ON p.owner_id = u.id", fetch=True)
    return jsonify(projects)


@admin_bp.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    execute_query("DELETE FROM projects WHERE id = %s", (project_id,), commit=True)
    return jsonify({"message": "Project removed"})


@hackathon_bp.route("/", methods=["GET"])
def list_hackathons():
    hackathons = execute_query("SELECT * FROM hackathons ORDER BY start_date DESC", fetch=True)
    return jsonify(hackathons)


@hackathon_bp.route("/", methods=["POST"])
def create_hackathon():
    data = request.json or {}
    hid = execute_query(
        "INSERT INTO hackathons (name, description, start_date, end_date, domain, max_team_size, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (data["name"], data.get("description"), data.get("start_date"), data.get("end_date"),
         data.get("domain"), data.get("max_team_size", 4), data.get("created_by")),
        commit=True,
    )
    return jsonify({"id": hid, "message": "Hackathon created"}), 201


@hackathon_bp.route("/teams", methods=["POST"])
def create_hackathon_team():
    data = request.json or {}
    tid = execute_query(
        "INSERT INTO hackathon_teams (hackathon_id, team_name, leader_id, members) VALUES (%s, %s, %s, %s)",
        (data["hackathon_id"], data["team_name"], data.get("leader_id"), json.dumps(data.get("members", []))),
        commit=True,
    )
    return jsonify({"id": tid, "message": "Team created"}), 201


@hackathon_bp.route("/teams/<int:hackathon_id>", methods=["GET"])
def list_hackathon_teams(hackathon_id):
    teams = execute_query("SELECT * FROM hackathon_teams WHERE hackathon_id = %s", (hackathon_id,), fetch=True)
    for t in teams:
        t["members"] = parse_json_field(t.get("members"))
    return jsonify(teams)


@hackathon_bp.route("/suggest-team", methods=["POST"])
def suggest_team():
    data = request.json or {}
    members = data.get("candidates", [])
    result = predict_compatibility(members)
    return jsonify(result)


@analytics_bp.route("/dashboard", methods=["GET"])
def dashboard_analytics():
    users = execute_query("SELECT skills, interests, created_at FROM users", fetch=True)
    projects = execute_query("SELECT domain, status, completion_percent, difficulty FROM projects", fetch=True)

    skill_counts = {}
    domain_counts = {}
    for u in users:
        for s in parse_json_field(u.get("skills")):
            skill_counts[s] = skill_counts.get(s, 0) + 1

    for p in projects:
        d = p.get("domain") or "Other"
        domain_counts[d] = domain_counts.get(d, 0) + 1

    total_projects = len(projects)
    completed = sum(1 for p in projects if p.get("status") == "Completed")
    completion_rate = round(completed / max(total_projects, 1) * 100, 1)

    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:8]

    return jsonify({
        "total_users": len(users),
        "total_projects": total_projects,
        "completion_rate": completion_rate,
        "top_skills": [{"skill": s, "count": c} for s, c in top_skills],
        "top_domains": [{"domain": d, "count": c} for d, c in top_domains],
        "avg_completion": round(sum(p.get("completion_percent", 0) for p in projects) / max(total_projects, 1), 1),
    })


@analytics_bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    users = execute_query(
        "SELECT id, name, contributions, completed_projects, team_rating FROM users WHERE is_admin = 0 ORDER BY contributions DESC, completed_projects DESC LIMIT 20",
        fetch=True,
    )
    badges = execute_query("SELECT user_id, badge_name FROM badges", fetch=True)
    badge_map = {}
    for b in badges:
        badge_map.setdefault(b["user_id"], []).append(b["badge_name"])

    for u in users:
        u["badges"] = badge_map.get(u["id"], [])
    return jsonify(users)


@analytics_bp.route("/badges", methods=["POST"])
def award_badge():
    data = request.json or {}
    execute_query(
        "INSERT INTO badges (user_id, badge_name) VALUES (%s, %s)",
        (data["user_id"], data["badge_name"]), commit=True,
    )
    return jsonify({"message": "Badge awarded"})
