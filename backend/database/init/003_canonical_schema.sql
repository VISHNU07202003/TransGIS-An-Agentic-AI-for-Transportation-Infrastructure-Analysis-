-- 003_canonical_schema.sql
-- TransGIS Phase 2: Canonical Entity Resolution Schema

-- 1. Canonical Topology Base
CREATE TABLE canonical_nodes (
    id VARCHAR(50) PRIMARY KEY, -- e.g., 'GNV-NODE-001'
    geometry GEOMETRY(Point, 4326) NOT NULL,
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_canonical_nodes_geom ON canonical_nodes USING GIST(geometry);

CREATE TABLE canonical_edges (
    id VARCHAR(50) PRIMARY KEY, -- e.g., 'GNV-EDGE-001'
    from_node_id VARCHAR(50) REFERENCES canonical_nodes(id),
    to_node_id VARCHAR(50) REFERENCES canonical_nodes(id),
    geometry GEOMETRY(LineString, 4326) NOT NULL,
    normalized_name VARCHAR(255),
    route_refs VARCHAR(255)[], -- e.g., ['SR 26', 'US 441']
    version INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_canonical_edges_geom ON canonical_edges USING GIST(geometry);
CREATE INDEX idx_canonical_edges_name ON canonical_edges(normalized_name);

-- 2. Raw Source Features
CREATE TABLE source_features (
    id VARCHAR(100) PRIMARY KEY, -- uuid or composite
    dataset_id VARCHAR(100) NOT NULL,
    source_key VARCHAR(100) NOT NULL, -- original ID (e.g., 'OBJECTID' or 'station')
    feature_type VARCHAR(50) NOT NULL, -- 'POINT', 'LINESTRING', etc
    original_geometry GEOMETRY NOT NULL,
    original_crs VARCHAR(50) NOT NULL,
    normalized_geometry GEOMETRY(Geometry, 4326) NOT NULL,
    raw_payload JSONB,
    checksum VARCHAR(64),
    dataset_version VARCHAR(50)
);

CREATE INDEX idx_source_features_geom ON source_features USING GIST(normalized_geometry);
CREATE INDEX idx_source_features_dataset ON source_features(dataset_id, source_key);

-- 3. Conflation Associations (One-to-Many support)
CREATE TABLE feature_association_groups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_feature_id VARCHAR(100) REFERENCES source_features(id) ON DELETE CASCADE,
    matcher_version VARCHAR(50),
    status VARCHAR(20) DEFAULT 'MATCHED', -- 'MATCHED', 'AMBIGUOUS', 'REJECTED', 'MANUAL'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feature_assoc_group_source ON feature_association_groups(source_feature_id);

CREATE TABLE feature_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    association_group_id UUID REFERENCES feature_association_groups(id) ON DELETE CASCADE,
    canonical_node_id VARCHAR(50) REFERENCES canonical_nodes(id),
    canonical_edge_id VARCHAR(50) REFERENCES canonical_edges(id),
    association_type VARCHAR(50) NOT NULL, -- 'EDGE_MATCH', 'NODE_MATCH'
    sequence_order INTEGER, -- ordering when multiple edges make up one source segment
    overlap_length FLOAT,
    source_coverage_ratio FLOAT,
    edge_coverage_ratio FLOAT,
    direction_compatibility VARCHAR(20),
    score FLOAT,
    evidence JSONB,
    CONSTRAINT chk_one_target CHECK (
        (canonical_node_id IS NOT NULL AND canonical_edge_id IS NULL) OR 
        (canonical_node_id IS NULL AND canonical_edge_id IS NOT NULL)
    )
);

CREATE INDEX idx_feature_assoc_node ON feature_associations(canonical_node_id);
CREATE INDEX idx_feature_assoc_edge ON feature_associations(canonical_edge_id);
CREATE INDEX idx_feature_assoc_group ON feature_associations(association_group_id);

-- 4. Traffic Observations
CREATE TABLE observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_feature_id VARCHAR(100) REFERENCES source_features(id) ON DELETE CASCADE,
    association_group_id UUID REFERENCES feature_association_groups(id) ON DELETE SET NULL,
    metric VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50) NOT NULL,
    valid_from DATE,
    valid_to DATE,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_record_id VARCHAR(100),
    dataset_version VARCHAR(50)
);

CREATE INDEX idx_obs_source ON observations(source_feature_id);
CREATE INDEX idx_obs_metric ON observations(metric);

-- 5. Entity Event Sourcing (Tombstones/Splits/Merges)
CREATE TABLE entity_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(20) NOT NULL, -- 'NODE' or 'EDGE'
    entity_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(20) NOT NULL, -- 'CREATED', 'MERGED_INTO', 'SPLIT_FROM', 'RETIRED'
    related_entity_id VARCHAR(50), -- e.g., the new ID it was merged into
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason JSONB
);

CREATE INDEX idx_entity_events_id ON entity_events(entity_id);
