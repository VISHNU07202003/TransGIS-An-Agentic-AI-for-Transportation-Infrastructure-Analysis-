import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Base directory for data configs
DATA_DIR = Path(__file__).parent

FDOT_LAYER_KEYS = ['intersections', 'aadt', 'traffic_monitoring', 'traffic_signals']

def _load_json(filename: str) -> Dict[str, Any]:
    file_path = DATA_DIR / filename
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON in {file_path}: {e}")
        return {}

def get_fdot_config() -> Dict[str, Any]:
    return _load_json("fdot_layer_config.json")

def get_gainesville_config() -> Dict[str, Any]:
    return _load_json("gainesville_dataset_config.json")

def get_fdot_layer_url(layer_key: str) -> str:
    config = get_fdot_config()
    base_url = config.get("base_url", "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer")
    
    if layer_key == 'traffic_signals':
        return config.get("traffic_signals_service_url", "https://services1.arcgis.com/O1JpcwDW8sjYuddV/ArcGIS/rest/services/Traffic_Signal_Locations_TDA/FeatureServer/0")
        
    layers = config.get("layers", {})
    if layer_key in layers:
        layer_id = layers[layer_key].get("id")
        return f"{base_url}/{layer_id}"
        
    # Fallback to hardcoded ids if not found in config mapping
    layer_ids = {
        'intersections': 6,
        'aadt': 0,
        'portable_traffic_monitoring': 9,
        'telemetered_traffic_monitoring': 16,
    }
    
    layer_id = layer_ids.get(layer_key)
    if layer_id is not None:
        return f"{base_url}/{layer_id}"
        
    logger.warning(f"Layer key '{layer_key}' not found in FDOT config.")
    return base_url
