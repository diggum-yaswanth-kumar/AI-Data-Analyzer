# Data Insight AI

Data Insight AI is a production-style full-stack AI analytics dashboard built with Next.js, FastAPI, Pandas, and the free-tier Google Gemini API. It lets users upload CSV or Excel files, preview data, generate charts automatically, ask natural language questions, receive AI-generated insights, and export polished PDF reports.

## Features

- Upload CSV and Excel datasets
- Instant dataset preview table
- Auto-generated bar, line, pie, and histogram charts
- AI insights using Google Gemini free tier
- Natural language chat with your data
- Business suggestions and anomaly detection
- PDF report export
- SaaS-style dark dashboard UI

## Local setup

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```
