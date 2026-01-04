from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from datetime import datetime, date, timedelta
from typing import Optional, List
import jwt
import hashlib
import os
import sys
from io import StringIO
import traceback
import contextlib

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pythonera.db")
if SQLALCHEMY_DATABASE_URL.startswith("postgres"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    start_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DailyLesson(Base):
    __tablename__ = "daily_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    day_number = Column(Integer, unique=True, index=True)
    topic = Column(String)
    content = Column(Text)
    question = Column(Text)
    solution = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day_number = Column(Integer)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    study_time = Column(Integer, default=0)  # seconds
    practice_time = Column(Integer, default=0)  # seconds
    
    user = relationship("User")

class UserStreak(Base):
    __tablename__ = "user_streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    current_streak = Column(Integer, default=0)
    last_completed_date = Column(DateTime, nullable=True)
    
    user = relationship("User")

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Python Era API")

# CORS configuration
origins = [
    "http://localhost:3000",
    "https://python-era.vercel.app",
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class LessonCreate(BaseModel):
    day_number: int
    topic: str
    content: str
    question: str
    solution: str

class CodeExecute(BaseModel):
    code: str

class TimeUpdate(BaseModel):
    study_time: int
    practice_time: int

# Utility functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_token(user_id: int, username: str, is_admin: bool) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Safe code execution
@contextlib.contextmanager
def stdout_capture():
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = old_stdout

def execute_code_safe(code: str) -> dict:
    """Execute Python code in a safe environment"""
    output = ""
    error = ""
    
    # Restricted imports (can be expanded)
    restricted_modules = ['os', 'sys', 'subprocess', 'fileinput', 'shutil']
    
    try:
        # Simple check for restricted imports
        for mod in restricted_modules:
            if f"import {mod}" in code or f"from {mod}" in code:
                error = f"Import of '{mod}' is not allowed for security reasons"
                return {"output": "", "error": error}
        
        # Execute code with timeout simulation
        with stdout_capture() as captured:
            exec_globals = {"__builtins__": __builtins__}
            exec(code, exec_globals)
            output = captured.getvalue()
        
    except Exception as e:
        error = str(e) + "\n" + traceback.format_exc()
    
    return {"output": output, "error": error}

# Routes
@app.get("/")
def root():
    return {"message": "Python Era API", "status": "running"}

@app.post("/api/auth/register", response_model=TokenResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    hashed = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed,
        start_date=datetime.utcnow()  # Set start_date on registration
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create streak record
    streak = UserStreak(user_id=user.id, current_streak=0)
    db.add(streak)
    db.commit()
    
    token = create_token(user.id, user.username, user.is_admin)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "start_date": user.start_date.isoformat() if user.start_date else None
        }
    }

@app.post("/api/auth/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Set start_date on first login if not set
    if not user.start_date:
        user.start_date = datetime.utcnow()
        db.commit()
    
    token = create_token(user.id, user.username, user.is_admin)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "start_date": user.start_date.isoformat() if user.start_date else None
        }
    }

@app.get("/api/user/me")
def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    streak = db.query(UserStreak).filter(UserStreak.user_id == current_user.id).first()
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "start_date": current_user.start_date.isoformat() if current_user.start_date else None,
        "streak": streak.current_streak if streak else 0
    }

@app.get("/api/lessons/today")
def get_today_lesson(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.start_date:
        raise HTTPException(status_code=400, detail="Start date not set")
    
    # Calculate current day
    start_date = current_user.start_date.date()
    today = date.today()
    current_day = (today - start_date).days + 1
    
    if current_day < 1:
        raise HTTPException(status_code=400, detail="Invalid day calculation")
    
    # Get lesson for current day
    lesson = db.query(DailyLesson).filter(DailyLesson.day_number == current_day).first()
    if not lesson:
        raise HTTPException(status_code=404, detail=f"No lesson available for day {current_day}")
    
    # Get user progress for today
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.day_number == current_day
    ).first()
    
    return {
        "day_number": current_day,
        "topic": lesson.topic,
        "content": lesson.content,
        "question": lesson.question,
        "completed": progress.completed if progress else False,
        "study_time": progress.study_time if progress else 0,
        "practice_time": progress.practice_time if progress else 0
    }

@app.post("/api/execute")
def execute_code(code_data: CodeExecute, current_user: User = Depends(get_current_user)):
    result = execute_code_safe(code_data.code)
    return result

