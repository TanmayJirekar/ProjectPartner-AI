"""Seed sample data for ProjectPartner AI."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from backend.utils.db import execute_query
from backend.utils.auth import hash_password


def seed():
    users = [
        ("Tanmay Jirekar", "tanmay@example.com", "Python, Flask, Machine Learning", "AI, Web Development"),
        ("Priya Sharma", "priya@example.com", "React, JavaScript, UI/UX, Figma", "Web Development, Design"),
        ("Arjun Patel", "arjun@example.com", "Java, Spring Boot, MySQL, Docker", "Backend, DevOps"),
        ("Sneha Reddy", "sneha@example.com", "TensorFlow, Python, Deep Learning, NLP", "AI/ML, Research"),
    ]

    for name, email, skills_str, interests_str in users:
        existing = execute_query("SELECT id FROM users WHERE email = %s", (email,), fetch_one=True)
        if existing:
            continue
        execute_query(
            "INSERT INTO users (name, email, password, college, branch, year, skills, interests) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (name, email, hash_password("demo123"), "Tech University", "CS", 3,
             json.dumps([s.strip() for s in skills_str.split(",")]),
             json.dumps([i.strip() for i in interests_str.split(",")])),
            commit=True,
        )

    owner = execute_query("SELECT id FROM users WHERE email = %s", ("tanmay@example.com",), fetch_one=True)
    if owner:
        existing_proj = execute_query("SELECT id FROM projects WHERE title = %s", ("AI Resume Analyzer",), fetch_one=True)
        if not existing_proj:
            pid = execute_query(
                """INSERT INTO projects (owner_id, title, description, problem_statement, required_skills,
                   team_size, domain, difficulty, duration, technology_stack, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (owner["id"], "AI Resume Analyzer",
                 "Build an AI-powered resume analysis tool that extracts skills and matches candidates to jobs.",
                 "Students struggle to identify skill gaps in their resumes.",
                 json.dumps(["Python", "Machine Learning", "NLP", "Flask"]),
                 4, "AI/ML", "Medium", "3 months",
                 json.dumps(["Python", "Flask", "scikit-learn", "Groq API"]), "Open"),
                commit=True,
            )
            execute_query("INSERT INTO teams (project_id, user_id, role) VALUES (%s, %s, %s)",
                          (pid, owner["id"], "Project Owner"), commit=True)

            execute_query(
                """INSERT INTO projects (owner_id, title, description, problem_statement, required_skills,
                   team_size, domain, difficulty, duration, technology_stack, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (owner["id"], "Smart Campus IoT Platform",
                 "IoT-based smart campus monitoring system with real-time dashboards.",
                 "Campus facilities lack real-time monitoring and automation.",
                 json.dumps(["IoT", "Python", "React", "MQTT"]),
                 5, "IoT", "Hard", "4 months",
                 json.dumps(["Arduino", "React", "Node.js", "MongoDB"]), "Open"),
                commit=True,
            )

    execute_query(
        "INSERT INTO hackathons (name, description, domain, max_team_size) VALUES (%s, %s, %s, %s)",
        ("AI Innovation Hackathon 2026", "48-hour hackathon focused on AI solutions for education.", "AI/ML", 4),
        commit=True,
    )

    print("Sample data seeded successfully!")


if __name__ == "__main__":
    seed()
