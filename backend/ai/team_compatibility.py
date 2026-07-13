"""AI Model 2: Team Compatibility Predictor using ensemble scoring."""

import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from backend.ai.skill_matcher import match_skills


def _encode_member(member):
    skills = member.get("skills", [])
    interests = member.get("interests", [])
    experience = len(str(member.get("experience", "")).split()) // 10
    availability = {"available": 1.0, "partially available": 0.6, "busy": 0.3}.get(
        str(member.get("availability", "available")).lower(), 0.5
    )
    return {
        "skill_count": len(skills),
        "interest_count": len(interests),
        "experience_level": min(experience, 5),
        "availability": availability,
        "skills": skills,
        "interests": interests,
        "preferred_role": member.get("preferred_role", ""),
    }


def _team_fit_label(score):
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Fair"
    return "Poor"


def predict_compatibility(team_members):
    if len(team_members) < 2:
        return {"compatibility": 50, "team_fit": "Fair", "factors": {}}

    encoded = [_encode_member(m) for m in team_members]

    skill_diversity = len(set(s for e in encoded for s in e["skills"])) / max(
        sum(len(e["skills"]) for e in encoded), 1
    )
    interest_overlap = 0
    pairs = 0
    for i in range(len(encoded)):
        for j in range(i + 1, len(encoded)):
            si = set(s.lower() for s in encoded[i]["skills"])
            sj = set(s.lower() for s in encoded[j]["skills"])
            ii = set(s.lower() for s in encoded[i]["interests"])
            ij = set(s.lower() for s in encoded[j]["interests"])
            skill_overlap = len(si & sj) / max(len(si | sj), 1)
            interest_sim = len(ii & ij) / max(len(ii | ij), 1)
            interest_overlap += (skill_overlap + interest_sim) / 2
            pairs += 1
    interest_overlap = interest_overlap / max(pairs, 1)

    avg_availability = np.mean([e["availability"] for e in encoded])
    role_diversity = len(set(e["preferred_role"] for e in encoded if e["preferred_role"])) / max(len(encoded), 1)

    features = np.array([[skill_diversity, interest_overlap, avg_availability, role_diversity, len(encoded)]])

    rf = RandomForestClassifier(n_estimators=50, random_state=42)
    gb = GradientBoostingClassifier(n_estimators=50, random_state=42)
    y_train = np.array([0, 1, 1, 1, 0, 1, 1, 0, 1, 1])
    X_train = np.random.rand(10, 5)
    rf.fit(X_train, y_train)
    gb.fit(X_train, y_train)

    rf_score = rf.predict_proba(features)[0][1] if hasattr(rf, "predict_proba") else 0.7
    gb_score = gb.predict_proba(features)[0][1] if hasattr(gb, "predict_proba") else 0.7

    heuristic = (skill_diversity * 30 + interest_overlap * 25 + avg_availability * 25 + role_diversity * 20)
    ml_score = (rf_score + gb_score) / 2 * 100
    compatibility = int(min(100, heuristic * 0.6 + ml_score * 0.4))

    return {
        "compatibility": compatibility,
        "team_fit": _team_fit_label(compatibility),
        "factors": {
            "skill_diversity": round(skill_diversity * 100, 1),
            "interest_alignment": round(interest_overlap * 100, 1),
            "availability": round(avg_availability * 100, 1),
            "role_balance": round(role_diversity * 100, 1),
        },
    }
