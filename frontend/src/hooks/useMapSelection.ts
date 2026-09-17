import { useRef, useState } from 'react';
import { api } from '../api/client';
import type { IntersectionCandidate, MapLocation } from '../types';
export function useMapSelection() {
  const [selectedLocation, setSelectedLocation] = useState<MapLocation | null>(null);
  const [candidates, setCandidates] = useState<IntersectionCandidate[]>([]);
  const [selectedIntersection, setSelectedIntersection] = useState<IntersectionCandidate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sequence = useRef(0);
  const selectLocation = async (lat: number, lng: number, source: 'map_click' | 'geocoder') => {
    const requestId = ++sequence.current;
    setSelectedLocation({ latitude: lat, longitude: lng, source });
    setSelectedIntersection(null); setCandidates([]); setError(null); setLoading(true);
    try {
      const fc = await api.nearbyIntersections(lat, lng);
      if (requestId !== sequence.current) return;
      const parsed = fc.features.flatMap(f => {
        if (f.geometry.type !== 'Point' || typeof f.properties?.id !== 'number') return [];
        return [{ id: f.properties.id, name: f.properties.name || 'Unnamed intersection', latitude: f.geometry.coordinates[1], longitude: f.geometry.coordinates[0], distance_m: f.properties.distance_m } as IntersectionCandidate];
      });
      setCandidates(parsed);
      if (parsed.length === 1) setSelectedIntersection(parsed[0]);
    } catch { if (requestId === sequence.current) setError('Intersection search is unavailable. Please try another point.'); }
    finally { if (requestId === sequence.current) setLoading(false); }
  };
  return { selectedLocation, candidates, selectedIntersection, selectLocation, selectIntersection: setSelectedIntersection, loading, error };
}
