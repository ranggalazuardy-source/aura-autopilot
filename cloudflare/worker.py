from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from workers import asgi

app = FastAPI(title="AURA — Autonomous Unified Revenue Agent", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-AURA-API-Key"],
)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_db(request: Request):
    env = request.scope.get("env")
    if env is None or not hasattr(env, "DB"):
        raise HTTPException(503, "Database binding DB is not configured")
    return env.DB


async def require_api_key(request: Request):
    env = request.scope.get("env")
    expected = getattr(env, "AURA_API_KEY", None) if env else None
    supplied = request.headers.get("X-AURA-API-Key")
    if not expected:
        raise HTTPException(503, "AURA_API_KEY secret has not been configured")
    if supplied != expected:
        raise HTTPException(401, "Invalid API key")


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
async def root():
    return {
        "name": "AURA",
        "status": "online",
        "version": "0.2.0",
        "platform": "cloudflare-workers",
        "message": "Core API is running. Platform integrations are not connected.",
    }


@app.get("/health")
async def health():
    return {"ok": True, "timestamp": now_iso()}


@app.get("/config")
async def config():
    return {
        "mode": "full_opportunity_discovery",
        "budget": "flexible_with_explicit_spend_approval",
        "assets": ["youtube", "tiktok", "google", "website", "instagram", "marketplace_affiliate"],
        "autonomy": "guarded",
        "goal": "diversified_revenue",
        "live_integrations": [],
        "production_ready": False,
    }


@app.post("/opportunities", dependencies=[Depends(require_api_key)])
async def create_opportunity(payload: OpportunityIn, request: Request, db=Depends(get_db)):
    item_id = uuid4().hex
    data = payload.model_dump()
    await db.prepare(
        """INSERT INTO opportunities
        (id, title, channel, rationale, estimated_cost, estimated_revenue, risk_level, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'proposed', ?)"""
    ).bind(
        item_id, data["title"], data["channel"], data["rationale"],
        data["estimated_cost"], data["estimated_revenue"], data["risk_level"], now_iso()
    ).run()
    return {"id": item_id, "status": "proposed"}


@app.get("/opportunities", dependencies=[Depends(require_api_key)])
async def list_opportunities(db=Depends(get_db)):
    result = await db.prepare(
        """SELECT id, title, channel, rationale, estimated_cost, estimated_revenue,
        risk_level, status, created_at FROM opportunities ORDER BY created_at DESC LIMIT 200"""
    ).all()
    return result.results.to_py()


@app.post("/approvals", dependencies=[Depends(require_api_key)])
async def create_approval(payload: ApprovalIn, db=Depends(get_db)):
    item_id = uuid4().hex
    data = payload.model_dump()
    await db.prepare(
        """INSERT INTO approvals (id, action_type, description, amount, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)"""
    ).bind(item_id, data["action_type"], data["description"], data["amount"], now_iso()).run()
    return {"id": item_id, "status": "pending"}


@app.get("/approvals", dependencies=[Depends(require_api_key)])
async def list_approvals(db=Depends(get_db)):
    result = await db.prepare(
        """SELECT id, action_type, description, amount, status, created_at
        FROM approvals ORDER BY created_at DESC LIMIT 200"""
    ).all()
    return result.results.to_py()


@app.post("/approvals/{approval_id}/decision", dependencies=[Depends(require_api_key)])
async def decide_approval(approval_id: str, decision: str, db=Depends(get_db)):
    if decision not in {"approved", "rejected"}:
        raise HTTPException(400, "decision must be approved or rejected")
    existing = await db.prepare("SELECT id, status FROM approvals WHERE id = ?").bind(approval_id).first()
    if existing is None:
        raise HTTPException(404, "approval not found")
    if existing.status != "pending":
        raise HTTPException(409, "approval already decided")
    await db.prepare("UPDATE approvals SET status = ? WHERE id = ? AND status = 'pending'").bind(
        decision, approval_id
    ).run()
    return {"id": approval_id, "status": decision}


@app.post("/ledger", dependencies=[Depends(require_api_key)])
async def add_ledger_entry(payload: LedgerIn, db=Depends(get_db)):
    if payload.entry_type not in {"income", "expense"}:
        raise HTTPException(400, "entry_type must be income or expense")
    item_id = uuid4().hex
    data = payload.model_dump()
    await db.prepare(
        """INSERT INTO ledger (id, entry_type, category, amount, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?)"""
    ).bind(item_id, data["entry_type"], data["category"], data["amount"], data["note"], now_iso()).run()
    return {"id": item_id}


@app.get("/ledger/summary", dependencies=[Depends(require_api_key)])
async def ledger_summary(db=Depends(get_db)):
    result = await db.prepare(
        """SELECT
        COALESCE(SUM(CASE WHEN entry_type = 'income' THEN amount ELSE 0 END), 0) AS income,
        COALESCE(SUM(CASE WHEN entry_type = 'expense' THEN amount ELSE 0 END), 0) AS expense,
        COUNT(*) AS entries
        FROM ledger"""
    ).first()
    income = float(result.income)
    expense = float(result.expense)
    return {"income": income, "expense": expense, "net": income - expense, "entries": int(result.entries)}


@app.get("/ledger", dependencies=[Depends(require_api_key)])
async def ledger_entries(db=Depends(get_db)):
    result = await db.prepare(
        """SELECT id, entry_type, category, amount, note, created_at
        FROM ledger ORDER BY created_at DESC LIMIT 200"""
    ).all()
    return result.results.to_py()


Default = asgi.entrypoint(app)
