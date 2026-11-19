from datetime import datetime, timezone
from uuid import uuid4
import hmac

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from workers import asgi

VERSION = "0.5.0"
app = FastAPI(
    title="AURA — Autonomous Unified Revenue Agent",
    version=VERSION,
    docs_url="/docs",
    redoc_url=None,
)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_env(request: Request):
    return request.scope.get("env")


def get_db(request: Request):
    env = get_env(request)
    if env is None or not getattr(env, "DB", None):
        raise HTTPException(503, "Database binding DB is not configured")
    return env.DB


async def require_api_key(request: Request):
    env = get_env(request)
    expected = getattr(env, "AURA_API_KEY", None) if env else None
    supplied = request.headers.get("X-AURA-API-Key", "")
    if not expected:
        raise HTTPException(503, "AURA_API_KEY secret has not been configured")
    if not supplied or not hmac.compare_digest(str(supplied), str(expected)):
        raise HTTPException(401, "Invalid API key")


async def write_audit(db, event_type: str, object_id: str, details: str = ""):
    await db.prepare(
        "INSERT INTO audit_log (id, event_type, object_id, details, created_at) VALUES (?, ?, ?, ?, ?)"
    ).bind(uuid4().hex, event_type, object_id, details[:1000], now_iso()).run()


class OpportunityIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    channel: str = Field(min_length=2, max_length=80)
    rationale: str = Field(min_length=3, max_length=3000)
    estimated_cost: float = Field(default=0, ge=0)
    estimated_revenue: float = Field(default=0, ge=0)
    risk_level: str = Field(default="medium", pattern="^(low|medium|high)$")


class OpportunityStatusIn(BaseModel):
    status: str = Field(pattern="^(proposed|reviewing|shortlisted|rejected|archived)$")


class ApprovalIn(BaseModel):
    action_type: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=3, max_length=3000)
    amount: float = Field(default=0, ge=0)


class LedgerIn(BaseModel):
    entry_type: str = Field(pattern="^(income|expense)$")
    category: str = Field(min_length=2, max_length=80)
    amount: float = Field(gt=0)
    note: str = Field(default="", max_length=1000)

class ContentItemIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    platform: str = Field(default="YouTube", pattern="^(YouTube|TikTok|Instagram|Website)$")
    format: str = Field(default="Shorts", pattern="^(Shorts|Long-form|Carousel|Article)$")
    pillar: str = Field(default="Manhua review", max_length=80)
    hook: str = Field(min_length=3, max_length=500)
    script: str = Field(default="", max_length=10000)
    rights_status: str = Field(default="needs_review", pattern="^(needs_review|cleared|not_cleared)$")

class ContentStatusIn(BaseModel):
    status: str = Field(pattern="^(idea|draft|in_review|approved|published|paused)$")

class AgentTaskIn(BaseModel):
    agent: str = Field(min_length=2, max_length=80)
    objective: str = Field(min_length=5, max_length=2000)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    related_opportunity_id: str = Field(default="", max_length=64)

class AgentTaskStatusIn(BaseModel):
    status: str = Field(pattern="^(queued|in_progress|blocked|completed|cancelled)$")
    result_summary: str = Field(default="", max_length=3000)



