from flask import Blueprint, request, jsonify
from backend.utils.db import execute_query

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/project/<int:project_id>", methods=["GET"])
def list_tasks(project_id):
    tasks = execute_query(
        "SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assigned_to = u.id WHERE t.project_id = %s ORDER BY t.created_at DESC",
        (project_id,), fetch=True,
    )
    return jsonify(tasks)


@tasks_bp.route("/", methods=["POST"])
def create_task():
    data = request.json or {}
    if not data.get("project_id") or not data.get("title"):
        return jsonify({"error": "project_id and title required"}), 400

    task_id = execute_query(
        """INSERT INTO tasks (project_id, title, description, assigned_to, status, priority, parent_task_id, deadline, created_by)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            data["project_id"], data["title"], data.get("description"),
            data.get("assigned_to"), data.get("status", "To Do"),
            data.get("priority", "Medium"), data.get("parent_task_id"),
            data.get("deadline"), data.get("created_by"),
        ),
        commit=True,
    )
    _update_completion(data["project_id"])
    task = execute_query("SELECT * FROM tasks WHERE id = %s", (task_id,), fetch_one=True)
    return jsonify({"task": task}), 201


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json or {}
    allowed = {"title", "description", "assigned_to", "status", "priority", "deadline"}
    fields, values = [], []
    for field in allowed:
        if field in data:
            fields.append(f"{field} = %s")
            values.append(data[field])

    if not fields:
        return jsonify({"error": "No fields to update"}), 400

    values.append(task_id)
    execute_query(f"UPDATE tasks SET {', '.join(fields)} WHERE id = %s", tuple(values), commit=True)
    task = execute_query("SELECT * FROM tasks WHERE id = %s", (task_id,), fetch_one=True)
    if task:
        _update_completion(task["project_id"])
    return jsonify({"task": task})


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = execute_query("SELECT project_id FROM tasks WHERE id = %s", (task_id,), fetch_one=True)
    execute_query("DELETE FROM tasks WHERE id = %s", (task_id,), commit=True)
    if task:
        _update_completion(task["project_id"])
    return jsonify({"message": "Task deleted"})


def _update_completion(project_id):
    tasks = execute_query("SELECT status FROM tasks WHERE project_id = %s", (project_id,), fetch=True)
    if not tasks:
        return
    done = sum(1 for t in tasks if t["status"] == "Done")
    percent = int(done / len(tasks) * 100)
    execute_query("UPDATE projects SET completion_percent = %s WHERE id = %s", (percent, project_id), commit=True)
