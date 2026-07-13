"""AI Model 5: Success Prediction Model."""

from backend.ai.team_compatibility import predict_compatibility
from backend.utils.db import parse_json_field


def _risk_label(probability):
    if probability >= 75:
        return "Low"
    if probability >= 50:
        return "Medium"
    return "High"


def predict_success(project, team_members, tasks=None):
    tasks = tasks or []
    team_size = project.get("team_size", 4)
    current_team = len(team_members)
    team_fill_ratio = min(1.0, current_team / max(team_size, 1))

    completed_tasks = sum(1 for t in tasks if t.get("status") == "Done")
    task_ratio = completed_tasks / max(len(tasks), 1) if tasks else 0.3

    difficulty_penalty = {"Easy": 0, "Medium": 10, "Hard": 20, "Expert": 30}.get(
        project.get("difficulty", "Medium"), 10
    )

    compatibility_result = predict_compatibility(team_members) if len(team_members) >= 2 else {"compatibility": 60}
    compat_score = compatibility_result["compatibility"]

    skill_coverage = 0
    if team_members:
        all_skills = set()
        required = parse_json_field(project.get("required_skills"))
        for m in team_members:
            all_skills.update(s.lower() for s in parse_json_field(m.get("skills")))
        skill_coverage = len(all_skills & set(s.lower() for s in required)) / max(len(required), 1) * 100

    success_probability = int(min(100, max(0,
        team_fill_ratio * 25 +
        task_ratio * 20 +
        compat_score * 0.25 +
        skill_coverage * 0.2 -
        difficulty_penalty
    )))

    risk_factors = []
    if team_fill_ratio < 0.5:
        risk_factors.append("Team understaffed")
    if skill_coverage < 50:
        risk_factors.append("Skill gaps in team")
    if compat_score < 60:
        risk_factors.append("Low team compatibility")
    if difficulty_penalty >= 20:
        risk_factors.append("High project difficulty")

    return {
        "success_probability": success_probability,
        "risk": _risk_label(success_probability),
        "risk_factors": risk_factors,
        "metrics": {
            "team_fill": round(team_fill_ratio * 100, 1),
            "task_progress": round(task_ratio * 100, 1),
            "compatibility": compat_score,
            "skill_coverage": round(skill_coverage, 1),
        },
    }
