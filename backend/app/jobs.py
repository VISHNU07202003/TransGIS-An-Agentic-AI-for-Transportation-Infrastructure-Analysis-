"""Durable database queue. Atomic claims, bounded workers, owner isolation and expiry."""
import json
import logging
import threading
import time
import uuid
from sqlalchemy import select, update, delete, func
from app.config import get_settings
from app.operational import get_store, Job, ProviderState
from app.security import deadline_context, request_id_context
from app.schemas import ChatRequest

logger = logging.getLogger(__name__)

def run_analysis(payload):
    from app.agents.agent import TransportationAgent
    from app.db import check_database_connection, SessionLocal
    db = SessionLocal() if check_database_connection() else None
    try:
        return TransportationAgent().process_query(ChatRequest.model_validate(payload), db)
    finally:
        if db:
            db.close()

def submit_job(owner, request_id, payload):
    store = get_store()
    now = time.time()
    store.ensure_provider("analysis-queue")
    with store.session.begin() as s:
        s.execute(delete(Job).where(Job.expires_at < now))
        s.execute(update(ProviderState).where(ProviderState.name == "analysis-queue").values(last_success=now))
        count = s.scalar(select(func.count()).select_from(Job).where(Job.status.in_(["queued", "running"])))
        if count >= get_settings().job_queue_limit:
            raise OverflowError("Analysis queue is full")
        owner_count = s.scalar(select(func.count()).select_from(Job).where(Job.owner == owner, Job.status.in_(["queued", "running"])))
        if owner_count >= 3:
            raise OverflowError("You already have three pending analyses")
        job = Job(id=str(uuid.uuid4()), owner=owner, request_id=request_id, status="queued", payload=json.dumps(payload), created_at=now, expires_at=now + get_settings().job_retention_seconds)
        s.add(job)
    return job

def process_one():
    store = get_store()
    now = time.time()
    with store.session.begin() as s:
        s.execute(update(Job).where(Job.status == "running", Job.started_at < now - get_settings().job_deadline_seconds - 30).values(status="failed", error="Worker interrupted or analysis deadline exceeded. Submit again.", finished_at=now))
        s.execute(delete(Job).where(Job.expires_at < now))
        job_id = s.scalar(select(Job.id).where(Job.status == "queued").order_by(Job.created_at).limit(1))
        if not job_id:
            return False
        claimed = s.execute(update(Job).where(Job.id == job_id, Job.status == "queued").values(status="running", started_at=now))
        if not claimed.rowcount:
            return False
        job = s.get(Job, job_id)
        payload, request_id = json.loads(job.payload), job.request_id
    trace = request_id_context.set(request_id)
    deadline = deadline_context.set(time.monotonic() + get_settings().job_deadline_seconds)
    try:
        result = run_analysis(payload)
        result.request_id = request_id
        from app.security import check_deadline
        check_deadline()
        values = {"status": "succeeded", "result": result.model_dump_json(), "finished_at": time.time()}
    except Exception:
        logger.exception("analysis_failed", extra={"job_id": job_id})
        values = {"status": "failed", "error": "Analysis could not finish. Retry or contact the operator with the request ID.", "finished_at": time.time()}
    finally:
        deadline_context.reset(deadline)
        request_id_context.reset(trace)
    with store.session.begin() as s:
        s.execute(update(Job).where(Job.id == job_id, Job.status == "running").values(**values))
    return True

def start_workers():
    stop = threading.Event()
    def loop():
        while not stop.is_set():
            try:
                worked = process_one()
            except Exception:
                logger.exception("worker_iteration_failed")
                worked = False
            if not worked:
                stop.wait(1)
    threads = [threading.Thread(target=loop, daemon=True, name=f"analysis-worker-{i}") for i in range(get_settings().job_workers)]
    for thread in threads:
        thread.start()
    return stop, threads
