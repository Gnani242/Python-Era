# Python Era 🐍

A beginner-friendly full-stack web application for daily Python learning with streak tracking, code execution, and progress monitoring.

## 🏗️ Architecture

- **Frontend**: Next.js 14 (App Router) + Tailwind CSS - Deployed on Vercel
- **Backend**: FastAPI + SQLite/PostgreSQL - Deployed on Render
- **Code Editor**: Monaco Editor (VS Code editor in the browser)
- **Authentication**: JWT tokens
- **Database**: SQLite (dev) / PostgreSQL (production)

## ✨ Features

### Learning System
- **Daily Lessons**: Each user gets one lesson per day based on their start date
- **Day Calculation**: `current_day = today - start_date + 1`
- **Streak Tracking**: Tracks consecutive days of completion (resets on missed days)
- **Code Execution**: Safe Python code execution via backend API
- **Time Tracking**: Tracks study time and practice time per day

### User Features
- User registration and authentication
- Daily coding practice questions
- Real-time code execution with output/error display
- Progress dashboard with streak, current day, and time spent
- Mark tasks as complete to update streak

### Admin Features
- Role-based access control
- Create, edit, and delete daily lessons
- Manage coding questions and solutions
- Full lesson content management

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL (for production) or SQLite (for development)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file:
```
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./pythonera.db
FRONTEND_URL=http://localhost:3000
```

Run the backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env.local` file:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the frontend:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 📦 Deployment

### Backend on Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
   - **Environment**: Python 3
4. Add environment variables:
   - `SECRET_KEY`: A secure random string
   - `DATABASE_URL`: PostgreSQL connection string (provided by Render)
   - `FRONTEND_URL`: Your Vercel frontend URL
5. Deploy!

### Frontend on Vercel

1. Connect your GitHub repository to Vercel
2. Set root directory to `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL
4. Deploy automatically on push to main branch

## 📁 Project Structure

```
python-era/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── README.md           # Backend documentation
├── frontend/
│   ├── app/                # Next.js App Router pages
│   │   ├── page.tsx        # Home/redirect page
│   │   ├── login/          # Login/Register page
│   │   ├── dashboard/      # User dashboard
│   │   ├── learn/          # Daily learning page
│   │   └── admin/          # Admin panel
│   ├── lib/
│   │   └── api.ts          # API client functions
│   ├── package.json        # Node dependencies
│   └── README.md          # Frontend documentation
└── README.md              # This file
```

## 🔐 Security Features

- JWT-based authentication
- Password hashing (SHA256)
- Safe code execution (restricted imports)
- CORS protection
- Environment variables for secrets
- Role-based access control

## 🎯 Key Concepts

### Start Date Logic
- When a user registers/logs in for the first time, `start_date` is set to today
- This becomes Day 1 for that user
- Each day, `current_day = (today - start_date).days + 1`

### Streak Logic
- Streak increases only when a task is completed
- Consecutive days: streak +1
- Missing a day: streak resets to 1
- Each user has their own streak based on their start date

### Code Execution
- Code is executed on the backend (not in the browser)
- Restricted imports (os, sys, subprocess, etc.)
- Output and errors are returned to the frontend
- Safe execution environment

## 🛠️ Development

### Adding an Admin User

You can create an admin user by modifying the database directly or adding a script. For quick setup, you can run:

```python
# In Python shell or script
from backend.main import SessionLocal, User, hash_password
db = SessionLocal()
admin = User(
    username="admin",
    email="admin@example.com",
    hashed_password=hash_password("admin123"),
    is_admin=True
)
db.add(admin)
db.commit()
```

### Database Schema

- **users**: User accounts with start_date and admin flag
- **daily_lessons**: Lesson content for each day
- **user_progress**: User completion status and time tracking
- **user_streaks**: Streak tracking per user

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

Built with ❤️ for Python learners

