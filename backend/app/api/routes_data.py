from fastapi import APIRouter
from typing import List, Dict, Any
from app.data.source_registry import get_fdot_config, get_gainesville_config

router = APIRouter(prefix="/api/data")

@router.get("/sources")
def get_data_sources() -> List[Dict[str, Any]]:
    """List registered authoritative transportation data sources."""
    fdot_conf = get_fdot_config()
    gnv_conf = get_gainesville_config()
    
    sources = [
        {
            "agency": "Florida Department of Transportation (FDOT)",
            "dataset_name": "RCI Intersections",
            "source_type": "ArcGIS FeatureServer (Layer 6)",
            "source_url": "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/6",
            "description": "Statewide roadway inventory of intersecting roadways and physical configurations.",
            "status": "active"
        },
        {
            "agency": "Florida Department of Transportation (FDOT)",
            "dataset_name": "Annual Average Daily Traffic (AADT)",
            "source_type": "ArcGIS FeatureServer (Layer 0)",
            "source_url": "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/0",
            "description": "Annual average daily traffic volumes and factor groups on state highway system corridors.",
            "status": "active"
        },
        {
            "agency": "Florida Department of Transportation (FDOT)",
            "dataset_name": "Traffic Monitoring Sites",
            "source_type": "ArcGIS FeatureServer (Layers 9 & 16)",
            "source_url": "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer/16",
            "description": "Telemetered and portable continuous traffic monitoring stations.",
            "status": "active"
        },
        {
            "agency": "Florida Department of Transportation (FDOT)",
            "dataset_name": "Traffic Signal Locations",
            "source_type": "ArcGIS FeatureServer",
            "source_url": "https://services1.arcgis.com/O1JpcwDW8sjYuddV/ArcGIS/rest/services/Traffic_Signal_Locations_TDA/FeatureServer/0",
            "description": "Inventory of traffic control signals on and off state roadway system.",
            "status": "active"
        },
        {
            "agency": "City of Gainesville Public Works",
            "dataset_name": gnv_conf.get("name", "Traffic Counts"),
            "source_type": "Socrata SODA Open Data API",
            "source_url": gnv_conf.get("resource_url", "https://data.cityofgainesville.org/resource/v2qq-gus2.json"),
            "description": gnv_conf.get("description", "Selected attributes and spatial locations of traffic count sites in the City of Gainesville."),
            "status": "active"
        }
    ]
    return sources

@router.get("/traffic-sites/{site_id}/observations")
def get_traffic_observations(site_id: str):
    """Retrieve observations for a specific traffic site."""
    return {
        "site_id": site_id,
        "observations": []
    }
