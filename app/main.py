from datetime import datetime, timezone
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Float, DateTime, Text, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aura.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Opportunity(Base):
    __tablename__ = "opportunities"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    channel: Mapped[str] = mapped_column(String(80))
    rationale: Mapped[str] = mapped_column(Text)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0)
    estimated_revenue: Mapped[float] = mapped_column(Float, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")
    status: Mapped[str] = mapped_column(String(30), default="proposed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(primary_key=True)
    action_type: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    amount: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class LedgerEntry(Base):
    __tablename__ = "ledger"
    id: Mapped[int] = mapped_column(primary_key=True)
    entry_type: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(80))
    amount: Mapped[float] = mapped_column(Float)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)
app = FastAPI(title="AURA — Autonomous Unified Revenue Agent", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OpportunityIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    channel: str = Field(min_length=2, max_length=80)
    rationale: str = Field(min_length=3)
    estimated_cost: float = Field(default=0, ge=0)
    estimated_revenue: float = Field(default=0, ge=0)
    risk_level: str = Field(default="medium", pattern="^(low|medium|high)$")


class ApprovalIn(BaseModel):
    action_type: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=3)
    amount: float = Field(default=0, ge=0)


class LedgerIn(BaseModel):
    entry_type: str
    category: str = Field(min_length=2, max_length=80)
    amount: float = Field(gt=0)
    note: str = ""


@app.get("/")
def root():
    return {
        "name": "AURA",
        "status": "online",
        "version": "0.1.0",
        "message": "Core API is running. Platform integrations are not connected.",
    }


@app.get("/health")
def health():
    return {"ok": True, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/config")
def config():
    return {
        "mode": "full_opportunity_discovery",
        "budget": "flexible_with_explicit_spend_approval",
        "assets": ["youtube", "tiktok", "google", "website", "instagram", "marketplace_affiliate"],
        "autonomy": "guarded",
        "goal": "diversified_revenue",
        "live_integrations": [],
        "production_ready": False,
    }


@app.post("/opportunities")
def create_opportunity(payload: OpportunityIn):
    with SessionLocal() as db:
        item = Opportunity(**payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return {"id": item.id, "status": item.status}


@app.get("/opportunities")
def list_opportunities():
    with SessionLocal() as db:
        items = db.scalars(select(Opportunity).order_by(Opportunity.created_at.desc())).all()
        return [{
            "id": x.id, "title": x.title, "channel": x.channel, "rationale": x.rationale,
            "estimated_cost": x.estimated_cost, "estimated_revenue": x.estimated_revenue,
            "risk_level": x.risk_level, "status": x.status,
        } for x in items]


@app.post("/approvals")
def create_approval(payload: ApprovalIn):
    with SessionLocal() as db:
        item = Approval(**payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return {"id": item.id, "status": item.status}


@app.get("/approvals")
def list_approvals():
    with SessionLocal() as db:
        items = db.scalars(select(Approval).order_by(Approval.created_at.desc())).all()
        return [{
            "id": x.id, "action_type": x.action_type, "description": x.description,
            "amount": x.amount, "status": x.status,
        } for x in items]


@app.post("/approvals/{approval_id}/decision")
def decide_approval(approval_id: int, decision: str):
    if decision not in {"approved", "rejected"}:
        raise HTTPException(400, "decision must be approved or rejected")
    with SessionLocal() as db:
        item = db.get(Approval, approval_id)
        if not item:
            raise HTTPException(404, "approval not found")
        if item.status != "pending":
            raise HTTPException(409, "approval already decided")
        item.status = decision
        db.commit()
        return {"id": item.id, "status": item.status}


@app.post("/ledger")
def add_ledger_entry(payload: LedgerIn):
    if payload.entry_type not in {"income", "expense"}:
        raise HTTPException(400, "entry_type must be income or expense")
    with SessionLocal() as db:
        item = LedgerEntry(**payload.model_dump())
        db.add(item)
        db.commit()
        db.refresh(item)
        return {"id": item.id}


@app.get("/ledger/summary")
def ledger_summary():
    with SessionLocal() as db:
        rows = db.scalars(select(LedgerEntry)).all()
        income = sum(x.amount for x in rows if x.entry_type == "income")
        expense = sum(x.amount for x in rows if x.entry_type == "expense")
        return {"income": income, "expense": expense, "net": income - expense, "entries": len(rows)}


@app.get("/ledger")
def ledger_entries():
    with SessionLocal() as db:
        rows = db.scalars(select(LedgerEntry).order_by(LedgerEntry.created_at.desc())).all()
        return [{
            "id": x.id, "entry_type": x.entry_type, "category": x.category,
            "amount": x.amount, "note": x.note,
        } for x in rows]
