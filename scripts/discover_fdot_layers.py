import os
import json
import httpx
from datetime import datetime, timezone

def discover_layers():
    base_url = "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer"
    signal_url = "https://services1.arcgis.com/O1JpcwDW8sjYuddV/ArcGIS/rest/services/Traffic_Signal_Locations_TDA/FeatureServer"
    
    print(f"Fetching layer list from {base_url} ...")
    
    layer_config = {
        "discovered_at": datetime.now(timezone.utc).isoformat(),
        "base_url": base_url,
        "layers": {}
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(f"{base_url}?f=json")
            resp.raise_for_status()
            data = resp.json()
            
            layers = data.get("layers", [])
            print(f"Found {len(layers)} layers in RCI.")
            
            # Map of target logical names to partial match strings
            targets = {
                "intersections": "intersection",
                "aadt": "annual average daily traffic",
                "traffic_monitoring": "traffic monitoring"
            }
            
            for layer in layers:
                lid = layer.get("id")
                name = layer.get("name", "")
                geom = layer.get("geometryType", "Unknown")
                
                print(f"[{lid}] {name} ({geom})")
                
                name_lower = name.lower()
                
                for target_key, search_str in targets.items():
                    if search_str in name_lower or (target_key == "aadt" and "aadt" in name_lower):
                        print(f"  -> Matched target: {target_key}")
                        
                        # fetch metadata
                        meta_resp = client.get(f"{base_url}/{lid}?f=json")
                        meta_resp.raise_for_status()
                        meta_data = meta_resp.json()
                        
                        fields = [{"name": f["name"], "type": f["type"], "alias": f.get("alias", "")} for f in meta_data.get("fields", [])]
                        
                        layer_config["layers"][target_key] = {
                            "id": lid,
                            "name": name,
                            "geometry_type": geom,
                            "fields": fields
                        }
            
            # Check traffic signals separately
            print(f"\nChecking separate traffic signal service at {signal_url} ...")
            try:
                sig_resp = client.get(f"{signal_url}?f=json")
                sig_resp.raise_for_status()
                sig_data = sig_resp.json()
                sig_layers = sig_data.get("layers", [])
                for sl in sig_layers:
                    if "signal" in sl.get("name", "").lower():
                        slid = sl.get("id")
                        s_name = sl.get("name", "")
                        
                        smeta_resp = client.get(f"{signal_url}/{slid}?f=json")
                        smeta_resp.raise_for_status()
                        smeta_data = smeta_resp.json()
                        s_geom = smeta_data.get("geometryType", "Unknown")
                        s_fields = [{"name": f["name"], "type": f["type"], "alias": f.get("alias", "")} for f in smeta_data.get("fields", [])]
                        
                        layer_config["layers"]["traffic_signals"] = {
                            "id": slid,
                            "name": s_name,
                            "geometry_type": s_geom,
                            "fields": s_fields,
                            "url": signal_url
                        }
                        print(f"  -> Matched target: traffic_signals (Layer {slid})")
                        break
            except Exception as e:
                print(f"Error checking traffic signals: {e}")

    except Exception as e:
        print(f"Error querying base URL: {e}")
        return

    # Create directories if they don't exist
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', 'app', 'data')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'fdot_layer_config.json')
    
    with open(out_file, 'w') as f:
        json.dump(layer_config, f, indent=2)
        
    print(f"\nSaved config to {out_file}")

if __name__ == '__main__':
    discover_layers()
