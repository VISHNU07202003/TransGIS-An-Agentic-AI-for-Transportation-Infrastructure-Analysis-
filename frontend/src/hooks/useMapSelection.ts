import { useState } from 'react';
import { api } from '../api/client';
import type { IntersectionCandidate, MapLocation } from '../types';

export function useMapSelection() {
  const [selectedLocation, setSelectedLocation] = useState<MapLocation | null>(null);
  const [candidates, setCandidates] = useState<IntersectionCandidate[]>([]);
  const [selectedIntersection, setSelectedIntersection] = useState<IntersectionCandidate | null>(null);
  const [loading, setLoading] = useState(false);

  const selectLocation = async (lat: number, lng: number, source: 'map_click' | 'geocoder') => {
    setSelectedLocation({ latitude: lat, longitude: lng, source });
    setSelectedIntersection(null);
    setLoading(true);
    try {
      const fc = await api.nearbyIntersections(lat, lng);
      const parsedCandidates = fc.features.map(f => ({
        id: f.properties?.id,
        name: f.properties?.name || 'Unknown',
        latitude: (f.geometry as any).coordinates[1],
        longitude: (f.geometry as any).coordinates[0],
        distance_m: f.properties?.distance_m || 0
      })) as IntersectionCandidate[];
      setCandidates(parsedCandidates);
    } catch (e) {
      console.error(e);
      setCandidates([]);
    } finally {
      setLoading(false);
    }
  };

  const selectIntersection = (candidate: IntersectionCandidate) => {
    setSelectedIntersection(candidate);
  };

  return {
    selectedLocation,
    candidates,
    selectedIntersection,
    selectLocation,
    selectIntersection,
    loading
  };
}
