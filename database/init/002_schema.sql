-- Source registry
CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    agency TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    description TEXT,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_verified_at TIMESTAMPTZ,
    UNIQUE (agency, dataset_name)
);

-- Intersections
CREATE TABLE IF NOT EXISTS intersections (
    id BIGSERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(id),
    source_object_id TEXT,
    roadway TEXT,
    intersecting_roadway TEXT,
    description TEXT,
    district TEXT,
    county TEXT,
    geometry GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Traffic monitoring sites
CREATE TABLE IF NOT EXISTS traffic_sites (
    id BIGSERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(id),
    source_site_id TEXT,
    roadway TEXT,
    description TEXT,
    geometry GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source_id, source_site_id)
);

-- Traffic observations
CREATE TABLE IF NOT EXISTS traffic_observations (
    id BIGSERIAL PRIMARY KEY,
    traffic_site_id BIGINT REFERENCES traffic_sites(id),
    source_id INTEGER REFERENCES data_sources(id),
    observation_date DATE,
    start_time TIME,
    end_time TIME,
    volume NUMERIC,
    unit TEXT NOT NULL DEFAULT 'vehicles/hour',
    raw_source_reference TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Traffic signals
CREATE TABLE IF NOT EXISTS traffic_signals (
    id BIGSERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(id),
    source_signal_id TEXT,
    signal_type TEXT,
    roadway TEXT,
    geometry GEOMETRY(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Roadway segments with AADT
CREATE TABLE IF NOT EXISTS roadway_segments (
    id BIGSERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES data_sources(id),
    source_object_id TEXT,
    roadway TEXT,
    aadt INTEGER,
    aadt_year INTEGER,
    geometry GEOMETRY(LineString, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