DASHBOARD = r"""
<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AURA — Operations</title>
<style>
:root{color-scheme:dark;--bg:#0b1020;--panel:#141c30;--line:#26334d;--muted:#9aa9c3;--text:#edf3ff;--accent:#9b8cff;--green:#6ee7b7;--red:#fda4af}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,Segoe UI,sans-serif}
main{max-width:1120px;margin:auto;padding:24px 18px 60px}.top{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}
h1{font-size:25px;margin:0}h2{font-size:17px;margin:0 0 14px}.muted,.hint{color:var(--muted)}.hint{font-size:12px}
.panel,.metric{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:17px;margin-top:16px}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.metric strong{display:block;font-size:23px;margin-top:5px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}.tab,button{border:1px solid var(--line);background:#202b45;color:var(--text);padding:9px 13px;border-radius:9px;cursor:pointer}
.tab.active,button.primary{background:var(--accent);color:#11152a;border-color:var(--accent);font-weight:700}
input,select,textarea{width:100%;padding:10px;border-radius:8px;border:1px solid var(--line);background:#0e1729;color:var(--text);margin:5px 0 11px}
textarea{min-height:75px;resize:vertical}label{display:block;color:var(--muted);font-size:13px}
.row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.actions{display:flex;gap:7px;flex-wrap:wrap}
table{width:100%;border-collapse:collapse;font-size:13px}td,th{text-align:left;padding:10px 7px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted)}
.hidden{display:none}.status{font-size:12px;border:1px solid var(--line);padding:3px 7px;border-radius:20px}.ok{color:var(--green)}.bad{color:var(--red)}
#login{max-width:480px;margin:60px auto}.scroll{overflow:auto}.notice{padding:10px;border-radius:8px;background:#202b45;margin-top:10px}
@media(max-width:700px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.row{grid-template-columns:1fr}main{padding:17px 12px}}
</style></head>
<body><main>
<div id="login" class="panel"><h1>AURA</h1><p class="muted">Operations dashboard · guarded mode</p>
<label>API key</label><input id="key" type="password" autocomplete="off" placeholder="Masukkan AURA_API_KEY">
<button class="primary" onclick="connect()">Connect</button><p class="hint">Key hanya disimpan di session browser ini, bukan di repository.</p><div id="loginmsg" class="hint"></div></div>
<div id="app" class="hidden">
<div class="top"><div><h1>AURA <span class="status">GUARDED</span></h1><div class="muted">Autonomous Unified Revenue Agent · <span id="stamp">—</span></div></div><div class="actions"><button onclick="refresh()">Refresh</button><button onclick="logout()">Lock</button></div></div>
<div class="grid">
<div class="metric"><span class="muted">Confirmed income</span><strong id="income">Rp0</strong></div>
<div class="metric"><span class="muted">Recorded expenses</span><strong id="expense">Rp0</strong></div>
<div class="metric"><span class="muted">Net recorded</span><strong id="net">Rp0</strong></div>
<div class="metric"><span class="muted">Pending approvals</span><strong id="pending">0</strong></div>
</div>
<div class="tabs"><button class="tab active" data-tab="opps">Opportunities</button><button class="tab" data-tab="content">Content</button><button class="tab" data-tab="approvals">Approvals</button><button class="tab" data-tab="ledger">Ledger</button></div>
<section id="opps" class="panel"><h2>Opportunity pipeline</h2>
<form id="oppform"><div class="row"><div><label>Opportunity</label><input name="title" required minlength="3"></div><div><label>Channel</label><select name="channel"><option>YouTube</option><option>TikTok</option><option>Google / SEO</option><option>Website</option><option>Instagram</option><option>Affiliate marketplace</option><option>Other</option></select></div></div>
<label>Rationale</label><textarea name="rationale" required></textarea><div class="row"><div><label>Estimated cost (IDR)</label><input name="estimated_cost" type="number" min="0" value="0"></div><div><label>Estimated revenue (IDR)</label><input name="estimated_revenue" type="number" min="0" value="0"></div></div>
<label>Risk</label><select name="risk_level"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select><button class="primary">Add opportunity</button></form><div id="opptable" class="scroll"></div></section>
<section id="content" class="panel hidden"><h2>Content production queue</h2>
<p class="hint">Draft planning only. Approval requires rights status = cleared. Publishing is not automated.</p>
<form id="contentform"><div class="row"><div><label>Working title</label><input name="title" required minlength="3"></div><div><label>Platform</label><select name="platform"><option>YouTube</option><option>TikTok</option><option>Instagram</option><option>Website</option></select></div></div>
<div class="row"><div><label>Format</label><select name="format"><option>Shorts</option><option>Long-form</option><option>Carousel</option><option>Article</option></select></div><div><label>Content pillar</label><input name="pillar" value="Manhua review" required></div></div>
<label>Hook</label><textarea name="hook" required></textarea><label>Script / notes</label><textarea name="script"></textarea>
<label>Rights status</label><select name="rights_status"><option value="needs_review">Needs review</option><option value="cleared">Cleared</option><option value="not_cleared">Not cleared</option></select>
<button class="primary">Add content idea</button></form><div id="contenttable" class="scroll"></div></section>
<section id="approvals" class="panel hidden"><h2>Human approval queue</h2><p class="hint">Approval is a recorded decision only. It does not automatically execute a payment or purchase.</p>
<form id="approvalform"><div class="row"><div><label>Action type</label><input name="action_type" placeholder="e.g. paid promotion" required></div><div><label>Amount (IDR)</label><input name="amount" type="number" min="0" value="0"></div></div><label>Description</label><textarea name="description" required></textarea><button class="primary">Submit for approval</button></form><div id="approvaltable" class="scroll"></div></section>
<section id="ledger" class="panel hidden"><h2>Revenue & expense ledger</h2><form id="ledgerform"><div class="row"><div><label>Type</label><select name="entry_type"><option value="income">Income</option><option value="expense">Expense</option></select></div><div><label>Category</label><input name="category" required></div></div><div class="row"><div><label>Amount (IDR)</label><input name="amount" type="number" min="1" required></div><div><label>Note</label><input name="note"></div></div><button class="primary">Record entry</button></form><div id="ledgertable" class="scroll"></div></section>
<div id="msg" class="notice hidden"></div>
</div></main>
<script>
let apiKey=sessionStorage.getItem("aura_key")||"";
const fmt=n=>new Intl.NumberFormat("id-ID",{style:"currency",currency:"IDR",maximumFractionDigits:0}).format(Number(n||0));
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
async function api(path,opts={}){const r=await fetch(path,{...opts,headers:{"Content-Type":"application/json","X-AURA-API-Key":apiKey,...(opts.headers||{})}});let d={};try{d=await r.json()}catch{}if(!r.ok)throw Error(d.detail||("HTTP "+r.status));return d}
function connect(){apiKey=document.getElementById("key").value.trim();if(!apiKey)return;sessionStorage.setItem("aura_key",apiKey);refresh().then(()=>{document.getElementById("login").classList.add("hidden");document.getElementById("app").classList.remove("hidden")}).catch(e=>{sessionStorage.removeItem("aura_key");document.getElementById("loginmsg").textContent=e.message})}
function logout(){sessionStorage.removeItem("aura_key");apiKey="";location.reload()}
function say(s){const m=document.getElementById("msg");m.textContent=s;m.classList.remove("hidden");setTimeout(()=>m.classList.add("hidden"),3500)}
async function refresh(){const [o,c,a,l,s]=await Promise.all([api("/opportunities"),api("/content"),api("/approvals"),api("/ledger"),api("/ledger/summary")]);document.getElementById("income").textContent=fmt(s.income);document.getElementById("expense").textContent=fmt(s.expense);document.getElementById("net").textContent=fmt(s.net);document.getElementById("pending").textContent=a.filter(x=>x.status==="pending").length;document.getElementById("stamp").textContent=new Date().toLocaleString("id-ID");
document.getElementById("opptable").innerHTML=table(["Opportunity","Channel","Est. revenue","Risk","Status","Action"],o.map(x=>[esc(x.title),esc(x.channel),fmt(x.estimated_revenue),esc(x.risk_level),esc(x.status),x.status==="proposed"?'<button onclick="statusOpp(\''+x.id+'\',\'reviewing\')">Review</button>':"—"]));
document.getElementById("contenttable").innerHTML=table(["Content","Platform","Format","Rights","Status","Action"],c.map(x=>[esc(x.title),esc(x.platform),esc(x.format),esc(x.rights_status),esc(x.status),x.status==="idea"?'<button onclick="statusContent(\''+x.id+'\',\'draft\')">Draft</button>':x.status==="draft"?'<button onclick="statusContent(\''+x.id+'\',\'in_review\')">Review</button>':x.status==="in_review"&&x.rights_status==="cleared"?'<button onclick="statusContent(\''+x.id+'\',\'approved\')">Approve</button>':"—"]));
document.getElementById("approvaltable").innerHTML=table(["Action","Amount","Status","Created","Decision"],a.map(x=>[esc(x.description),fmt(x.amount),esc(x.status),esc(x.created_at),x.status==="pending"?' <button onclick="decide(\''+x.id+'\',\'approved\')">Approve</button> <button onclick="decide(\''+x.id+'\',\'rejected\')">Reject</button>':"—"]));
document.getElementById("ledgertable").innerHTML=table(["Type","Category","Amount","Note","Created"],l.map(x=>[esc(x.entry_type),esc(x.category),fmt(x.amount),esc(x.note),esc(x.created_at)]))}
function table(head,rows){return '<table><thead><tr>'+head.map(x=>'<th>'+x+'</th>').join('')+'</tr></thead><tbody>'+(rows.length?rows.map(r=>'<tr>'+r.map(x=>'<td>'+x+'</td>').join('')+'</tr>').join(''):'<tr><td colspan="'+head.length+'" class="muted">No data yet</td></tr>')+'</tbody></table>'}
async function statusOpp(id,status){try{await api('/opportunities/'+id+'/status',{method:'POST',body:JSON.stringify({status})});await refresh()}catch(e){say(e.message)}}
async function statusContent(id,status){try{await api('/content/'+id+'/status',{method:'POST',body:JSON.stringify({status})});await refresh()}catch(e){say(e.message)}}
async function decide(id,decision){if(!confirm('Catat keputusan '+decision+'?'))return;try{await api('/approvals/'+id+'/decision?decision='+decision,{method:'POST'});await refresh()}catch(e){say(e.message)}}
function formData(f){return Object.fromEntries(new FormData(f).entries())}
document.getElementById("oppform").addEventListener("submit",async e=>{e.preventDefault();let d=formData(e.target);d.estimated_cost=Number(d.estimated_cost);d.estimated_revenue=Number(d.estimated_revenue);try{await api("/opportunities",{method:"POST",body:JSON.stringify(d)});e.target.reset();await refresh();say("Opportunity saved")}catch(x){say(x.message)}});
document.getElementById("contentform").addEventListener("submit",async e=>{e.preventDefault();let d=formData(e.target);try{await api("/content",{method:"POST",body:JSON.stringify(d)});e.target.reset();await refresh();say("Content idea saved")}catch(x){say(x.message)}});
document.getElementById("approvalform").addEventListener("submit",async e=>{e.preventDefault();let d=formData(e.target);d.amount=Number(d.amount);try{await api("/approvals",{method:"POST",body:JSON.stringify(d)});e.target.reset();await refresh();say("Approval request queued")}catch(x){say(x.message)}});
document.getElementById("ledgerform").addEventListener("submit",async e=>{e.preventDefault();let d=formData(e.target);d.amount=Number(d.amount);try{await api("/ledger",{method:"POST",body:JSON.stringify(d)});e.target.reset();await refresh();say("Ledger entry saved")}catch(x){say(x.message)}});
document.querySelectorAll(".tab").forEach(b=>b.addEventListener("click",()=>{document.querySelectorAll(".tab").forEach(x=>x.classList.toggle("active",x===b));["opps","content","approvals","ledger"].forEach(x=>document.getElementById(x).classList.toggle("hidden",x!==b.dataset.tab))}));
if(apiKey){document.getElementById("key").value=apiKey;connect()}
</script></body></html>
"""


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "AURA",
        "status": "online",
        "version": VERSION,
        "platform": "cloudflare-workers",
        "dashboard": "/dashboard",
        "message": "Core API is running. External platform integrations are not connected.",
    }


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    return HTMLResponse(DASHBOARD)


