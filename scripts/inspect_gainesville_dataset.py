import httpx
import json
import datetime
import os
from pathlib import Path

# Paths
BASE_DIR = Path(r"v:\MASTER'S\Sem 3\individual study\agentic-transportation-analysis")
CONFIG_PATH = BASE_DIR / "backend" / "app" / "data" / "gainesville_dataset_config.json"

DATASET_ID = "pfc3-w5ih"
BASE_URL = "https://data.cityofgainesville.org"
METADATA_URL = f"{BASE_URL}/api/views/{DATASET_ID}.json"
DATA_URL = f"{BASE_URL}/resource/{DATASET_ID}.json"

def categorize_field(name, datatype):
    name_lower = name.lower()
    if 'lat' in name_lower or 'lon' in name_lower or datatype == 'point' or 'location' in name_lower:
        return 'geometry'
    elif 'count' in name_lower or 'volume' in name_lower or 'aadt' in name_lower:
        return 'count'
    elif 'id' in name_lower or 'site' in name_lower or 'station' in name_lower:
        return 'identifier'
    elif 'date' in name_lower or 'time' in name_lower or 'year' in name_lower or datatype == 'calendar_date':
        return 'time'
    else:
        return 'other'

def main():
    print(f"Fetching metadata from {METADATA_URL}")
    try:
        with httpx.Client(timeout=10.0) as client:
            meta_resp = client.get(METADATA_URL)
            meta_resp.raise_for_status()
            metadata = meta_resp.json()
            
            data_resp = client.get(DATA_URL, params={"$limit": 5})
            data_resp.raise_for_status()
            data_sample = data_resp.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    name = metadata.get("name", "Unknown")
    description = metadata.get("description", "No description")
    columns_info = metadata.get("columns", [])
    
    # Try to get row count from metadata if available
    try:
        with httpx.Client(timeout=10.0) as client:
            count_resp = client.get(DATA_URL, params={"$select": "count(*)"})
            count_resp.raise_for_status()
            row_count = int(count_resp.json()[0].get('count', 0))
    except Exception:
        row_count = 0
    
    print(f"\n--- Dataset Info ---")
    print(f"Name: {name}")
    print(f"Description: {description}")
    print(f"Row Count: {row_count}")
    
    columns_config = []
    field_mapping = {
        "geometry_fields": [],
        "count_fields": [],
        "identifier_fields": [],
        "time_fields": []
    }
    
    print("\n--- Columns ---")
    for col in columns_info:
        col_name = col.get("fieldName", "")
        col_datatype = col.get("dataTypeName", "")
        col_desc = col.get("description", "")
        
        # Skip some internal socrata columns starting with :
        if col_name.startswith(':'):
            continue
            
        category = categorize_field(col_name, col_datatype)
        
        if category == 'geometry':
            field_mapping["geometry_fields"].append(col_name)
        elif category == 'count':
            field_mapping["count_fields"].append(col_name)
        elif category == 'identifier':
            field_mapping["identifier_fields"].append(col_name)
        elif category == 'time':
            field_mapping["time_fields"].append(col_name)
            
        columns_config.append({
            "name": col_name,
            "datatype": col_datatype,
            "description": col_desc,
            "field_category": category
        })
        print(f"- {col_name} ({col_datatype}) -> Category: {category}")
        
    config = {
        "discovered_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "dataset_id": DATASET_ID,
        "base_url": BASE_URL,
        "name": name,
        "description": description,
        "row_count": row_count,
        "columns": columns_config,
        "field_mapping": field_mapping
    }
    
    print("\n--- Data Sample ---")
    print(json.dumps(data_sample, indent=2))
    
    os.makedirs(CONFIG_PATH.parent, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        
    print(f"\nSaved config to {CONFIG_PATH}")
    
if __name__ == "__main__":
    main()
