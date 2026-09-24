🎓 Smart AI EdTech Portal & Virtual Tutor

An adaptive Learning Management System (LMS) powered by AI that identifies student weaknesses through quiz performance and automatically recommends tailored video lessons in Bangla 🇧🇩, English 🇬🇧, and Hindi 🇮🇳. It also features a floating AI Tutor for instant learning assistance and Chart.js analytics for teachers.
🌟 Key Features
👨‍🏫 Teacher Management Portal
Single & Bulk Entry:** Upload quiz marks individually or via bulk CSV files (`student_id, subject, topic, score`).
  Visual Performance Analytics:** Real-time pass/fail ratio charts and subject-wise weakness trends via Chart.js.
  Dynamic Subject Setup:** Easily add and manage new subject courses.

👨‍🎓 Student AI Learning Dashboard
Targeted Recommendations:** Automatic weak-topic detection paired with curated multilingual video classes.
  Clear Quiz Summary:** Direct evaluation showing scored marks, subjects, and pass/weak performance status.
  🤖 Floating AI Virtual Tutor:** Integrated popup chatbot providing instant explanations for topics like Velocity, Speed, Integration, Arrays, and SQL.
  🌗 Theme Switcher:** Smooth light and dark mode toggling.

🛠️ Tech Stack

Backend: FastAPI (Python), SQLAlchemy, Pandas, Uvicorn
Frontend: HTML5, CSS3, Vanilla JavaScript, Chart.js
Database: SQLite / PostgreSQL
Authentication:** Role-Based Access Control (Teacher & Student)

 📁 Repository Structure
├── api.py
├── database.py
├── models.py
├── ml_recommender.py
├── index.html
├── requirements.txt
└── README.md
