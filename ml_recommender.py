import pandas as pd
from sqlalchemy.orm import Session
from models import QuizResponse, AdaptiveLearningPath, Lesson

class EdTechAIEngine:
    def __init__(self, db: Session):
        self.db = db

    def fetch_student_quiz_features(self, student_id: str) -> pd.DataFrame:
        query = self.db.query(QuizResponse).filter(QuizResponse.student_id == student_id)
        df = pd.read_sql(query.statement, self.db.bind)
        if df.empty:
            return pd.DataFrame()

        topic_summary = df.groupby('topic_tag').agg(
            total_questions=('is_correct', 'count'),
            correct_answers=('is_correct', 'sum')
        ).reset_index()

        topic_summary['accuracy_rate'] = topic_summary['correct_answers'] / topic_summary['total_questions']
        return topic_summary

    def evaluate_and_generate_recommendations(self, student_id: str):
        topic_df = self.fetch_student_quiz_features(student_id)
        if topic_df.empty:
            return

        # Purono recommendation gulo prothome delete korbe jeno dynamic topic overwrite hoy
        self.db.query(AdaptiveLearningPath).filter(
            AdaptiveLearningPath.student_id == student_id
        ).delete()
        self.db.commit()

        # Mark 50%-er kom hole durbol topic dhorbe
        weak_topics = topic_df[topic_df['accuracy_rate'] < 0.50]

        for _, row in weak_topics.iterrows():
            weak_tag = row['topic_tag'].strip().lower()
            accuracy = row['accuracy_rate']
            confidence = round(1.0 - accuracy, 2)

            # Match or auto-create dynamic Lesson for the typed topic
            lesson_title = f"Masterclass on {weak_tag.upper()}"
            recommended_lesson = self.db.query(Lesson).filter(
                Lesson.title.ilike(f"%{weak_tag}%")
            ).first()

            if not recommended_lesson:
                recommended_lesson = Lesson(
                    title=lesson_title,
                    content_url=f"https://www.youtube.com/results?search_query={weak_tag}+programming+tutorial"
                )
                self.db.add(recommended_lesson)
                self.db.commit()
                self.db.refresh(recommended_lesson)

            new_recommendation = AdaptiveLearningPath(
                student_id=student_id,
                recommended_lesson_id=recommended_lesson.id,
                weak_topic_tag=weak_tag,
                confidence_score=confidence,
                status="pending"
            )
            self.db.add(new_recommendation)

        self.db.commit()
        print(f"[AI ENGINE] Generated dynamic recommendation for weak topics of Student: {student_id}")