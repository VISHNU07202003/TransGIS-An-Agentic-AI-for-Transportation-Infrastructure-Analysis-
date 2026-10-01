import sqlite3
import pytest

def setup_db(conn):
    conn.executescript("""
        CREATE TABLE datasets (
            id TEXT PRIMARY KEY,
            status TEXT, -- 'STAGING', 'PUBLISHED', 'FAILED'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE source_records (
            id TEXT,
            dataset_id TEXT,
            data TEXT,
            PRIMARY KEY (id, dataset_id)
        );
        -- The view the application actually queries
        CREATE VIEW live_source_records AS 
        SELECT r.* FROM source_records r
        JOIN datasets d ON r.dataset_id = d.id
        WHERE d.status = 'PUBLISHED';
    """)

def test_atomic_publish_and_crash_recovery():
    conn = sqlite3.connect(":memory:")
    setup_db(conn)
    cur = conn.cursor()
    
    # 1. Existing Published Dataset
    cur.execute("INSERT INTO datasets (id, status) VALUES ('v1', 'PUBLISHED')")
    cur.execute("INSERT INTO source_records (id, dataset_id, data) VALUES ('rec-1', 'v1', 'old_data')")
    
    # 2. Worker Starts Ingestion (Staging)
    cur.execute("INSERT INTO datasets (id, status) VALUES ('v2', 'STAGING')")
    cur.execute("INSERT INTO source_records (id, dataset_id, data) VALUES ('rec-1', 'v2', 'new_data')")
    
    # 3. Simulate Worker Crash
    # Dataset 'v2' remains in STAGING. 
    # Let's verify the live view still only shows 'old_data' and no duplicates.
    cur.execute("SELECT data FROM live_source_records")
    live_records = cur.fetchall()
    assert len(live_records) == 1
    assert live_records[0][0] == 'old_data'
    
    # 4. Worker Restarts / Retry
    # In a real system, the worker detects stale 'STAGING' and either cleans it or creates 'v3'
    cur.execute("UPDATE datasets SET status = 'FAILED' WHERE id = 'v2'")
    cur.execute("INSERT INTO datasets (id, status) VALUES ('v3', 'STAGING')")
    cur.execute("INSERT INTO source_records (id, dataset_id, data) VALUES ('rec-1', 'v3', 'new_data')")
    
    # Still protected
    cur.execute("SELECT data FROM live_source_records")
    assert len(cur.fetchall()) == 1
    
    # 5. Atomic Publish Transaction
    try:
        conn.execute("BEGIN TRANSACTION")
        # Demote old published
        cur.execute("UPDATE datasets SET status = 'ARCHIVED' WHERE status = 'PUBLISHED'")
        # Promote new
        cur.execute("UPDATE datasets SET status = 'PUBLISHED' WHERE id = 'v3'")
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        
    # Verify new live view
    cur.execute("SELECT data FROM live_source_records")
    new_live = cur.fetchall()
    assert len(new_live) == 1
    assert new_live[0][0] == 'new_data'
    
    conn.close()
