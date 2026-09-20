from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CALIBRA Metrology Compliance API",
    description="Explainable, Context-Aware OIML R76 Compliance Engine for Non-Automatic Weighing Instruments (NAWI)",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "ok",
        "service": "CALIBRA Metrology Compliance Engine",
        "standard": "OIML R76-1:2006 & OIML R76-2:2006",
        "precision": "Arbitrary Precision Python Decimal (34 digits)",
        "gravity_engine": "Somigliana (WGS84) + Free-Air Elevation Correction"
    }

@app.get("/audit")
def get_audit_trail(limit: int = 50, db: Session = Depends(get_db)):
    """
    Returns chronological immutable audit events.
    """
    return db.query(models.AuditEvent).order_by(models.AuditEvent.timestamp.desc()).limit(limit).all()

@app.get("/rulesets")
def get_rulesets(db: Session = Depends(get_db)):
    """
    Returns versioned rulesets and MPE boundaries.
    """
    return db.query(models.RuleSet).all()

# Register Routers
from routers import instruments, compliance, reports, sessions, context, equipment, replay, demo
app.include_router(instruments.router)
app.include_router(compliance.router)
app.include_router(reports.router)
app.include_router(sessions.router)
app.include_router(context.router)
app.include_router(equipment.router)
app.include_router(replay.router)
app.include_router(demo.router)
