from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CALIBRA API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "CALIBRA API"}

from routers import instruments, compliance, reports, sessions
app.include_router(instruments.router)
app.include_router(compliance.router)
app.include_router(reports.router)
app.include_router(sessions.router)

