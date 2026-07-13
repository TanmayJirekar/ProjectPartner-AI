"""AI Model 3: Hybrid Project Recommendation System."""

from backend.ai.skill_matcher import match_skills
from backend.utils.db import parse_json_field


def _content_score(user, project):
    user_skills = parse_json_field(user.get("skills"))
    user_interests = parse_json_field(user.get("interests"))
    project_skills = parse_json_field(project.get("required_skills"))
    project_domain = (project.get("domain") or "").lower()

    skill_result = match_skills(user_skills, project_skills)
    interest_match = sum(
        1 for i in user_interests if i.lower() in project_domain or i.lower() in (project.get("title") or "").lower()
    )
    interest_score = min(100, interest_match * 25)
    domain_match = 100 if any(i.lower() == project_domain for i in user_interests) else 30

    return skill_result["match_score"] * 0.5 + interest_score * 0.3 + domain_match * 0.2


def _collaborative_score(user_id, project, all_applications):
    similar_users = set()
    user_projects = {a["project_id"] for a in all_applications if a["user_id"] == user_id}
    for app in all_applications:
        if app["user_id"] != user_id:
            other_projects = {a["project_id"] for a in all_applications if a["user_id"] == app["user_id"]}
            if user_projects & other_projects:
                similar_users.add(app["user_id"])

    if not similar_users:
        return 50

    similar_applied = sum(1 for a in all_applications if a["user_id"] in similar_users and a["project_id"] == project["id"])
    return min(100, 40 + similar_applied * 15)


def recommend_projects(user, projects, all_applications=None):
    all_applications = all_applications or []
    recommendations = []

    for project in projects:
        if project.get("owner_id") == user.get("id"):
            continue
        content = _content_score(user, project)
        collab = _collaborative_score(user.get("id"), project, all_applications)
        hybrid_score = int(content * 0.7 + collab * 0.3)

        skill_result = match_skills(
            parse_json_field(user.get("skills")),
            parse_json_field(project.get("required_skills")),
        )

        recommendations.append({
            "project_id": project["id"],
            "title": project["title"],
            "domain": project.get("domain"),
            "match_score": hybrid_score,
            "skill_gap": skill_result.get("skill_gap", []),
            "recommendation": skill_result.get("recommendation"),
        })

    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations[:10]
