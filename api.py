from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import User, Subject, Lesson, QuizResponse, AdaptiveLearningPath
from ml_recommender import EdTechAIEngine
from pydantic import BaseModel, Field
import pandas as pd
import io
import urllib.parse
import uuid

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubjectCreateRequest(BaseModel):
    subject_name: str

class SignUpRequest(BaseModel):
    full_name: str
    custom_id: str
    email: str
    password: str
    role: str

class SignInRequest(BaseModel):
    email_or_id: str
    password: str

class ResetPasswordRequest(BaseModel):
    email_or_id: str
    new_password: str

class TeacherQuizEntry(BaseModel):
    student_custom_id: str
    subject_name: str
    topic_tag: str
    obtained_score: float = Field(..., ge=0, le=15)

class ChatbotQueryRequest(BaseModel):
    message: str

def generate_multilingual_classes(topic_tag: str, subject_name: str):
    clean_topic = topic_tag.strip()
    clean_subject = subject_name.strip() if subject_name else ""
    full_query = f"{clean_subject} {clean_topic}".strip()

    verified_multilingual = {
        "velocity": [
            {"title": f"🇧🇩 Bangla: {clean_topic.upper()} - এইচএসসি ফিজিক্স ক্লাস", "channel": "10 Minute School", "embed_id": "5yfh5aQ3VWA", "query": "velocity physics 10 minute school bangla"},
            {"title": f"🇬🇧 English: {clean_topic.upper()} vs Speed Fundamentals", "channel": "Khan Academy", "embed_id": "rAof9Ld5sOg", "query": "velocity physics khan academy"},
            {"title": f"🇮🇳 Hindi: {clean_topic.upper()} Concept & Numericals", "channel": "Physics Wallah", "embed_id": "WUvTyaaNkzM", "query": "velocity physics wallah hindi"}
        ],
        "speed": [
            {"title": f"🇧🇩 Bangla: {clean_topic.upper()} - দ্রুতি ও বেগ ব্যাখ্যা", "channel": "OnnoRokom Pathshala", "embed_id": "5yfh5aQ3VWA", "query": "speed physics onnorokom pathshala bangla"},
            {"title": f"🇬🇧 English: {clean_topic.upper()} & Motion Masterclass", "channel": "The Organic Chemistry Tutor", "embed_id": "rAof9Ld5sOg", "query": "speed physics organic chemistry tutor"},
            {"title": f"🇮🇳 Hindi: {clean_topic.upper()} in One Shot Physics", "channel": "Physics Wallah", "embed_id": "WUvTyaaNkzM", "query": "speed physics wallah hindi"}
        ],
        "integration": [
            {"title": f"🇧🇩 Bangla: {clean_topic.upper()} - যোগজীকরণ শর্টকাট ও বেসিক", "channel": "10 Minute School", "embed_id": "f32SChP4G10", "query": "integration 10 minute school bangla"},
            {"title": f"🇬🇧 English: {clean_topic.upper()} - Complete Calculus Rules", "channel": "Khan Academy", "embed_id": "N2dp1O_z1sA", "query": "integration calculus khan academy"},
            {"title": f"🇮🇳 Hindi: {clean_topic.upper()} - Basic to Advance Calculus", "channel": "Unacademy JEE", "embed_id": "WsQQvHm4lSw", "query": "integration unacademy hindi"}
        ],
        "array": [
            {"title": f"🇧🇩 Bangla: {clean_topic.upper()} - ডাটা স্ট্রাকচার অ্যারেকে সহজ ভাষায়", "channel": "Tamim Shahriar Subeen / 10MS", "embed_id": "14dsk8Y__Yw", "query": "array data structure bangla tutorial"},
            {"title": f"🇬🇧 English: {clean_topic.upper()} - Data Structures & Memory", "channel": "freeCodeCamp.org", "embed_id": "p9I2323D1aU", "query": "array data structure freecodecamp"},
            {"title": f"🇮🇳 Hindi: {clean_topic.upper()} in C/C++ Data Structures", "channel": "CodeWithHarry", "embed_id": "Db9ZYbJONNc", "query": "array codewithharry hindi"}
        ]
    }

    lower_topic = clean_topic.lower()
    for key in verified_multilingual:
        if key in lower_topic or lower_topic in key:
            classes = []
            for item in verified_multilingual[key]:
                classes.append({
                    "title": item["title"],
                    "channel": item["channel"],
                    "embed_url": f"https://www.youtube.com/embed/{item['embed_id']}",
                    "watch_url": f"https://www.youtube.com/results?search_query={urllib.parse.quote(item['query'])}",
                    "thumbnail": f"https://img.youtube.com/vi/{item['embed_id']}/hqdefault.jpg"
                })
            return classes

    q_bangla = urllib.parse.quote(f"{full_query} bangla tutorial lesson")
    q_english = urllib.parse.quote(f"{full_query} english tutorial course")
    q_hindi = urllib.parse.quote(f"{full_query} hindi explanation lecture")

    return [
        {
            "title": f"🇧🇩 Bangla Class: {clean_topic.upper()} সম্পূর্ণ বাংলা টিউটোরিয়াল",
            "channel": "Top Bangla EdTech Channel",
            "embed_url": "https://www.youtube.com/embed/5yfh5aQ3VWA",
            "watch_url": f"https://www.youtube.com/results?search_query={q_bangla}",
            "thumbnail": "https://img.youtube.com/vi/5yfh5aQ3VWA/hqdefault.jpg"
        },
        {
            "title": f"🇬🇧 English Class: {clean_topic.upper()} Full Concept & Practice",
            "channel": "Global English Academy",
            "embed_url": "https://www.youtube.com/embed/rAof9Ld5sOg",
            "watch_url": f"https://www.youtube.com/results?search_query={q_english}",
            "thumbnail": "https://img.youtube.com/vi/rAof9Ld5sOg/hqdefault.jpg"
        },
        {
            "title": f"🇮🇳 Hindi Class: {clean_topic.upper()} In Depth Explanation",
            "channel": "Popular Hindi E-Learning",
            "embed_url": "https://www.youtube.com/embed/WUvTyaaNkzM",
            "watch_url": f"https://www.youtube.com/results?search_query={q_hindi}",
            "thumbnail": "https://img.youtube.com/vi/WUvTyaaNkzM/hqdefault.jpg"
        }
    ]

