import asyncio
import time
from collections import defaultdict, deque
from datetime import datetime
from app.core.database import get_pg_pool, get_mongo, get_redis
from app.models.schemas import SignalIn
from app.services.alert_strategy import get_alert_strategy

# In-memory buffer for backpressure handling
signal_buffer: deque = deque(maxlen=100_000)
debounce_map: dict = defaultdict(list)
_metrics = {"processed": 0, "last_reset": time.time()}

async def buffer_signal(signal: SignalIn):
    signal_buffer.append(signal)

async def process_signals():
    """Background worker: drains buffer and applies debounce logic."""
    while True:
        batch = []
        while signal_buffer and len(batch) < 500:
            batch.append(signal_buffer.popleft())

        if batch:
            for sig in batch:
                debounce_map[sig.component_id].append(sig)
            await _flush_debounced()
            _metrics["processed"] += len(batch)

        await asyncio.sleep(0.1)

async def _flush_debounced():
    now = datetime.utcnow().timestamp()
    pg = await get_pg_pool()
    mongo = get_mongo()
    redis = await get_redis()

    for comp_id, signals in list(debounce_map.items()):
        if len(signals) >= 1:
            first = signals[0]
            try:
                # Check if work item exists
                existing = await pg.fetchrow(
                    "SELECT id FROM work_items WHERE component_id=$1 AND status NOT IN ('RESOLVED','CLOSED')",
                    comp_id
                )
                if not existing:
                    severity = first.severity.value
                    work_id = await pg.fetchval(
                        """INSERT INTO work_items (component_id, severity, status, created_at)
                           VALUES ($1, $2, 'OPEN', NOW()) RETURNING id""",
                        comp_id, severity
                    )
                    strategy = get_alert_strategy(first.severity)
                    await strategy.send(comp_id, first.message)
                    await redis.hset("dashboard", str(work_id), f"{comp_id}|{severity}|OPEN")
                else:
                    work_id = existing["id"]

                # Store raw signals in MongoDB
                docs = [s.model_dump() | {"work_item_id": work_id, "ts": datetime.utcnow()} for s in signals]
                await mongo["signals"].insert_many(docs)
                debounce_map.pop(comp_id)
            except Exception as e:
                print(f"[ERROR] flushing signals: {e}")

async def metrics_reporter():
    """Prints throughput every 5 seconds."""
    while True:
        await asyncio.sleep(5)
        elapsed = time.time() - _metrics["last_reset"]
        rate = _metrics["processed"] / elapsed if elapsed > 0 else 0
        print(f"📊 Throughput: {rate:.1f} signals/sec | Buffer: {len(signal_buffer)}")
        _metrics["processed"] = 0
        _metrics["last_reset"] = time.time()
