import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from backend.utils.db import execute_query
from backend.config import UPLOAD_FOLDER

messages_bp = Blueprint("messages", __name__)
notifications_bp = Blueprint("notifications", __name__)


@messages_bp.route("/", methods=["POST"])
def send_message():
    data = request.json or {}
    if not data.get("sender_id") or not data.get("content"):
        return jsonify({"error": "sender_id and content required"}), 400

    msg_id = execute_query(
        "INSERT INTO messages (sender_id, receiver_id, project_id, content, file_path) VALUES (%s, %s, %s, %s, %s)",
        (data["sender_id"], data.get("receiver_id"), data.get("project_id"), data["content"], data.get("file_path")),
        commit=True,
    )

    recipient = data.get("receiver_id")
    if recipient:
        execute_query(
            "INSERT INTO notifications (user_id, title, message, type) VALUES (%s, %s, %s, %s)",
            (recipient, "New Message", data["content"][:100], "message"), commit=True,
        )
    return jsonify({"message": "Sent", "id": msg_id}), 201


@messages_bp.route("/user/<int:user_id>", methods=["GET"])
def user_messages(user_id):
    project_id = request.args.get("project_id")
    if project_id:
        msgs = execute_query(
            """SELECT m.*, u.name as sender_name FROM messages m
               JOIN users u ON m.sender_id = u.id
               WHERE m.project_id = %s ORDER BY m.created_at ASC""",
            (project_id,), fetch=True,
        )
    else:
        msgs = execute_query(
            """SELECT m.*, u.name as sender_name FROM messages m
               JOIN users u ON m.sender_id = u.id
               WHERE m.sender_id = %s OR m.receiver_id = %s ORDER BY m.created_at DESC LIMIT 50""",
            (user_id, user_id), fetch=True,
        )
    return jsonify(msgs)


@messages_bp.route("/upload", methods=["POST"])
def upload_chat_file():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files["file"]
    filename = secure_filename(f"chat_{file.filename}")
    file.save(str(UPLOAD_FOLDER / filename))
    return jsonify({"filename": filename})


@notifications_bp.route("/user/<int:user_id>", methods=["GET"])
def get_notifications(user_id):
    notifs = execute_query(
        "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 30",
        (user_id,), fetch=True,
    )
    return jsonify(notifs)


@notifications_bp.route("/<int:notif_id>/read", methods=["PUT"])
def mark_read(notif_id):
    execute_query("UPDATE notifications SET is_read = 1 WHERE id = %s", (notif_id,), commit=True)
    return jsonify({"message": "Marked as read"})
