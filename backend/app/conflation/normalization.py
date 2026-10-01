import re
from typing import Optional, Tuple

DIR_MAP = {
    "N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST",
    "NW": "NORTHWEST", "NE": "NORTHEAST", "SW": "SOUTHWEST", "SE": "SOUTHEAST",
    "NORTH": "NORTH", "SOUTH": "SOUTH", "EAST": "EAST", "WEST": "WEST"
}

TYPE_MAP = {
    "ST": "STREET", "STREET": "STREET",
    "AVE": "AVENUE", "AVENUE": "AVENUE",
    "BLVD": "BOULEVARD", "BOULEVARD": "BOULEVARD",
    "RD": "ROAD", "ROAD": "ROAD",
    "DR": "DRIVE", "DRIVE": "DRIVE",
    "LN": "LANE", "LANE": "LANE",
    "PL": "PLACE", "PLACE": "PLACE",
    "WAY": "WAY",
    "TERR": "TERRACE", "TER": "TERRACE", "TERRACE": "TERRACE",
    "HWY": "HIGHWAY", "HIGHWAY": "HIGHWAY"
}

ROUTE_ALIASES = {
    "STATE ROAD": "SR", "ST RD": "SR",
    "STATE HWY": "SR", "STATE HIGHWAY": "SR",
    "US HIGHWAY": "US", "US HWY": "US",
    "CR": "CR", "COUNTY ROAD": "CR"
}

def normalize_street_name(name: str) -> Optional[str]:
    """
    Normalizes street names for entity matching.
    e.g., 'W University Ave' -> 'WEST UNIVERSITY AVENUE'
    'NW 13th St' -> 'NORTHWEST 13TH STREET'
    """
    if not name:
        return None
        
    name = name.upper().strip()
    
    # Remove punctuation
    name = re.sub(r'[.,]', '', name)
    
    tokens = name.split()
    if not tokens:
        return None
        
    normalized_tokens = []
    for i, token in enumerate(tokens):
        # Check directional at start or end
        if (i == 0 or i == len(tokens) - 1) and token in DIR_MAP:
            normalized_tokens.append(DIR_MAP[token])
            continue
            
        # Check street type at end
        if i > 0 and token in TYPE_MAP:
            normalized_tokens.append(TYPE_MAP[token])
            continue
            
        normalized_tokens.append(token)
        
    return " ".join(normalized_tokens)

def normalize_route_alias(route: str) -> Optional[str]:
    """
    Normalizes route designations.
    e.g., 'STATE ROAD 26' -> 'SR 26'
    """
    if not route:
        return None
        
    route = route.upper().strip()
    route = re.sub(r'[.,]', '', route)
    
    for alias, replacement in ROUTE_ALIASES.items():
        if route.startswith(alias + " "):
            route = route.replace(alias + " ", replacement + " ", 1)
            break
            
    # Remove extra spaces between prefix and number (e.g. SR  26 -> SR 26)
    route = re.sub(r'(SR|US|CR)\s+(\d+)', r'\1 \2', route)
    
    return route
