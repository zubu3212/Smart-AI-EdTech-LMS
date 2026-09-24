import uuid
from database import engine, Base, SessionLocal
from models import User, Lesson, QuizResponse
from ml_recommender import EdTechAIEngine

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # টেস্ট ডাটা তৈরি
        student_id = uuid.uuid4()
        student = User(id=student_id, full_name="Test Student", email=f"test_{student_id}@test.com")
        lesson = Lesson(title="Python Loops Masterclass", content_url="https://s3.aws.com/loops.mp4")
        db.add_all([student, lesson])
        db.commit()

        # ডামি কুইজ উত্তর (Loops-এ স্টুডেন্ট দুর্বল)
        responses = [
            QuizResponse(student_id=student_id, attempt_id=uuid.uuid4(), question_id=uuid.uuid4(), topic_tag="loops", is_correct=False, time_taken_seconds=40),
            QuizResponse(student_id=student_id, attempt_id=uuid.uuid4(), question_id=uuid.uuid4(), topic_tag="loops", is_correct=False, time_taken_seconds=30),
            QuizResponse(student_id=student_id, attempt_id=uuid.uuid4(), question_id=uuid.uuid4(), topic_tag="sql", is_correct=True, time_taken_seconds=20),
        ]
        db.add_all(responses)
        db.commit()

        # AI ইঞ্জিন এনালিটিক্স সম্পন্ন করবে
        ai_engine = EdTechAIEngine(db)
        ai_engine.evaluate_and_generate_recommendations(str(student_id))

    finally:
        db.close()

if __name__ == "__main__":
    main()