"""Tool schemas for NaviGator function calling."""

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_nearby_intersections",
            "description": "Find authoritative FDOT intersections near a coordinate. Use this when the user provides a location and you need to identify which intersection(s) they are referring to.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "description": "Latitude of the location"},
                    "longitude": {"type": "number", "description": "Longitude of the location"},
                    "radius_m": {"type": "number", "minimum": 25, "maximum": 2000, "description": "Search radius in meters (default 250)"}
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_intersection_details",
            "description": "Retrieve detailed properties of a specific intersection given its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intersection_id": {"type": "string", "description": "The unique ID of the intersection"}
                },
                "required": ["intersection_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_nearby_traffic_sites",
            "description": "Find traffic monitoring sites near a specific intersection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intersection_id": {"type": "string", "description": "The unique ID of the intersection"},
                    "radius_m": {"type": "number", "minimum": 25, "maximum": 5000, "description": "Search radius in meters (default 500)"}
                },
                "required": ["intersection_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_hourly_traffic_volume",
            "description": "Get hourly traffic volume for a specific traffic monitoring site over a time range on a given date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_id": {"type": "string", "description": "The unique ID of the traffic monitoring site"},
                    "date": {"type": "string", "description": "The date for the query (YYYY-MM-DD format)"},
                    "start_time": {"type": "string", "description": "Start time in HH:MM format (optional, default 00:00)"},
                    "end_time": {"type": "string", "description": "End time in HH:MM format (optional, default 23:59)"}
                },
                "required": ["site_id", "date"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_signal_information",
            "description": "Get traffic signal hardware/timing information for an intersection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intersection_id": {"type": "string", "description": "The unique ID of the intersection"}
                },
                "required": ["intersection_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_aadt_near_intersection",
            "description": "Get Annual Average Daily Traffic (AADT) data near an intersection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intersection_id": {"type": "string", "description": "The unique ID of the intersection"}
                },
                "required": ["intersection_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_available_data",
            "description": "Check what data sets (signals, traffic volume, AADT) are available near an intersection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "intersection_id": {"type": "string", "description": "The unique ID of the intersection"}
                },
                "required": ["intersection_id"],
                "additionalProperties": False
            }
        }
    }
]