# --- AI STUDY CHATBOT API ---
@app.post("/api/ai/chatbot")
def ai_study_tutor(data: ChatbotQueryRequest):
    query = data.message.lower().strip()
    
    knowledge_base = {
        "velocity": "🔹 **Velocity (বেগ):** সময়ের সাথে সরণের পরিবর্তনের হারকে বেগ বলে। এটি একটি ভেক্টর রাশি (মান ও দিক দুটিই আছে)।\n📐 **সূত্র:** v = s / t\n💡 **উদাহরণ:** একটি গাড়ি উত্তর দিকে ৬০ কিমি/ঘণ্টা বেগে চলছে।",
        "speed": "🔹 **Speed (দ্রুতি):** সময়ের সাথে অতিক্রান্ত দূরত্বের পরিবর্তনের হারকে দ্রুতি বলে। এটি স্কেলার রাশি।\n📐 **সূত্র:** Speed = Distance / Time",
        "integration": "🔹 **Integration (যোগজীকরণ):** ক্যালকুলাসের একটি শাখা যা ক্ষুদ্র ক্ষুদ্র অংশ যুক্ত করে মোট ক্ষেত্রফল নির্ণয় করে।\n📐 **গাণিতিক রূপ:** ∫ x^n dx = (x^(n+1))/(n+1) + C",
        "array": "🔹 **Array (অ্যারে):** প্রোগ্রামিংয়ে সমজাতীয় একাধিক ডেটা একটিমাত্র ভ্যারিয়েবল নামের অধীনে ইনডেক্স ব্যবহার করে সাজিয়ে রাখার পদ্ধতি।\n💻 **উদাহরণ:** int scores[5] = {10, 20, 30, 40, 50};",
        "sql": "🔹 **SQL:** ডাটাবেজ থেকে তথ্য খোঁজা এবং পরিচালনার জন্য ব্যবহৃত হয়।\n💻 **কোয়েরি উদাহরণ:** SELECT * FROM students WHERE score < 7.5;"
    }

    for key, response in knowledge_base.items():
        if key in query:
            return {"reply": response}

    return {"reply": f"🤖 **AI Tutor:** '{data.message}' বিষয়টি বেশ আকর্ষণীয়! এই বিষয়ে আরও বিস্তারিত জানতে আপনার ড্যাশবোর্ডের রেকমেন্ডেড ভিডিও ক্লাসগুলো দেখতে পারেন। সুনির্দিষ্ট প্রশ্ন করতে লিখুন: Velocity, Integration, Array, SQL বা Speed।"}

