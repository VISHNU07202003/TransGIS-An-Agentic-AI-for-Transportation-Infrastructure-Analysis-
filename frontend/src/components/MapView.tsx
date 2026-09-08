import { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import type { IntersectionCandidate, MapFeature, MapLocation } from '../types';

interface MapViewProps {
  onMapClick: (lat: number, lng: number) => void;
  markers?: IntersectionCandidate[];
  selectedIntersection?: IntersectionCandidate | null;
  mapFeatures?: MapFeature[];
  selectedLocation?: MapLocation | null;
}

export default function MapView({ 
  onMapClick, 
  markers = [], 
  selectedIntersection,
  mapFeatures = [],
  selectedLocation 
}: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const currentMarkers = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (!mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: import.meta.env.VITE_MAP_STYLE_URL || 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [-82.3248, 29.6516],
      zoom: 13,
    });

    map.current.on('click', (e) => {
      onMapClick(e.lngLat.lat, e.lngLat.lng);
    });

    return () => {
      map.current?.remove();
    };
  }, []);

  useEffect(() => {
    if (!map.current) return;

    currentMarkers.current.forEach(marker => marker.remove());
    currentMarkers.current = [];

    if (selectedLocation) {
      const marker = new maplibregl.Marker({ color: 'red' })
        .setLngLat([selectedLocation.longitude, selectedLocation.latitude])
        .addTo(map.current);
      currentMarkers.current.push(marker);
    }

    markers.forEach(candidate => {
      const isSelected = selectedIntersection?.id === candidate.id;
      const marker = new maplibregl.Marker({ color: isSelected ? 'green' : 'blue' })
        .setLngLat([candidate.longitude, candidate.latitude])
        .addTo(map.current!);
      currentMarkers.current.push(marker);
    });

  }, [markers, selectedIntersection, selectedLocation]);

  return <div ref={mapContainer} className="map-view" />;
}
