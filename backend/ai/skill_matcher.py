"""AI Model 1: Skill Matching Engine using TF-IDF and Cosine Similarity."""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILL_WEIGHTS = {
    "python": 1.2, "machine learning": 1.3, "tensorflow": 1.3, "flask": 1.1,
    "react": 1.1, "javascript": 1.0, "java": 1.0, "sql": 1.0, "mysql": 1.0,
    "docker": 1.2, "kubernetes": 1.3, "aws": 1.2, "devops": 1.2,
}


def _normalize_skills(skills):
    return [s.strip().lower() for s in skills if s and str(s).strip()]


def _recommendation_label(score):
    if score >= 80:
        return "Highly Suitable"
    if score >= 60:
        return "Suitable"
    if score >= 40:
        return "Moderately Suitable"
    return "Not Suitable"


def match_skills(student_skills, project_skills):
    student_skills = _normalize_skills(student_skills)
    project_skills = _normalize_skills(project_skills)

    if not student_skills or not project_skills:
        return {"match_score": 0, "recommendation": "Not Suitable", "skill_gap": project_skills}

    student_text = " ".join(student_skills)
    project_text = " ".join(project_skills)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([student_text, project_text])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    matched = set(student_skills) & set(project_skills)
    gap = list(set(project_skills) - set(student_skills))

    weight_bonus = sum(SKILL_WEIGHTS.get(s, 1.0) for s in matched) / max(len(project_skills), 1)
    overlap_ratio = len(matched) / max(len(project_skills), 1)

    score = int(min(100, (cosine_sim * 50 + overlap_ratio * 40 + weight_bonus * 10)))
    return {
        "match_score": score,
        "recommendation": _recommendation_label(score),
        "matched_skills": list(matched),
        "skill_gap": gap,
    }