@app.get("/health")
async def health():
    return {"ok": True, "timestamp": now_iso(), "version": VERSION}


@app.get("/config")
async def config():
    return {
        "mode": "multi_agent_revenue_operations",
        "initial_capital_idr": 0,
        "risk_profile": "moderate",
        "distribution": {"owner_percent": 50, "reinvestment_percent": 50, "frequency": "monthly", "closing_day": 1},
        "spending_requires_owner_approval": True,
        "financial_transactions_require_owner_approval": True,
        "assets": ["youtube", "tiktok", "google", "website", "instagram", "affiliate", "ecommerce", "services", "equities_research", "crypto_research"],
        "autonomy": "guarded",
        "goal": "diversified_net_revenue",
        "live_integrations": [],
        "dashboard_available": True,
        "production_ready": False,
    }


@app.post("/opportunities", dependencies=[Depends(require_api_key)])
async def create_opportunity(payload: OpportunityIn, db=Depends(get_db)):
    item_id = uuid4().hex
    data = payload.model_dump()
    await db.prepare(
        """INSERT INTO opportunities
        (id, title, channel, rationale, estimated_cost, estimated_revenue, risk_level, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'proposed', ?)"""
    ).bind(item_id, data["title"], data["channel"], data["rationale"],
           data["estimated_cost"], data["estimated_revenue"], data["risk_level"], now_iso()).run()
    await write_audit(db, "opportunity.created", item_id, data["title"])
    return {"id": item_id, "status": "proposed"}


