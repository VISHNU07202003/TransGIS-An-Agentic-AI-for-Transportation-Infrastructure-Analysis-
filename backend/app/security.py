"""Per-user opaque bearer tokens, role checks, shared rate limits and request tracing."""
import hashlib
import hmac
import json
import logging
import re
import time
import uuid
from dataclasses import dataclass
from contextvars import ContextVar
from fastapi import HTTPException, Request
from starlette.responses import JSONResponse
from app.config import get_settings
from app.operational import get_store

request_id_context = ContextVar("request_id", default="-")
deadline_context = ContextVar("deadline", default=None)
logger = logging.getLogger(__name__)
ROLES = {"reader": 0, "analyst": 1, "admin": 2}


@dataclass
class Principal:
    subject: str
    role: str


def configured_tokens():
    items = json.loads(get_settings().auth_tokens_json)
    if not isinstance(items, list):
        raise ValueError("AUTH_TOKENS_JSON must be an array")
    subjects = set()
    for item in items:
        if not isinstance(item, dict) or item.get("role") not in ROLES or not re.fullmatch(r"[a-f0-9]{64}", item.get("sha256", "")):
            raise ValueError("Invalid access token hash or role")
        if not re.fullmatch(r"[A-Za-z0-9_.@-]{1,100}", item.get("subject", "")) or item["subject"] in subjects:
            raise ValueError("Every access token needs a unique subject")
        subjects.add(item["subject"])
    return items


def authenticate(request):
    if get_settings().auth_mode == "disabled":
        host = request.client.host if request.client else "unknown"
        return Principal("local-" + hashlib.sha256(host.encode()).hexdigest()[:24], "admin")
    header = request.headers.get("authorization", "")
    if not header.startswith("Bearer ") or len(header) > 1024:
        raise HTTPException(401, "An access token is required", headers={"WWW-Authenticate": "Bearer"})
    digest = hashlib.sha256(header[7:].encode()).hexdigest()
    for item in configured_tokens():
        if hmac.compare_digest(digest, item["sha256"]):
            return Principal(item["subject"], item["role"])
    raise HTTPException(401, "Invalid access token", headers={"WWW-Authenticate": "Bearer"})


def require_role(request: Request, role="analyst"):
    principal = request.state.principal
    if ROLES[principal.role] < ROLES[role]:
        raise HTTPException(403, "Your role does not allow this operation")
    return principal


def check_deadline():
    deadline = deadline_context.get()
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError("Analysis time limit reached")


async def request_controls(request, call_next):
    # Never trust client-provided request ids or X-Forwarded-For without a trusted proxy configuration.
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    token = request_id_context.set(request_id)
    started = time.monotonic()
    status = 500
    try:
        if request.url.path.startswith("/api/") and request.url.path != "/api/auth/config" and request.method != "OPTIONS":
            try:
                request.state.principal = authenticate(request)
                owner = request.state.principal.subject
                minute = int(time.time() // 60)
                analysis = request.method == "POST" and request.url.path in ("/api/chat", "/api/analyses")
                limit = get_settings().analysis_limit_per_minute if analysis else get_settings().rate_limit_per_minute
                key = hashlib.sha256(f"{owner}:{minute}:{analysis}".encode()).hexdigest()
                from starlette.concurrency import run_in_threadpool
                count = await run_in_threadpool(get_store().increment, key, (minute + 1) * 60)
                if count > limit:
                    raise HTTPException(429, "Request limit reached. Try again shortly.", headers={"Retry-After": str(60 - int(time.time() % 60))})
                length = request.headers.get("content-length", "0")
                if not length.isdigit() or int(length) > 32768:
                    raise HTTPException(413, "Request too large")
            except HTTPException as exc:
                response = JSONResponse({"detail": exc.detail, "request_id": request_id}, status_code=exc.status_code, headers=exc.headers)
            else:
                response = await call_next(request)
        else:
            response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Cache-Control"] = "no-store"
        return response
    except Exception:
        logger.exception("request_failed")
        return JSONResponse({"detail": "Service temporarily unavailable", "request_id": request_id}, status_code=503, headers={"X-Request-ID": request_id})
    finally:
        logger.info("http_request", extra={"method": request.method, "path": request.url.path, "status": status, "duration_ms": round((time.monotonic() - started) * 1000)})
        request_id_context.reset(token)
