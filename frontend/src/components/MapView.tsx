import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Navigation, Layers, Compass } from "lucide-react";
import type { IntersectionCandidate, MapFeature, MapLocation } from "../types";

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
  selectedLocation,
}: MapViewProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const currentMarkers = useRef<maplibregl.Marker[]>([]);

  useEffect(() => {
    if (!mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style:
        import.meta.env.VITE_MAP_STYLE_URL ||
        "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
      center: [-82.3248, 29.6516], // Gainesville, FL
      zoom: 13.5,
      pitch: 30,
    });

    map.current.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");

    map.current.on("click", (e) => {
      onMapClick(e.lngLat.lat, e.lngLat.lng);
    });

    return () => {
      map.current?.remove();
    };
  }, []);

  useEffect(() => {
    if (!map.current) return;

    currentMarkers.current.forEach((marker) => marker.remove());
    currentMarkers.current = [];

    // Clicked / Geocoded target point
    if (selectedLocation) {
      const el = document.createElement("div");
      el.className = "relative flex items-center justify-center";
      el.innerHTML = `
        <div class="absolute w-8 h-8 bg-red-500/20 rounded-full animate-ping"></div>
        <div class="relative w-4 h-4 bg-red-500 border-2 border-white rounded-full shadow-lg"></div>
      `;

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([selectedLocation.longitude, selectedLocation.latitude])
        .setPopup(
          new maplibregl.Popup({ offset: 15 }).setHTML(`
            <div style="font-family: sans-serif; font-size: 11px;">
              <strong style="color: #38bdf8;">Query Point</strong><br/>
              ${selectedLocation.latitude.toFixed(5)}, ${selectedLocation.longitude.toFixed(5)}
            </div>
          `)
        )
        .addTo(map.current);
      currentMarkers.current.push(marker);

      map.current.flyTo({
        center: [selectedLocation.longitude, selectedLocation.latitude],
        zoom: 14.5,
        speed: 1.2,
      });
    }

    // Candidate intersections
    markers.forEach((candidate) => {
      const isSelected = selectedIntersection?.id === candidate.id;
      const el = document.createElement("div");
      el.className = "cursor-pointer group";

      if (isSelected) {
        el.innerHTML = `
          <div class="relative flex items-center justify-center">
            <div class="absolute w-10 h-10 bg-cyan-400/30 rounded-full animate-ping"></div>
            <div class="relative px-2.5 py-1 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold text-[10px] rounded-full shadow-xl border border-white flex items-center gap-1">
              <span>?</span>
              <span>${candidate.name}</span>
            </div>
          </div>
        `;
      } else {
        el.innerHTML = `
          <div class="w-3.5 h-3.5 bg-cyan-400/80 hover:bg-cyan-300 border border-slate-900 rounded-full shadow-md transition-transform transform group-hover:scale-125"></div>
        `;
      }

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([candidate.longitude, candidate.latitude])
        .setPopup(
          new maplibregl.Popup({ offset: 15 }).setHTML(`
            <div style="font-family: sans-serif; font-size: 11px;">
              <strong style="color: #38bdf8;">Intersection #${candidate.id}</strong><br/>
              <strong>${candidate.name}</strong><br/>
              <span style="color: #94a3b8;">${Math.round(candidate.distance_m)}m from click</span>
            </div>
          `)
        )
        .addTo(map.current!);
      currentMarkers.current.push(marker);
    });
  }, [markers, selectedIntersection, selectedLocation]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />

      {/* Modern floating badge */}
      <div className="absolute top-4 left-4 z-10 bg-slate-950/80 backdrop-blur-md border border-slate-800/80 px-3 py-1.5 rounded-xl text-xs text-slate-300 flex items-center gap-2 shadow-xl">
        <Compass className="w-3.5 h-3.5 text-cyan-400 animate-spin-slow" />
        <span className="font-medium">Gainesville Urban Transport Grid</span>
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
      </div>

      <div className="absolute bottom-4 left-4 z-10 bg-slate-950/80 backdrop-blur-md border border-slate-800/80 px-3 py-1.5 rounded-xl text-[11px] text-slate-400 flex items-center gap-3 shadow-xl">
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block"></span> Selected Point
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span> FDOT Intersections
        </span>
      </div>
    </div>
  );
}

