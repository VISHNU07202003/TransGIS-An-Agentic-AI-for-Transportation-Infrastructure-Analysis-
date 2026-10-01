"""Bounded public-provider reads, persistent caching and shared circuit breakers."""
import asyncio
import hashlib
import json
import logging
import time
from urllib.parse import urlparse
import httpx
from sqlalchemy import update
from app.config import get_settings
from app.operational import get_store, ProviderState
from app.security import check_deadline, deadline_context

logger = logging.getLogger(__name__)

class ProviderUnavailable(RuntimeError):
    pass

class SchemaChanged(ProviderUnavailable):
    pass

def provider_name(url):
    parsed = urlparse(url)
    return (parsed.netloc + parsed.path.rstrip("/").removesuffix("/query"))[:200]

def _validate(data, required_fields):
    if not isinstance(data, (dict, list)):
        raise SchemaChanged("Provider did not return a JSON object or array")
    if isinstance(data, dict) and "error" in data:
        raise ProviderUnavailable("Provider returned an API error")
    if required_fields:
        features = data.get("features") if isinstance(data, dict) else data
        if not isinstance(features, list):
            raise SchemaChanged("Missing features array")
        for feature in features:
            attrs = feature.get("attributes", feature) if isinstance(feature, dict) else {}
            if not isinstance(attrs, dict) or not set(required_fields).issubset(attrs):
                raise SchemaChanged("Required source fields are missing")
    return data

def get_json_sync(url, params=None, required_fields=None, *, ttl=None, force=False):
    check_deadline()
    settings = get_settings()
    store = get_store()
    name = provider_name(url)
    key = hashlib.sha256(json.dumps([url, params or {}], sort_keys=True).encode()).hexdigest()
    if not force:
        cached = store.cache_get(key)
        if cached is not None:
            return _validate(cached, required_fields)
    store.ensure_provider(name)
    now = time.time()
    with store.session.begin() as s:
        row = s.get(ProviderState, name)
        if row.opened_until > now:
            raise ProviderUnavailable("Provider circuit is open; retry later")
        if row.failures >= settings.circuit_failure_threshold:
            claim = s.execute(update(ProviderState).where(ProviderState.name == name, ProviderState.opened_until <= now).values(opened_until=now + settings.provider_timeout_seconds + 5))
            if not claim.rowcount:
                raise ProviderUnavailable("Provider recovery probe is running")
    remaining = (deadline_context.get() or (time.monotonic() + settings.provider_timeout_seconds)) - time.monotonic()
    try:
        with httpx.Client(timeout=min(settings.provider_timeout_seconds, max(.1, remaining)), follow_redirects=True) as client:
            response = client.get(url, params=params, headers={"User-Agent": "TransGIS/2.0 academic transportation research"})
            response.raise_for_status()
            data = _validate(response.json(), required_fields)
        store.cache_put(key, data, ttl if ttl is not None else settings.cache_ttl_seconds)
        with store.session.begin() as s:
            s.execute(update(ProviderState).where(ProviderState.name == name).values(failures=0, opened_until=0, last_success=time.time(), last_error=None))
        return data
    except (httpx.HTTPError, ValueError, ProviderUnavailable) as exc:
        with store.session.begin() as s:
            failures = s.execute(update(ProviderState).where(ProviderState.name == name).values(failures=ProviderState.failures + 1, last_error=type(exc).__name__).returning(ProviderState.failures)).scalar_one()
            if failures >= settings.circuit_failure_threshold:
                s.execute(update(ProviderState).where(ProviderState.name == name).values(opened_until=time.time() + settings.circuit_reset_seconds))
            if isinstance(exc, SchemaChanged):
                s.execute(update(ProviderState).where(ProviderState.name == name).values(schema_status="changed", schema_checked_at=time.time(), schema_detail=str(exc)))
        logger.warning("provider_read_failed", extra={"provider": name, "error_type": type(exc).__name__})
        raise ProviderUnavailable(f"{name}: source unavailable or schema incompatible") from exc

async def get_json_async(url, params=None, required_fields=None, **kwargs):
    return await asyncio.to_thread(get_json_sync, url, params, required_fields, **kwargs)
