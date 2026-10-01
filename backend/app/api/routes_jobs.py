import json
import time
from fastapi import APIRouter, Request, HTTPException
from app.schemas import ChatRequest
from app.security import require_role
from app.jobs import submit_job
from app.operational import get_store, Job

router = APIRouter(prefix="/api/analyses", tags=["analysis jobs"])

def job_payload(job):
    return {"id": job.id, "status": job.status, "request_id": job.request_id,
            "created_at": job.created_at, "result": json.loads(job.result) if job.result else None, "error": job.error}

@router.post("", status_code=202)
def submit(payload: ChatRequest, request: Request):
    principal = require_role(request)
    try:
        job = submit_job(principal.subject, request.state.request_id, payload.model_dump(mode="json"))
    except OverflowError as exc:
        raise HTTPException(429, str(exc), headers={"Retry-After": "10"}) from exc
    return job_payload(job)

@router.get("/{job_id}")
def read(job_id: str, request: Request):
    with get_store().session() as s:
        job = s.get(Job, job_id)
        if not job or job.owner != request.state.principal.subject or job.expires_at < time.time():
            raise HTTPException(404, "Analysis not found")
        return job_payload(job)

@router.delete("/{job_id}", status_code=204)
def cancel(job_id: str, request: Request):
    from sqlalchemy import update
    with get_store().session.begin() as s:
        job = s.get(Job, job_id)
        if not job or job.owner != request.state.principal.subject:
            raise HTTPException(404, "Analysis not found")
        s.execute(update(Job).where(Job.id == job_id, Job.status.in_(["queued", "running"])).values(status="cancelled", finished_at=time.time()))
