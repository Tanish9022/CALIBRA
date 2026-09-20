# CALIBRA — Deployment & Containerization

CALIBRA is architected to run either locally (for zero-dependency development/demonstration) or in production via Docker containers.

## 1. Quick Local Start

### Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py --force
python -m uvicorn main:app --reload --port 8000
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```
Navigate to `http://localhost:5174/`.

---

## 2. Docker Deployment

CALIBRA includes `docker-compose.yml` defining the FastAPI backend and Vite/Nginx frontend services:

```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
