import uuid
from database import engine, Base, SessionLocal
from models import User, Subject, QuizResponse
from ml_recommender import EdTechAIEngine


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        student = db.query(User).filter(User.custom_id == "demo-student-001").first()
        if not student:
            student = User(
                custom_id="demo-student-001",
                full_name="Demo Student",
                email="demo.student@edtech.test",
                password_hash="demo123",
                role="student",
            )
            db.add(student)
            db.commit()
            db.refresh(student)

        subject = db.query(Subject).filter(Subject.name.ilike("Physics")).first()
        if not subject:
            subject = Subject(name="Physics")
            db.add(subject)
            db.commit()

        existing = db.query(QuizResponse).filter(QuizResponse.student_id == student.id).count()
        if existing == 0:
            demo_responses = [
                QuizResponse(
                    student_id=student.id,
                    subject_name="Physics",
                    topic_tag="velocity",
                    obtained_score=5.5,
                    is_correct=False,
                ),
                QuizResponse(
                    student_id=student.id,
                    subject_name="Physics",
                    topic_tag="velocity",
                    obtained_score=6.0,
                    is_correct=False,
                ),
                QuizResponse(
                    student_id=student.id,
                    subject_name="Physics",
                    topic_tag="speed",
                    obtained_score=8.5,
                    is_correct=True,
                ),
            ]
            db.add_all(demo_responses)
            db.commit()

        ai_engine = EdTechAIEngine(db)
        ai_engine.evaluate_and_generate_recommendations(str(student.id))
        print("Seed data created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
