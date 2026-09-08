import json
import logging
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)

class FDOTClient:
    """Client for querying FDOT ArcGIS REST services."""
    
    def __init__(self, base_url: str = "https://gis.fdot.gov/arcgis/rest/services/RCI_Layers/FeatureServer"):
        self.base_url = base_url
        self._client = httpx.AsyncClient(timeout=30.0)
    
    async def query_layer(
        self,
        layer_url: str,
        where: str = "1=1",
        geometry: Optional[Dict[str, Any]] = None,
        geometry_type: str = "esriGeometryEnvelope",
        spatial_rel: str = "esriSpatialRelIntersects",
        in_sr: int = 4326,
        out_sr: int = 4326,
        out_fields: str = "*",
        return_geometry: bool = True,
        distance: Optional[float] = None,
        units: str = "esriSRUnit_Meter",
        result_record_count: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true" if return_geometry else "false",
            "outSR": out_sr,
            "f": "json"
        }
        
        if geometry:
            params["geometry"] = json.dumps(geometry)
            params["geometryType"] = geometry_type
            params["spatialRel"] = spatial_rel
            params["inSR"] = in_sr
            if distance is not None:
                params["distance"] = distance
                params["units"] = units

        if result_record_count is not None:
            params["resultRecordCount"] = result_record_count
            
        url = f"{layer_url}/query"
        
        for attempt in range(2):
            try:
                response = await self._client.post(url, data=params)
                response.raise_for_status()
                data = response.json()
                
                if "error" in data:
                    logger.error(f"ArcGIS REST API error: {data['error']}")
                    return {"features": []}
                    
                features = data.get("features", [])
                logger.info(f"Query to {url} returned {len(features)} features.")
                return data
            except httpx.HTTPError as e:
                logger.warning(f"HTTP error on attempt {attempt + 1} querying {url}: {e}")
                if attempt == 1:
                    logger.error(f"Failed to query {url} after retries.")
                    return {"features": []}
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON from {url}: {e}")
                return {"features": []}
                
        return {"features": []}
    
    def _get_url(self, layer_id: int) -> str:
        return f"{self.base_url}/{layer_id}"
        
    async def query_intersections_near(
        self, lat: float, lon: float, radius_m: float = 250
    ) -> List[Dict[str, Any]]:
        geometry = {"x": lon, "y": lat}
        data = await self.query_layer(
            layer_url=self._get_url(6), # Layer 6: Intersections
            geometry=geometry,
            geometry_type="esriGeometryPoint",
            distance=radius_m,
            units="esriSRUnit_Meter",
            in_sr=4326,
            out_sr=4326
        )
        return data.get("features", [])
    
    async def query_aadt_near(
        self, lat: float, lon: float, radius_m: float = 500
    ) -> List[Dict[str, Any]]:
        geometry = {"x": lon, "y": lat}
        data = await self.query_layer(
            layer_url=self._get_url(0), # Layer 0: AADT
            geometry=geometry,
            geometry_type="esriGeometryPoint",
            distance=radius_m,
            units="esriSRUnit_Meter",
            in_sr=4326,
            out_sr=4326
        )
        return data.get("features", [])
    
    async def query_traffic_monitoring_near(
        self, lat: float, lon: float, radius_m: float = 500
    ) -> List[Dict[str, Any]]:
        geometry = {"x": lon, "y": lat}
        portable_data = await self.query_layer(
            layer_url=self._get_url(9), # Layer 9: Portable Traffic Monitoring Sites
            geometry=geometry,
            geometry_type="esriGeometryPoint",
            distance=radius_m,
            units="esriSRUnit_Meter",
            in_sr=4326,
            out_sr=4326
        )
        telemetered_data = await self.query_layer(
            layer_url=self._get_url(16), # Layer 16: Telemetered Traffic Monitoring Sites
            geometry=geometry,
            geometry_type="esriGeometryPoint",
            distance=radius_m,
            units="esriSRUnit_Meter",
            in_sr=4326,
            out_sr=4326
        )
        
        return portable_data.get("features", []) + telemetered_data.get("features", [])
    
    async def query_traffic_signals_near(
        self, lat: float, lon: float, radius_m: float = 500  
    ) -> List[Dict[str, Any]]:
        tda_url = "https://services1.arcgis.com/O1JpcwDW8sjYuddV/ArcGIS/rest/services/Traffic_Signal_Locations_TDA/FeatureServer/0"
        geometry = {"x": lon, "y": lat}
        data = await self.query_layer(
            layer_url=tda_url,
            geometry=geometry,
            geometry_type="esriGeometryPoint",
            distance=radius_m,
            units="esriSRUnit_Meter",
            in_sr=4326,
            out_sr=4326
        )
        return data.get("features", [])
    
    async def close(self):
        await self._client.aclose()
