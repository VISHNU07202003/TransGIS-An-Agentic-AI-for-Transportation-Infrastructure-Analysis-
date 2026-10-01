import json
import logging
from datetime import datetime, timezone
from app.security import request_id_context

class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {"timestamp": datetime.now(timezone.utc).isoformat(), "level": record.levelname,
                   "module": record.name, "message": record.getMessage(), "request_id": request_id_context.get()}
        for key in ("method", "path", "status", "duration_ms", "provider", "error_type", "job_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["error_type"] = record.exc_info[0].__name__
        return json.dumps(payload, ensure_ascii=False)

def setup_logging(log_level):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
