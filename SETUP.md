# Python Era - Setup Guide

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file in `backend/`:
```
SECRET_KEY=your-secret-key-here-make-it-random-and-secure
DATABASE_URL=sqlite:///./pythonera.db
FRONTEND_URL=http://localhost:3000
```

Run backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 2. Create Admin User

```bash
cd backend
python create_admin.py
```

Follow the prompts to create your first admin user.

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create `.env.local` file in `frontend/`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run frontend:
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

### 4. First Steps

1. Login as admin (created in step 2)
2. Go to Admin Panel
3. Create your first lesson (Day 1)
4. Logout and create a regular user account
5. Start learning!

## Deployment

### Backend (Render)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repo
4. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port 10000`
   - Environment: Python 3
5. Environment Variables:
   - `SECRET_KEY`: Random secure string
   - `DATABASE_URL`: PostgreSQL (provided by Render)
   - `FRONTEND_URL`: Your Vercel URL

### Frontend (Vercel)

1. Push code to GitHub
2. Import project on Vercel
3. Root directory: `frontend`
4. Environment Variable:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL
5. Deploy!

## Notes

- Users' `start_date` is set on first login/registration
- Each day is calculated as: `today - start_date + 1`
- Streaks reset if a day is missed
- Code execution happens on backend (safe)
- Timer tracks study and practice time separately