@app.get("/opportunities", dependencies=[Depends(require_api_key)])
async def list_opportunities(db=Depends(get_db)):
    result = await db.prepare(
        """SELECT id, title, channel, rationale, estimated_cost, estimated_revenue,
        risk_level, status, created_at FROM opportunities ORDER BY created_at DESC LIMIT 200"""
    ).all()
    return result.results.to_py()


@app.post("/opportunities/{opportunity_id}/status", dependencies=[Depends(require_api_key)])
async def update_opportunity_status(opportunity_id: str, payload: OpportunityStatusIn, db=Depends(get_db)):
    existing = await db.prepare("SELECT id, status FROM opportunities WHERE id = ?").bind(opportunity_id).first()
    if existing is None:
        raise HTTPException(404, "opportunity not found")
    await db.prepare("UPDATE opportunities SET status = ? WHERE id = ?").bind(payload.status, opportunity_id).run()
    await write_audit(db, "opportunity.status_changed", opportunity_id, payload.status)
    return {"id": opportunity_id, "status": payload.status}


@app.post("/approvals", dependencies=[Depends(require_api_key)])
async def create_approval(payload: ApprovalIn, db=Depends(get_db)):
    item_id = uuid4().hex
    data = payload.model_dump()
    await db.prepare(
        """INSERT INTO approvals (id, action_type, description, amount, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', ?)"""
    ).bind(item_id, data["action_type"], data["description"], data["amount"], now_iso()).run()
    await write_audit(db, "approval.requested", item_id, data["action_type"])
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
    await write_audit(db, "approval." + decision, approval_id, "")
    return {"id": approval_id, "status": decision, "execution": "not_executed"}


