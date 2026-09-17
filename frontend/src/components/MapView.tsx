import { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { Crosshair, Layers, Minus, Plus } from 'lucide-react';
import type { IntersectionCandidate, MapFeature, MapLocation } from '../types';
interface Props { onMapClick: (lat: number, lng: number) => void; markers?: IntersectionCandidate[]; selectedIntersection?: IntersectionCandidate | null; mapFeatures?: MapFeature[]; selectedLocation?: MapLocation | null; onCandidateSelect: (candidate: IntersectionCandidate) => void; }
export default function MapView({ onMapClick, markers = [], selectedIntersection, selectedLocation, onCandidateSelect }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const callbacks = useRef({ onMapClick, onCandidateSelect });
  callbacks.current = { onMapClick, onCandidateSelect };
  const [showMarkers, setShowMarkers] = useState(true);
  const [mapError, setMapError] = useState(false);
  useEffect(() => {
    if (!container.current) return;
    let instance: maplibregl.Map;
    try {
      instance = new maplibregl.Map({ container: container.current, style: import.meta.env.VITE_MAP_STYLE_URL || 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json', center: [-82.3448, 29.6516], zoom: 12.7, attributionControl: {} });
    } catch { setMapError(true); return; }
    map.current = instance;
    instance.on('click', e => callbacks.current.onMapClick(e.lngLat.lat, e.lngLat.lng));
    instance.on('error', () => setMapError(true));
    instance.on('idle', () => { if (instance.areTilesLoaded()) setMapError(false); });
    const observer = new ResizeObserver(() => instance.resize());
    observer.observe(container.current);
    return () => { observer.disconnect(); instance.remove(); map.current = null; };
  }, []);
  useEffect(() => {
    if (!map.current || !selectedLocation) return;
    map.current.flyTo({ center: [selectedLocation.longitude, selectedLocation.latitude], zoom: 15, duration: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 700 });
  }, [selectedLocation]);
  useEffect(() => {
    if (!map.current) return;
    const created: maplibregl.Marker[] = [];
    if (selectedLocation) {
      const el = document.createElement('div'); el.className = 'query-marker'; el.setAttribute('aria-label', 'Selected query point');
      created.push(new maplibregl.Marker({ element: el }).setLngLat([selectedLocation.longitude, selectedLocation.latitude]).addTo(map.current));
    }
    if (showMarkers) markers.forEach((candidate, i) => {
      const el = document.createElement('button');
      el.className = 'intersection-marker' + (selectedIntersection?.id === candidate.id ? ' is-selected' : '');
      el.type = 'button'; el.textContent = String(i + 1); el.title = candidate.name; el.setAttribute('aria-label', 'Select ' + candidate.name);
      el.addEventListener('click', e => { e.stopPropagation(); callbacks.current.onCandidateSelect(candidate); });
      created.push(new maplibregl.Marker({ element: el }).setLngLat([candidate.longitude, candidate.latitude]).addTo(map.current!));
    });
    return () => created.forEach(marker => marker.remove());
  }, [markers, selectedIntersection, selectedLocation, showMarkers]);
  return <div className="map-surface"><div ref={container} className="map-canvas" />{mapError && <div className="map-error" role="status">Map tiles are unavailable. Address search is still available.</div>}<div className="map-controls"><button onClick={() => map.current?.zoomIn()} aria-label="Zoom in"><Plus size={19} /></button><button onClick={() => map.current?.zoomOut()} aria-label="Zoom out"><Minus size={19} /></button><span /><button onClick={() => map.current?.flyTo({ center: [-82.3248, 29.6516], zoom: 13, duration: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 700 })} aria-label="Recenter on Gainesville"><Crosshair size={19} /></button></div><button className={'layers-button ' + (showMarkers ? 'enabled' : '')} onClick={() => setShowMarkers(v => !v)} aria-pressed={showMarkers}><Layers size={16} /> Intersections</button></div>;
}