# --- Subject APIs ---
@app.post("/api/subjects")
def create_subject(data: SubjectCreateRequest, db: Session = Depends(get_db)):
    clean_name = data.subject_name.strip()
    existing = db.query(Subject).filter(Subject.name.ilike(clean_name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Subject already exists!")

    new_sub = Subject(name=clean_name)
    db.add(new_sub)
    db.commit()
    return {"message": f"Subject '{clean_name}' successfully created!"}

@app.get("/api/subjects")
def get_subjects(db: Session = Depends(get_db)):
    subjects = db.query(Subject).all()
    return [{"id": str(s.id), "name": s.name} for s in subjects]

# --- Auth APIs ---
@app.post("/api/auth/signup")
def signup(data: SignUpRequest, db: Session = Depends(get_db)):
    clean_id = data.custom_id.strip()
    clean_email = data.email.strip().lower()

    if db.query(User).filter(User.email == clean_email).first():
        raise HTTPException(status_code=400, detail="Email already registered!")
    if db.query(User).filter(User.custom_id == clean_id).first():
        raise HTTPException(status_code=400, detail="ID already registered!")

    new_user = User(
        full_name=data.full_name,
        custom_id=clean_id,
        email=clean_email,
        password_hash=data.password,
        role=data.role.lower()
    )
    db.add(new_user)
    db.commit()
    return {"message": f"Account created for ID: {clean_id}!"}

@app.post("/api/auth/signin")
def signin(data: SignInRequest, db: Session = Depends(get_db)):
    identifier = data.email_or_id.strip()
    user = db.query(User).filter(
        ((User.email == identifier.lower()) | (User.custom_id == identifier)),
        User.password_hash == data.password
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials!")
    
    return {
        "message": "Login successful!",
        "user": {
            "id": str(user.id),
            "custom_id": user.custom_id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }

@app.post("/api/auth/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    identifier = data.email_or_id.strip()
    new_pass = data.new_password.strip()

    if not identifier or not new_pass:
        raise HTTPException(status_code=400, detail="দয়া করে আইডি/ইমেইল এবং নতুন পাসওয়ার্ড প্রদান করুন!")

    user = db.query(User).filter(
        (User.email == identifier.lower()) | (User.custom_id == identifier)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="এই আইডি বা ইমেইল দিয়ে কোনো অ্যাকাউন্ট পাওয়া যায়নি!")

    user.password_hash = new_pass
    db.commit()
    return {"message": "পাসওয়ার্ড সফলভাবে পরিবর্তন করা হয়েছে! নতুন পাসওয়ার্ড দিয়ে লগইন করুন।"}

# --- Single Teacher Quiz Entry API ---
@app.post("/api/teacher/submit-quiz")
def submit_quiz_score(data: TeacherQuizEntry, db: Session = Depends(get_db)):
    clean_id = data.student_custom_id.strip()
    clean_topic = data.topic_tag.lower().strip()
    clean_subject = data.subject_name.strip() if data.subject_name else "General Subject"
    
    student = db.query(User).filter(User.custom_id == clean_id).first()
    if not student:
        student = User(
            custom_id=clean_id,
            full_name=f"Student ({clean_id})",
            email=f"student_{clean_id}@edtech.com",
            password_hash="123456",
            role="student"
        )
        db.add(student)
        db.commit()
        db.refresh(student)

    db.query(QuizResponse).filter(QuizResponse.student_id == student.id).delete()
    db.query(AdaptiveLearningPath).filter(AdaptiveLearningPath.student_id == student.id).delete()
    db.commit()

    is_pass = data.obtained_score >= 7.5

    quiz_entry = QuizResponse(
        student_id=student.id,
        subject_name=clean_subject,
        topic_tag=clean_topic,
        obtained_score=data.obtained_score,
        is_correct=is_pass
    )
    db.add(quiz_entry)
    db.commit()

    ai_engine = EdTechAIEngine(db)
    ai_engine.evaluate_and_generate_recommendations(str(student.id))

    return {"message": f"Score {data.obtained_score}/15 for '{clean_topic.upper()}' saved & AI updated!"}

# --- Bulk CSV Upload API ---
@app.post("/api/teacher/upload-bulk-quiz")
async def upload_bulk_quiz(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only .csv files are supported!")

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

    required_columns = ['student_id', 'subject', 'topic', 'score']
    for col in required_columns:
        if col not in df.columns:
            raise HTTPException(status_code=400, detail=f"CSV file must contain column: '{col}'")

    success_count = 0
    ai_engine = EdTechAIEngine(db)

    for _, row in df.iterrows():
        clean_id = str(row['student_id']).strip()
        clean_subject = str(row['subject']).strip()
        clean_topic = str(row['topic']).strip().lower()
        score = float(row['score'])

        student = db.query(User).filter(User.custom_id == clean_id).first()
        if not student:
            student = User(
                custom_id=clean_id,
                full_name=f"Student ({clean_id})",
                email=f"student_{clean_id}@edtech.com",
                password_hash="123456",
                role="student"
            )
            db.add(student)
            db.commit()
            db.refresh(student)

        db.query(QuizResponse).filter(QuizResponse.student_id == student.id).delete()
        db.query(AdaptiveLearningPath).filter(AdaptiveLearningPath.student_id == student.id).delete()
        db.commit()

        is_pass = score >= 7.5

        quiz_entry = QuizResponse(
            student_id=student.id,
            subject_name=clean_subject,
            topic_tag=clean_topic,
            obtained_score=score,
            is_correct=is_pass
        )
        db.add(quiz_entry)
        db.commit()

        ai_engine.evaluate_and_generate_recommendations(str(student.id))
        success_count += 1

    return {"message": f"Successfully processed {success_count} student scores from CSV and updated AI recommendations!"}

# --- Student Dashboard API ---
@app.get("/api/dashboard/custom/{student_custom_id}")
def get_dashboard_by_custom_id(student_custom_id: str, db: Session = Depends(get_db)):
    clean_id = student_custom_id.strip()
    student = db.query(User).filter(User.custom_id == clean_id).first()
    
    if not student:
        return {"student_name": f"Student ({clean_id})", "quiz_info": None, "recommendations": []}

    quiz_resp = db.query(QuizResponse).filter(
        QuizResponse.student_id == student.id
    ).order_by(QuizResponse.created_at.desc()).first()

    rec = db.query(AdaptiveLearningPath).filter(
        AdaptiveLearningPath.student_id == student.id
    ).order_by(AdaptiveLearningPath.generated_at.desc()).first()

    quiz_info = None
    if quiz_resp:
        quiz_info = {
            "subject_name": quiz_resp.subject_name,
            "topic_tag": quiz_resp.topic_tag.upper(),
            "obtained_score": quiz_resp.obtained_score,
            "status": "PASS" if quiz_resp.is_correct else "NEEDS REVISION (WEAK)"
        }

    result = []
    if rec:
        topic = rec.weak_topic_tag.lower().strip()
        subject = quiz_resp.subject_name if quiz_resp else ""
        videos = generate_multilingual_classes(topic, subject)

        result.append({
            "id": str(rec.id),
            "weak_topic": rec.weak_topic_tag,
            "confidence_score": rec.confidence_score,
            "recommended_videos": videos,
            "status": rec.status
        })

    return {
        "student_name": student.full_name,
        "student_id": student.custom_id,
        "quiz_info": quiz_info,
        "recommendations": result
    }

# --- Teacher Analytics Summary API ---
@app.get("/api/analytics/teacher-summary")
def get_teacher_analytics(db: Session = Depends(get_db)):
    all_quizzes = db.query(QuizResponse).all()
    if not all_quizzes:
        return {
            "total_students": 0,
            "avg_score": 0,
            "pass_count": 0,
            "fail_count": 0,
            "subject_weakness": {}
        }

    total_students = len(set([q.student_id for q in all_quizzes]))
    scores = [q.obtained_score for q in all_quizzes]
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0
    
    pass_count = sum(1 for q in all_quizzes if q.obtained_score >= 7.5)
    fail_count = len(all_quizzes) - pass_count

    subject_weakness = {}
    for q in all_quizzes:
        if q.obtained_score < 7.5:
            subj = q.subject_name
            subject_weakness[subj] = subject_weakness.get(subj, 0) + 1

    return {
        "total_students": total_students,
        "avg_score": avg_score,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "subject_weakness": subject_weakness
    }

# --- Student Quiz History Analytics API ---
@app.get("/api/analytics/student-history/{student_custom_id}")
def get_student_history(student_custom_id: str, db: Session = Depends(get_db)):
    clean_id = student_custom_id.strip()
    student = db.query(User).filter(User.custom_id == clean_id).first()
    if not student:
        return {"history": []}

    quizzes = db.query(QuizResponse).filter(
        QuizResponse.student_id == student.id
    ).order_by(QuizResponse.created_at.asc()).all()

    history = []
    for q in quizzes:
        history.append({
            "topic": q.topic_tag.upper(),
            "subject": q.subject_name,
            "score": q.obtained_score,
            "date": q.created_at.strftime("%b %d") if q.created_at else "Quiz"
        })

    return {"history": history}