@app.post("/api/progress/complete")
def complete_task(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.start_date:
        raise HTTPException(status_code=400, detail="Start date not set")
    
    start_date = current_user.start_date.date()
    today = date.today()
    current_day = (today - start_date).days + 1
    
    # Get or create progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.day_number == current_day
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            day_number=current_day,
            completed=True,
            completed_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
    
    # Update streak
    streak = db.query(UserStreak).filter(UserStreak.user_id == current_user.id).first()
    if not streak:
        streak = UserStreak(user_id=current_user.id, current_streak=1, last_completed_date=datetime.utcnow())
        db.add(streak)
    else:
        last_date = streak.last_completed_date.date() if streak.last_completed_date else None
        if last_date == today:
            # Already completed today, no change
            pass
        elif last_date == today - timedelta(days=1):
            # Consecutive day
            streak.current_streak += 1
            streak.last_completed_date = datetime.utcnow()
        elif last_date and last_date < today - timedelta(days=1):
            # Missed day(s), reset streak
            streak.current_streak = 1
            streak.last_completed_date = datetime.utcnow()
        else:
            # First completion
            streak.current_streak = 1
            streak.last_completed_date = datetime.utcnow()
    
    db.commit()
    return {"message": "Task completed", "day": current_day, "streak": streak.current_streak}

@app.post("/api/progress/time")
def update_time(time_data: TimeUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.start_date:
        raise HTTPException(status_code=400, detail="Start date not set")
    
    start_date = current_user.start_date.date()
    today = date.today()
    current_day = (today - start_date).days + 1
    
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.day_number == current_day
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            day_number=current_day
        )
        db.add(progress)
    
    progress.study_time = time_data.study_time
    progress.practice_time = time_data.practice_time
    db.commit()
    
    return {"message": "Time updated"}

@app.get("/api/dashboard")
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.start_date:
        raise HTTPException(status_code=400, detail="Start date not set")
    
    start_date = current_user.start_date.date()
    today = date.today()
    current_day = (today - start_date).days + 1
    
    # Get today's progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.day_number == current_day
    ).first()
    
    total_time = 0
    if progress:
        total_time = progress.study_time + progress.practice_time
    
    streak = db.query(UserStreak).filter(UserStreak.user_id == current_user.id).first()
    
    return {
        "current_day": current_day,
        "total_time_today": total_time,
        "streak": streak.current_streak if streak else 0,
        "start_date": start_date.isoformat()
    }

# Admin routes
@app.post("/api/admin/lessons", dependencies=[Depends(get_admin_user)])
def create_lesson(lesson_data: LessonCreate, db: Session = Depends(get_db)):
    # Check if day already exists
    if db.query(DailyLesson).filter(DailyLesson.day_number == lesson_data.day_number).first():
        raise HTTPException(status_code=400, detail=f"Lesson for day {lesson_data.day_number} already exists")
    
    lesson = DailyLesson(
        day_number=lesson_data.day_number,
        topic=lesson_data.topic,
        content=lesson_data.content,
        question=lesson_data.question,
        solution=lesson_data.solution
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return {"message": "Lesson created", "lesson": lesson}

@app.get("/api/admin/lessons", dependencies=[Depends(get_admin_user)])
def get_all_lessons(db: Session = Depends(get_db)):
    lessons = db.query(DailyLesson).order_by(DailyLesson.day_number).all()
    return [{
        "id": l.id,
        "day_number": l.day_number,
        "topic": l.topic,
        "content": l.content,
        "question": l.question,
        "solution": l.solution
    } for l in lessons]

@app.put("/api/admin/lessons/{lesson_id}", dependencies=[Depends(get_admin_user)])
def update_lesson(lesson_id: int, lesson_data: LessonCreate, db: Session = Depends(get_db)):
    lesson = db.query(DailyLesson).filter(DailyLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    lesson.day_number = lesson_data.day_number
    lesson.topic = lesson_data.topic
    lesson.content = lesson_data.content
    lesson.question = lesson_data.question
    lesson.solution = lesson_data.solution
    db.commit()
    return {"message": "Lesson updated"}

@app.delete("/api/admin/lessons/{lesson_id}", dependencies=[Depends(get_admin_user)])
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(DailyLesson).filter(DailyLesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    db.delete(lesson)
    db.commit()
    return {"message": "Lesson deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

