-- Spatial indexes (GiST)
CREATE INDEX IF NOT EXISTS idx_intersections_geometry ON intersections USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_traffic_sites_geometry ON traffic_sites USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_traffic_signals_geometry ON traffic_signals USING GIST (geometry);
CREATE INDEX IF NOT EXISTS idx_roadway_segments_geometry ON roadway_segments USING GIST (geometry);

-- Composite index for temporal queries
CREATE INDEX IF NOT EXISTS idx_traffic_observations_site_date_time ON traffic_observations (traffic_site_id, observation_date, start_time);
