import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.api.routes import router, limiter
from app.workers.signal_processor import process_signals, metrics_reporter
from app.core.database import get_pg_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    pg = await get_pg_pool()
    await pg.execute("""
        CREATE TABLE IF NOT EXISTS work_items (
            id SERIAL PRIMARY KEY,
            component_id TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'OPEN',
            mttr_minutes INT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    await pg.execute("""
        CREATE TABLE IF NOT EXISTS rca_records (
            id SERIAL PRIMARY KEY,
            work_item_id INT REFERENCES work_items(id),
            incident_start TIMESTAMPTZ,
            incident_end TIMESTAMPTZ,
            root_cause_category TEXT,
            fix_applied TEXT,
            prevention_steps TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    asyncio.create_task(process_signals())
    asyncio.create_task(metrics_reporter())
    yield

app = FastAPI(title="Incident Management System", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api")
