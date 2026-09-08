import type { ChatRequest, ChatResponse, GeocodeResult, HealthStatus } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API error ${response.status}: ${error}`);
  }
  return response.json();
}

export const api = {
  health: () => request<HealthStatus>('/health'),

  chat: (req: ChatRequest) =>
    request<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(req),
    }),

  nearbyIntersections: (lat: number, lon: number, radiusM = 250) =>
    request<GeoJSON.FeatureCollection>(
      `/api/intersections/nearby?lat=${lat}&lon=${lon}&radius_m=${radiusM}`
    ),

  intersectionDetails: (id: number) =>
    request<GeoJSON.Feature>(`/api/intersections/${id}`),

  trafficSites: (intersectionId: number, radiusM = 500) =>
    request<GeoJSON.FeatureCollection>(
      `/api/intersections/${intersectionId}/traffic-sites?radius_m=${radiusM}`
    ),

  geocode: (address: string) =>
    request<GeocodeResult>(`/api/geocode?address=${encodeURIComponent(address)}`),
};
