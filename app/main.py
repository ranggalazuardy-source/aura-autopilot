from datetime import datetime, timezone
import hmac
import os
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, select, update, String, Float, DateTime, Text
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


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100))
    object_id: Mapped[str] = mapped_column(String(80))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)
API_KEY_HEADER = APIKeyHeader(name="X-AURA-API-Key", auto_error=False)
app = FastAPI(title="AURA — Local Development API", version="0.2.0")
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-AURA-API-Key"],
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Cache-Control", "no-store")
    return response


async def require_api_key(x_aura_api_key: str | None = Depends(API_KEY_HEADER)):
    expected = os.getenv("AURA_API_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="AURA_API_KEY is not configured")
    if not x_aura_api_key or not hmac.compare_digest(x_aura_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid API key")


def record_audit(db, event_type: str, object_id: int | str, details: str = ""):
    db.add(AuditLog(
        event_type=event_type,
        object_id=str(object_id),
        details=details[:1000],
    ))


@app.get("/")
def root():
    return {
        "name": "AURA",
        "status": "online",
        "version": "0.2.0",
        "message": "Local development API is running; integrations and agent execution are disabled.",
    }


@app.get("/health")
def health():
    return {"ok": True, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/config")
def config():
    return {
        "mode": "local_development",
        "budget": "zero_capital_with_explicit_spend_approval",
        "autonomy": "guarded",
        "live_integrations": [],
        "production_ready": False,
    }


class OpportunityIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    channel: str = Field(min_length=2, max_length=80)
    rationale: str = Field(min_length=3, max_length=3000)
    estimated_cost: float = Field(default=0, ge=0, allow_inf_nan=False)
    estimated_revenue: float = Field(default=0, ge=0, allow_inf_nan=False)
    risk_level: str = Field(default="medium", pattern="^(low|medium|high)$")


class ApprovalIn(BaseModel):
    action_type: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=3, max_length=3000)
    amount: float = Field(default=0, ge=0, allow_inf_nan=False)


class LedgerIn(BaseModel):
    entry_type: str = Field(pattern="^(income|expense)$")
    category: str = Field(min_length=2, max_length=80)
    amount: float = Field(gt=0, allow_inf_nan=False)
    note: str = Field(default="", max_length=1000)


@app.post("/opportunities", dependencies=[Depends(require_api_key)])
def create_opportunity(payload: OpportunityIn):
    with SessionLocal() as db:
        item = Opportunity(**payload.model_dump())
        db.add(item)
        db.flush()
        record_audit(db, "opportunity.created", item.id, item.title)
        db.commit()
        return {"id": item.id, "status": item.status}


@app.get("/opportunities", dependencies=[Depends(require_api_key)])
def list_opportunities():
    with SessionLocal() as db:
        items = db.scalars(select(Opportunity).order_by(Opportunity.created_at.desc()).limit(200)).all()
        return [{
            "id": x.id, "title": x.title, "channel": x.channel, "rationale": x.rationale,
            "estimated_cost": x.estimated_cost, "estimated_revenue": x.estimated_revenue,
            "risk_level": x.risk_level, "status": x.status,
        } for x in items]


@app.post("/opportunities/{opportunity_id}/status", dependencies=[Depends(require_api_key)])
def update_opportunity_status(opportunity_id: int, status: str):
    allowed = {"proposed", "reviewing", "shortlisted", "rejected", "archived"}
    if status not in allowed:
        raise HTTPException(400, "invalid opportunity status")
    with SessionLocal() as db:
        item = db.get(Opportunity, opportunity_id)
        if item is None:
            raise HTTPException(404, "opportunity not found")
        item.status = status
        record_audit(db, "opportunity.status_changed", item.id, status)
        db.commit()
        return {"id": item.id, "status": item.status}


@app.post("/approvals", dependencies=[Depends(require_api_key)])
def create_approval(payload: ApprovalIn):
    with SessionLocal() as db:
        item = Approval(**payload.model_dump())
        db.add(item)
        db.flush()
        record_audit(db, "approval.requested", item.id, item.action_type)
        db.commit()
        return {"id": item.id, "status": item.status}


@app.get("/approvals", dependencies=[Depends(require_api_key)])
def list_approvals():
    with SessionLocal() as db:
        items = db.scalars(select(Approval).order_by(Approval.created_at.desc()).limit(200)).all()
        return [{
            "id": x.id, "action_type": x.action_type, "description": x.description,
            "amount": x.amount, "status": x.status,
        } for x in items]


@app.post("/approvals/{approval_id}/decision", dependencies=[Depends(require_api_key)])
def decide_approval(approval_id: int, decision: str):
    if decision not in {"approved", "rejected"}:
        raise HTTPException(400, "decision must be approved or rejected")
    with SessionLocal() as db:
        changed = db.execute(
            update(Approval)
            .where(Approval.id == approval_id, Approval.status == "pending")
            .values(status=decision)
        )
        if changed.rowcount != 1:
            if db.get(Approval, approval_id) is None:
                raise HTTPException(404, "approval not found")
            raise HTTPException(409, "approval already decided")
        record_audit(db, "approval." + decision, approval_id)
        db.commit()
        return {"id": approval_id, "status": decision, "execution": "not_executed"}


@app.post("/ledger", dependencies=[Depends(require_api_key)])
def add_ledger_entry(payload: LedgerIn):
    with SessionLocal() as db:
        item = LedgerEntry(**payload.model_dump())
        db.add(item)
        db.flush()
        record_audit(db, "ledger." + item.entry_type, item.id, item.category)
        db.commit()
        return {"id": item.id}


@app.get("/ledger/summary", dependencies=[Depends(require_api_key)])
def ledger_summary():
    with SessionLocal() as db:
        rows = db.scalars(select(LedgerEntry)).all()
        income = sum(x.amount for x in rows if x.entry_type == "income")
        expense = sum(x.amount for x in rows if x.entry_type == "expense")
        return {"income": income, "expense": expense, "net": income - expense, "entries": len(rows)}


@app.get("/ledger", dependencies=[Depends(require_api_key)])
def ledger_entries():
    with SessionLocal() as db:
        rows = db.scalars(select(LedgerEntry).order_by(LedgerEntry.created_at.desc()).limit(200)).all()
        return [{
            "id": x.id, "entry_type": x.entry_type, "category": x.category,
            "amount": x.amount, "note": x.note,
        } for x in rows]


@app.get("/audit", dependencies=[Depends(require_api_key)])
def audit_entries():
    with SessionLocal() as db:
        rows = db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)).all()
        return [{
            "id": x.id, "event_type": x.event_type, "object_id": x.object_id,
            "details": x.details, "created_at": x.created_at,
        } for x in rows]
