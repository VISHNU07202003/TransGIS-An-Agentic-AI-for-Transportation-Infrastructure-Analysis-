import sqlite3
import pytest

def test_one_to_many_integrity():
    """
    Validates that a single observation linked to an association group (which maps to multiple edges)
    does not cause double-counting when aggregated.
    """
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    
    # Minimal schema reflecting 003_canonical_schema.sql
    cur.executescript("""
        CREATE TABLE source_features (id TEXT PRIMARY KEY);
        CREATE TABLE feature_association_groups (id TEXT PRIMARY KEY, source_feature_id TEXT);
        CREATE TABLE feature_associations (
            id TEXT PRIMARY KEY,
            association_group_id TEXT,
            canonical_edge_id TEXT
        );
        CREATE TABLE observations (
            id TEXT PRIMARY KEY,
            association_group_id TEXT,
            metric TEXT,
            value REAL
        );
    """)
    
    # 1. Insert source feature
    cur.execute("INSERT INTO source_features (id) VALUES ('FDOT-1')")
    
    # 2. Insert ONE association group
    cur.execute("INSERT INTO feature_association_groups (id, source_feature_id) VALUES ('GROUP-1', 'FDOT-1')")
    
    # 3. Insert THREE canonical edges belonging to this group (e.g. divided highway + extra segment)
    cur.execute("INSERT INTO feature_associations (id, association_group_id, canonical_edge_id) VALUES ('ASSOC-1', 'GROUP-1', 'EDGE-1')")
    cur.execute("INSERT INTO feature_associations (id, association_group_id, canonical_edge_id) VALUES ('ASSOC-2', 'GROUP-1', 'EDGE-2')")
    cur.execute("INSERT INTO feature_associations (id, association_group_id, canonical_edge_id) VALUES ('ASSOC-3', 'GROUP-1', 'EDGE-3')")
    
    # 4. Insert ONE observation linked to the GROUP
    cur.execute("INSERT INTO observations (id, association_group_id, metric, value) VALUES ('OBS-1', 'GROUP-1', 'AADT', 1000.0)")
    
    # The Query: What is the total AADT in the system?
    # Correct aggregation: sum the observations directly, or group by observation ID if joining.
    # If a naive developer joins edges -> assocs -> group -> observations without distinct, they get 3000.0
    
    cur.execute("""
        SELECT SUM(value) FROM (
            SELECT DISTINCT o.id, o.value 
            FROM observations o
            JOIN feature_association_groups g ON o.association_group_id = g.id
            JOIN feature_associations a ON a.association_group_id = g.id
            WHERE a.canonical_edge_id IN ('EDGE-1', 'EDGE-2', 'EDGE-3')
        )
    """)
    
    total_aadt = cur.fetchone()[0]
    
    # Ensure it is exactly 1000.0, NOT 3000.0
    assert total_aadt == 1000.0, f"Expected 1000.0 AADT, got {total_aadt}. Data aggregation multiplied the source!"

    conn.close()
