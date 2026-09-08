import logging
from typing import Any, Dict, List, Optional, Tuple
import httpx

logger = logging.getLogger(__name__)

class GainesvilleClient:
    """Client for querying City of Gainesville open data (Socrata SODA API)."""
    
    def __init__(
        self,
        base_url: str = "https://data.cityofgainesville.org",
        dataset_id: str = "v2qq-gus2",
    ):
        self.base_url = base_url
        self.dataset_id = dataset_id
        self.resource_url = f"{base_url}/resource/{dataset_id}.json"
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def get_traffic_sites(
        self, 
        bbox: Optional[Tuple[float, float, float, float]] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        params = {"$limit": limit}
        
        if bbox:
            south, west, north, east = bbox
            params["$where"] = f"within_box(the_geom, {south}, {west}, {north}, {east})"
            
        try:
            response = await self._client.get(self.resource_url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved {len(data)} traffic sites from Gainesville data.")
            return data
        except httpx.HTTPError as e:
            logger.error(f"HTTP error retrieving Gainesville traffic sites: {e}")
            return []
    
    async def get_traffic_sites_near(
        self, lat: float, lon: float, radius_m: float = 500
    ) -> List[Dict[str, Any]]:
        params = {
            "$where": f"within_circle(the_geom, {lat}, {lon}, {radius_m})"
        }
        
        try:
            response = await self._client.get(self.resource_url, params=params)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Retrieved {len(data)} nearby traffic sites from Gainesville data.")
            return data
        except httpx.HTTPError as e:
            logger.error(f"HTTP error retrieving nearby Gainesville traffic sites: {e}")
            return []
    
    async def get_metadata(self) -> Dict[str, Any]:
        from .source_registry import get_gainesville_config
        return get_gainesville_config()
    
    async def close(self):
        await self._client.aclose()
