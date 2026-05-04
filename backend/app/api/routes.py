from fastapi import APIRouter, HTTPException, Request
from app.models.schemas import SignalIn, WorkItemUpdate, WorkItemStatus
from app.workers.signal_processor import buffer_signal
from app.core.database import get_pg_pool, get_mongo, get_redis
from app.services.work_item_state import get_state, StateError
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/signals")
@limiter.limit("10000/minute")
async def ingest_signal(signal: SignalIn, request: Request):
    await buffer_signal(signal)
    return {"status": "buffered"}

@router.get("/work-items")
async def list_work_items():
    pg = await get_pg_pool()
    rows = await pg.fetch("SELECT * FROM work_items ORDER BY created_at DESC LIMIT 100")
    return [dict(r) for r in rows]

@router.get("/work-items/{work_id}")
async def get_work_item(work_id: int):
    pg = await get_pg_pool()
    row = await pg.fetchrow("SELECT * FROM work_items WHERE id=$1", work_id)
    if not row:
        raise HTTPException(status_code=404, detail="Work item not found")
    mongo = get_mongo()
    signals = await mongo["signals"].find({"work_item_id": work_id}).to_list(200)
    for s in signals:
        s["_id"] = str(s["_id"])
    return {"work_item": dict(row), "signals": signals}

@router.patch("/work-items/{work_id}")
async def update_work_item(work_id: int, body: WorkItemUpdate):
    pg = await get_pg_pool()
    row = await pg.fetchrow("SELECT * FROM work_items WHERE id=$1", work_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    current_status = WorkItemStatus(row["status"])
    state = get_state(current_status)
    if not state:
        raise HTTPException(status_code=400, detail="Work item already closed")

    # Validate transition (RCA check happens here)
    try:
        state.validate_transition(body.rca)
    except StateError as e:
        raise HTTPException(status_code=422, detail=str(e))

    next_status = state.next_state()

    mttr = None
    if next_status == WorkItemStatus.CLOSED and body.rca:
        delta = body.rca.incident_end - body.rca.incident_start
        mttr = int(delta.total_seconds() / 60)  # in minutes
        async with pg.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE work_items SET status=$1, mttr_minutes=$2, updated_at=NOW() WHERE id=$3",
                    next_status.value, mttr, work_id
                )
                await conn.execute(
                    """INSERT INTO rca_records (work_item_id, incident_start, incident_end,
                       root_cause_category, fix_applied, prevention_steps)
                       VALUES ($1,$2,$3,$4,$5,$6)""",
                    work_id, body.rca.incident_start, body.rca.incident_end,
                    body.rca.root_cause_category.value,
                    body.rca.fix_applied, body.rca.prevention_steps
                )
    else:
        await pg.execute(
            "UPDATE work_items SET status=$1, updated_at=NOW() WHERE id=$2",
            next_status.value, work_id
        )

    redis = await get_redis()
    await redis.hset("dashboard", str(work_id), f"{row['component_id']}|{row['severity']}|{next_status.value}")
    return {"status": next_status, "mttr_minutes": mttr}

@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@router.get("/dashboard")
async def dashboard():
    redis = await get_redis()
    data = await redis.hgetall("dashboard")
    result = []
    for wid, val in data.items():
        parts = val.split("|")
        result.append({"id": wid, "component_id": parts[0], "severity": parts[1], "status": parts[2]})
    return sorted(result, key=lambda x: x["severity"])