@app.post("/ledger", dependencies=[Depends(require_api_key)])
async def add_ledger_entry(payload: LedgerIn, db=Depends(get_db)):
    item_id = uuid4().hex
    data = payload.model_dump()
    await db.prepare(
        """INSERT INTO ledger (id, entry_type, category, amount, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?)"""
    ).bind(item_id, data["entry_type"], data["category"], data["amount"], data["note"], now_iso()).run()
    await write_audit(db, "ledger." + data["entry_type"], item_id, data["category"])
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
    income, expense = float(result.income), float(result.expense)
    return {"income": income, "expense": expense, "net": income - expense, "entries": int(result.entries)}


@app.get("/ledger", dependencies=[Depends(require_api_key)])
async def ledger_entries(db=Depends(get_db)):
    result = await db.prepare(
        """SELECT id, entry_type, category, amount, note, created_at
        FROM ledger ORDER BY created_at DESC LIMIT 200"""
    ).all()
    return result.results.to_py()


@app.post("/content", dependencies=[Depends(require_api_key)])
async def create_content_item(payload: ContentItemIn, db=Depends(get_db)):
    item_id = uuid4().hex
    data = payload.model_dump()
    await db.prepare(
        """INSERT INTO content_items
        (id, title, platform, format, pillar, hook, script, rights_status, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'idea', ?, ?)"""
    ).bind(item_id, data["title"], data["platform"], data["format"], data["pillar"],
           data["hook"], data["script"], data["rights_status"], now_iso(), now_iso()).run()
    await write_audit(db, "content.created", item_id, data["title"])
    return {"id": item_id, "status": "idea"}

