"""Durable operational state. SQLite locally; shared PostgreSQL in production.

No raw access tokens are persisted. Analysis payloads expire with their job.
"""
import json
import time
from functools import lru_cache
from sqlalchemy import create_engine, Column, String, Float, Integer, Text, delete, select, update
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import get_settings


class Base(DeclarativeBase):
    pass


class CacheEntry(Base):
    __tablename__ = "api_cache"
    key = Column(String(64), primary_key=True)
    payload = Column(Text, nullable=False)
    expires_at = Column(Float, nullable=False, index=True)


class Counter(Base):
    __tablename__ = "request_counters"
    key = Column(String(128), primary_key=True)
    count = Column(Integer, nullable=False, default=1)
    expires_at = Column(Float, nullable=False, index=True)


class ProviderState(Base):
    __tablename__ = "provider_state"
    name = Column(String(200), primary_key=True)
    failures = Column(Integer, nullable=False, default=0)
    opened_until = Column(Float, nullable=False, default=0)
    last_success = Column(Float, nullable=True)
    last_error = Column(String(100), nullable=True)
    schema_status = Column(String(40), nullable=False, default="unchecked")
    schema_checked_at = Column(Float, nullable=True)
    schema_detail = Column(Text, nullable=True)


class Job(Base):
    __tablename__ = "analysis_jobs"
    id = Column(String(36), primary_key=True)
    owner = Column(String(100), nullable=False, index=True)
    request_id = Column(String(36), nullable=False)
    status = Column(String(20), nullable=False, index=True)
    payload = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    error = Column(String(200), nullable=True)
    created_at = Column(Float, nullable=False, index=True)
    started_at = Column(Float, nullable=True)
    finished_at = Column(Float, nullable=True)
    expires_at = Column(Float, nullable=False, index=True)


class Store:
    def __init__(self, url):
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        args = {"check_same_thread": False, "timeout": 15} if url.startswith("sqlite") else {"connect_timeout": 5}
        self.engine = create_engine(url, pool_pre_ping=True, connect_args=args)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def insert(self, model, values, conflict=None):
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        stmt = (sqlite_insert if self.engine.dialect.name == "sqlite" else pg_insert)(model).values(**values)
        return stmt.on_conflict_do_update(index_elements=[model.__table__.primary_key.columns.values()[0]], set_=conflict) if conflict else stmt.on_conflict_do_nothing()

    def cache_get(self, key):
        with self.session() as s:
            row = s.get(CacheEntry, key)
            return json.loads(row.payload) if row and row.expires_at > time.time() else None

    def cache_put(self, key, payload, ttl):
        values = {"key": key, "payload": json.dumps(payload), "expires_at": time.time() + ttl}
        with self.session.begin() as s:
            s.execute(delete(CacheEntry).where(CacheEntry.expires_at < time.time()))
            s.execute(self.insert(CacheEntry, values, {"payload": values["payload"], "expires_at": values["expires_at"]}))
            # Bound storage, including still-valid least-recently-expiring entries.
            excess = select(CacheEntry.key).order_by(CacheEntry.expires_at.desc()).offset(get_settings().cache_max_entries)
            s.execute(delete(CacheEntry).where(CacheEntry.key.in_(excess)))

    def increment(self, key, expires_at):
        with self.session.begin() as s:
            s.execute(delete(Counter).where(Counter.expires_at < time.time()))
            stmt = self.insert(Counter, {"key": key, "count": 1, "expires_at": expires_at}, {"count": Counter.count + 1})
            return s.execute(stmt.returning(Counter.count)).scalar_one()

    def ensure_provider(self, name):
        with self.session.begin() as s:
            s.execute(self.insert(ProviderState, {"name": name, "failures": 0, "opened_until": 0, "schema_status": "unchecked"}))


@lru_cache
def get_store():
    return Store(get_settings().state_database_url)
