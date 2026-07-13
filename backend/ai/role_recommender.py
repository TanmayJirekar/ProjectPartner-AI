"""AI Model 4: Role Recommendation Engine."""

ROLE_SKILL_MAP = {
    "Backend Developer": ["python", "java", "flask", "django", "node", "sql", "mysql", "api", "rest"],
    "Frontend Developer": ["javascript", "react", "html", "css", "vue", "angular", "typescript"],
    "UI/UX Designer": ["figma", "ui", "ux", "design", "wireframe", "prototype", "adobe"],
    "ML Engineer": ["machine learning", "tensorflow", "pytorch", "scikit-learn", "deep learning", "nlp"],
    "Research Analyst": ["research", "analysis", "data analysis", "statistics", "paper", "literature"],
    "Project Manager": ["leadership", "management", "agile", "scrum", "communication", "planning"],
    "QA Tester": ["testing", "selenium", "qa", "automation", "junit", "quality assurance"],
    "DevOps Engineer": ["docker", "kubernetes", "aws", "ci/cd", "jenkins", "devops", "linux"],
}


def recommend_role(skills, experience="", interests=None):
    interests = interests or []
    skills_lower = [s.lower().strip() for s in skills]
    exp_lower = experience.lower()
    interests_lower = [i.lower() for i in interests]

    scores = {}
    for role, role_skills in ROLE_SKILL_MAP.items():
        skill_matches = sum(1 for rs in role_skills if any(rs in s for s in skills_lower))
        exp_matches = sum(1 for rs in role_skills if rs in exp_lower)
        interest_matches = sum(1 for rs in role_skills if any(rs in i for i in interests_lower))
        scores[role] = skill_matches * 3 + exp_matches * 2 + interest_matches * 2

    sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_role = sorted_roles[0][0] if sorted_roles and sorted_roles[0][1] > 0 else "Full Stack Developer"
    confidence = min(100, sorted_roles[0][1] * 10) if sorted_roles else 50

    return {
        "recommended_role": top_role,
        "confidence": confidence,
        "all_roles": [{"role": r, "score": s} for r, s in sorted_roles[:5]],
    }
