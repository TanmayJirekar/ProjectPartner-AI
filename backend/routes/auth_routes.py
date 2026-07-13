import json
from flask import Blueprint, request, jsonify
from backend.utils.db import execute_query, parse_json_field
from backend.utils.auth import hash_password, verify_password

auth_bp = Blueprint("auth", __name__)


def _serialize_user(user):
    if not user:
        return None
    for field in ("skills", "interests"):
        user[field] = parse_json_field(user.get(field))
    user.pop("password", None)
    return user


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    required = ["name", "email", "password"]
    if not all(data.get(f) for f in required):
        return jsonify({"error": "Name, email, and password are required"}), 400

    existing = execute_query("SELECT id FROM users WHERE email = %s", (data["email"],), fetch_one=True)
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    skills = json.dumps(data.get("skills", []))
    interests = json.dumps(data.get("interests", []))

    user_id = execute_query(
        """INSERT INTO users (name, email, password, college, branch, year, skills, interests, bio, github, linkedin, portfolio)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            data["name"], data["email"], hash_password(data["password"]),
            data.get("college"), data.get("branch"), data.get("year"),
            skills, interests, data.get("bio"),
            data.get("github"), data.get("linkedin"), data.get("portfolio"),
        ),
        commit=True,
    )
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True)
    return jsonify({"message": "Registration successful", "user": _serialize_user(user)}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    user = execute_query("SELECT * FROM users WHERE email = %s", (data["email"],), fetch_one=True)
    if not user or not verify_password(data["password"], user["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({"message": "Login successful", "user": _serialize_user(user)})


@auth_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(_serialize_user(user))


@auth_bp.route("/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    data = request.json or {}
    fields = []
    values = []
    allowed = ["name", "college", "branch", "year", "bio", "experience", "github", "linkedin",
               "portfolio", "availability", "preferred_role"]
    for field in allowed:
        if field in data:
            fields.append(f"{field} = %s")
            values.append(data[field])
    if "skills" in data:
        fields.append("skills = %s")
        values.append(json.dumps(data["skills"]))
    if "interests" in data:
        fields.append("interests = %s")
        values.append(json.dumps(data["interests"]))

    if not fields:
        return jsonify({"error": "No fields to update"}), 400

    values.append(user_id)
    execute_query(f"UPDATE users SET {', '.join(fields)} WHERE id = %s", tuple(values), commit=True)
    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True)
    return jsonify({"message": "Profile updated", "user": _serialize_user(user)})


@auth_bp.route("/users", methods=["GET"])
def list_users():
    domain = request.args.get("domain")
    skill = request.args.get("skill")
    users = execute_query("SELECT id, name, email, college, branch, year, skills, interests, experience, availability, preferred_role, contributions, team_rating FROM users WHERE is_admin = 0", fetch=True)
    results = []
    for u in users:
        u["skills"] = parse_json_field(u.get("skills"))
        u["interests"] = parse_json_field(u.get("interests"))
        if skill and not any(skill.lower() in s.lower() for s in u["skills"]):
            continue
        if domain and not any(domain.lower() in i.lower() for i in u["interests"]):
            continue
        results.append(u)
    return jsonify(results)
