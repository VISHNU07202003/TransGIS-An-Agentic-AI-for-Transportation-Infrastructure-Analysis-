export interface MapLocation {
  latitude: number;
  longitude: number;
  source: 'map_click' | 'geocoder';
}

export interface IntersectionCandidate {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  distance_m: number;
}

export interface Provenance {
  agency: string;
  dataset: string;
  source_url: string;
  record_id?: string;
  observation_date?: string;
  retrieval_timestamp: string;
  spatial_relation?: string;
}

export interface TrafficResult {
  value?: number;
  unit: string;
  result_type: 'DIRECT_OBSERVATION' | 'NEARBY_OBSERVATION' | 'DERIVED_FROM_SOURCE_DATA' | 'UNAVAILABLE';
  provenance?: Provenance;
  message?: string;
}

export interface MapFeature {
  type: string;
  geometry: {
    type: string;
    coordinates: number[] | number[][] | number[][][];
  };
  properties: Record<string, unknown>;
}

export interface ChatRequest {
  message: string;
  location?: MapLocation;
  selected_intersection_id?: number;
  conversation_id?: string;
}

export interface ChatResponse {
  status: 'answer' | 'needs_clarification' | 'no_data' | 'error';
  message: string;
  result?: TrafficResult;
  candidates?: IntersectionCandidate[];
  map_features?: MapFeature[];
  conversation_id?: string;
}

export interface GeocodeResult {
  latitude: number;
  longitude: number;
  display_name: string;
  confidence?: number;
}

export interface HealthStatus {
  status: string;
  database: string;
  fdot: string;
  gainesville: string;
  navigator: string;
}
