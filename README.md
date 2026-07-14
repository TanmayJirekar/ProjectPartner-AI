# 🤝 ProjectPartner-AI

> An AI-powered collaboration platform that helps students and developers discover compatible teammates for hackathons, academic projects, startups, and open-source contributions using intelligent matching algorithms.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Backend-green)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange)
![AI](https://img.shields.io/badge/AI-Powered-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

# 📖 Overview

ProjectPartner-AI is an AI-driven teammate recommendation platform that eliminates the challenge of finding the right collaborators. Instead of randomly joining teams, users create skill-based profiles, and the AI intelligently matches them with compatible teammates based on technical expertise, interests, availability, project goals, and personality traits.

Whether you're participating in a hackathon, building a startup, contributing to open source, or working on a college project, ProjectPartner-AI helps you build stronger and more productive teams.

---

# ✨ Features

## 🤖 AI-Powered Partner Matching
- Intelligent teammate recommendations
- Skill compatibility analysis
- Interest-based matching
- Personality compatibility scoring
- AI-generated compatibility reports

## 👤 Smart User Profiles
- Technical skills
- Experience level
- Preferred technologies
- Portfolio links
- GitHub & LinkedIn integration
- Availability status

## 🔍 Advanced Search
- Search by skills
- Search by technology stack
- Domain-based filtering
- Location filtering
- Experience filtering

## 💬 Team Collaboration
- Send collaboration requests
- Accept or reject invitations
- Team management dashboard
- Collaboration history

## 📊 AI Skill Analysis
- Analyze user profiles
- Recommend missing skills
- Project suitability prediction
- Team balance analysis

## 📈 Dashboard & Analytics
- Profile completion score
- Match percentage
- Active collaborations
- Pending requests
- Recommended teammates

---

# 🛠 Tech Stack

## Backend
- Python
- Flask
- SQLAlchemy
- Flask-JWT-Extended
- REST APIs

## AI
- Groq API
- Large Language Models (LLMs)
- Recommendation Engine
- Compatibility Analysis

## Frontend
- HTML
- CSS
- JavaScript
- Bootstrap

## Database
- MySQL

---

# 📂 Project Structure

```
ProjectPartner-AI/
│
├── app.py
├── models/
├── routes/
├── services/
├── templates/
├── static/
├── uploads/
├── config.py
├── requirements.txt
└── README.md
```

---

# 🚀 Installation

## 1. Clone Repository

```bash
git clone https://github.com/TanmayJirekar/ProjectPartner-AI.git

cd ProjectPartner-AI
```

## 2. Create Virtual Environment

```bash
python -m venv venv
```

### Activate

Windows

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file

```env
DATABASE_URL=mysql+mysqlconnector://username:password@localhost:3306/projectpartner

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=1440

GROQ_API_KEY=your_groq_api_key
```

---

## 5. Create Database

```sql
CREATE DATABASE projectpartner;
```

---

## 6. Run Application

```bash
python app.py
```

---

# 🧠 How It Works

1. Register and create your profile.
2. Add your technical skills, interests, and preferred technologies.
3. AI analyzes your profile.
4. The recommendation engine calculates compatibility scores.
5. Receive personalized teammate suggestions.
6. Send collaboration requests.
7. Form teams and start building amazing projects.

---

# 📸 Screenshots

Include screenshots for:

- Home Page
- Login & Registration
- User Dashboard
- AI Match Recommendations
- Profile Page
- Collaboration Requests
- Team Dashboard

---

# 🚀 Future Enhancements

- 💬 Real-time Chat
- 📹 Video Meeting Integration
- 🌍 Global Developer Community
- 📍 Nearby Teammate Discovery
- 🎯 AI Project Recommendations
- 📂 GitHub Repository Integration
- 📅 Team Scheduling Assistant
- 📈 Skill Growth Analytics
- 🤖 AI Resume Analysis
- 🏆 Hackathon Recommendation Engine

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository

```bash
git checkout -b feature-name
```

2. Commit your changes

```bash
git commit -m "Added new feature"
```

3. Push to GitHub

```bash
git push origin feature-name
```

4. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Tanmay Jirekar**

GitHub: https://github.com/TanmayJirekar

---

# 🌟 Why ProjectPartner-AI?

- 🤖 AI-based teammate matching
- 🚀 Improves hackathon and project success
- 👥 Finds compatible collaborators in seconds
- 📊 Data-driven compatibility scoring
- 💡 Encourages productive teamwork
- 🌍 Supports students, developers, freelancers, and startup founders

---

## ⭐ Support

If you found this project useful, don't forget to leave a ⭐ on GitHub!

**Build better teams. Build better projects. Build together with AI.**