@app.get("/content", dependencies=[Depends(require_api_key)])
async def list_content_items(db=Depends(get_db)):
    result = await db.prepare(
        """SELECT id, title, platform, format, pillar, hook, script, rights_status, status, created_at, updated_at
        FROM content_items ORDER BY updated_at DESC LIMIT 200"""
    ).all()
    return result.results.to_py()

@app.post("/content/{content_id}/status", dependencies=[Depends(require_api_key)])
async def update_content_status(content_id: str, payload: ContentStatusIn, db=Depends(get_db)):
    existing = await db.prepare("SELECT id, status FROM content_items WHERE id = ?").bind(content_id).first()
    if existing is None:
        raise HTTPException(404, "content item not found")
    if payload.status == "approved":
        item = await db.prepare("SELECT rights_status FROM content_items WHERE id = ?").bind(content_id).first()
        if item.rights_status != "cleared":
            raise HTTPException(409, "content rights must be cleared before approval")
    await db.prepare("UPDATE content_items SET status = ?, updated_at = ? WHERE id = ?").bind(
        payload.status, now_iso(), content_id
    ).run()
    await write_audit(db, "content.status_changed", content_id, payload.status)
    return {"id": content_id, "status": payload.status, "publishing": "not_automated"}

@app.post("/agent-tasks", dependencies=[Depends(require_api_key)])
async def create_agent_task(payload: AgentTaskIn, db=Depends(get_db)):
    task_id = uuid4().hex
    data = payload.model_dump()
    await db.prepare(
        """INSERT INTO agent_tasks
        (id, agent, objective, priority, related_opportunity_id, status, result_summary, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'queued', '', ?, ?)"""
    ).bind(task_id, data["agent"], data["objective"], data["priority"],
           data["related_opportunity_id"], now_iso(), now_iso()).run()
    await write_audit(db, "agent_task.queued", task_id, data["agent"])
    return {"id": task_id, "status": "queued", "execution": "not_started"}

@app.get("/agent-tasks", dependencies=[Depends(require_api_key)])
async def list_agent_tasks(db=Depends(get_db)):
    result = await db.prepare(
        """SELECT id, agent, objective, priority, related_opportunity_id, status, result_summary, created_at, updated_at
        FROM agent_tasks ORDER BY CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END,
        created_at DESC LIMIT 300"""
    ).all()
    return result.results.to_py()

@app.post("/agent-tasks/{task_id}/status", dependencies=[Depends(require_api_key)])
async def update_agent_task(task_id: str, payload: AgentTaskStatusIn, db=Depends(get_db)):
    existing = await db.prepare("SELECT id, status FROM agent_tasks WHERE id = ?").bind(task_id).first()
    if existing is None:
        raise HTTPException(404, "agent task not found")
    await db.prepare(
        "UPDATE agent_tasks SET status = ?, result_summary = ?, updated_at = ? WHERE id = ?"
    ).bind(payload.status, payload.result_summary, now_iso(), task_id).run()
    await write_audit(db, "agent_task.status_changed", task_id, payload.status)
    return {"id": task_id, "status": payload.status, "agent_execution": "not_automated"}

@app.get("/audit", dependencies=[Depends(require_api_key)])
async def audit_entries(db=Depends(get_db)):
    result = await db.prepare(
        """SELECT id, event_type, object_id, details, created_at
        FROM audit_log ORDER BY created_at DESC LIMIT 200"""
    ).all()
    return result.results.to_py()


Default = asgi.entrypoint(app)
