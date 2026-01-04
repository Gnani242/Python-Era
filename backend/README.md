# Python Era Backend

FastAPI backend for Python Era learning platform.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (create `.env` file):
```
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./pythonera.db
FRONTEND_URL=http://localhost:3000
```

3. Run the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Deployment on Render

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Add environment variables:
   - `SECRET_KEY`
   - `DATABASE_URL` (for PostgreSQL)
   - `FRONTEND_URL` (your Vercel URL)

## API Documentation

Visit `/docs` for interactive API documentation.

