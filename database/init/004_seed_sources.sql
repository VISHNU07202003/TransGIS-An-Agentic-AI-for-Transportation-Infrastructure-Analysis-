INSERT INTO data_sources (agency, dataset_name, source_url, source_type, description)
VALUES 
    ('FDOT', 'RCI Intersections', 'https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer', 'ArcGIS REST', 'FDOT RCI Intersections'),
    ('FDOT', 'AADT', 'https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer', 'ArcGIS REST', 'FDOT Annual Average Daily Traffic (AADT)'),
    ('FDOT', 'Traffic Monitoring', 'https://www.fdot.gov/statistics/trafficinfo/default.shtm', 'Web', 'FDOT Traffic Monitoring Sites'),
    ('FDOT', 'Traffic Signal Locations', 'https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer', 'ArcGIS REST', 'FDOT Traffic Signal Locations'),
    ('City of Gainesville', 'Traffic Counts', 'https://data.cityofgainesville.org/resource/pfc3-w5ih.json', 'Socrata API', 'City of Gainesville Traffic Counts')
ON CONFLICT (agency, dataset_name) DO NOTHING;
