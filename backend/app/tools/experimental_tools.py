"""
Experimental tool implementations for Systems A, B, and C.
These are strictly read-only and designed to expose different abstraction layers.
"""

class SystemATools:
    @staticmethod
    def search_fdot_aadt(roadway_id: str = None, route_name: str = None):
        """Query raw FDOT ArcGIS REST API abstraction."""
        pass
        
    @staticmethod
    def search_gainesville_counts(station_id: str = None, street_name: str = None):
        """Query raw Gainesville Socrata GeoJSON abstraction."""
        pass

class SystemBTools:
    @staticmethod
    def search_source_features_by_name(normalized_name: str):
        """Query normalized PostGIS DB for features matching a normalized road name."""
        pass
        
    @staticmethod
    def nearby_source_features(lat: float, lon: float, radius_m: float = 50.0):
        """Query normalized PostGIS DB using ST_DWithin for nearby records from any provider."""
        pass
        
    @staticmethod
    def get_source_observations(source_feature_id: str):
        """Retrieve traffic observations for a specific raw source feature."""
        pass

class SystemCTools:
    @staticmethod
    def resolve_location(name: str, intersect_name: str = None):
        """Uses the frozen ER layer and NLP to return candidate canonical IDs."""
        pass
        
    @staticmethod
    def get_canonical_entity(canonical_id: str):
        """Retrieves canonical node or edge properties."""
        pass
        
    @staticmethod
    def get_observations(canonical_id: str):
        """Retrieves all associated observations across all providers via the association_groups schema."""
        pass
        
    @staticmethod
    def get_entity_sources(canonical_id: str):
        """Retrieves provenance records associated with this canonical entity."""
        pass
