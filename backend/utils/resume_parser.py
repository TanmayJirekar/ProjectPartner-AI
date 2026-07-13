"""Resume PDF skill extraction."""

import re

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

SKILL_KEYWORDS = [
    "Python", "Java", "JavaScript", "TypeScript", "React", "Node.js", "Flask", "Django",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "SQL", "MySQL", "MongoDB",
    "Docker", "Kubernetes", "AWS", "Azure", "Git", "HTML", "CSS", "Vue", "Angular",
    "C++", "C#", "Go", "Rust", "Scala", "R", "Pandas", "NumPy", "Scikit-learn",
    "DevOps", "CI/CD", "Jenkins", "Linux", "Figma", "UI/UX", "Agile", "Scrum",
    "REST API", "GraphQL", "Microservices", "Redis", "Elasticsearch", "Spark",
]


def extract_text_from_pdf(file_path):
    if PyPDF2 is None:
        return ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = " ".join(page.extract_text() or "" for page in reader.pages)
        return text
    except Exception:
        return ""


def extract_skills_from_resume(file_path):
    text = extract_text_from_pdf(file_path)
    if not text:
        return {"skills": [], "experience": "", "technologies": []}

    text_lower = text.lower()
    found_skills = [skill for skill in SKILL_KEYWORDS if skill.lower() in text_lower]

    exp_match = re.search(r"(experience|work history)(.{0,2000})", text_lower, re.DOTALL)
    experience = exp_match.group(2).strip()[:500] if exp_match else text[:500]

    return {
        "skills": list(set(found_skills)),
        "experience": experience,
        "technologies": found_skills[:10],
    }
