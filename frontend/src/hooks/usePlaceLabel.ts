import { useEffect, useState } from 'react';
import { api } from '../api/client';

export function usePlaceLabel(point: { latitude: number; longitude: number } | null) {
  const lat = point?.latitude;
  const lon = point?.longitude;
  const key = point ? `${lat},${lon}` : '';
  const [resolved, setResolved] = useState({ key: '', label: '', address: '' });
  const [failedKey, setFailedKey] = useState('');
  useEffect(() => {
    if (lat === undefined || lon === undefined) return;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      api.reversePlace(lat, lon, controller.signal).then(place => {
        if (!controller.signal.aborted) setResolved({ key, label: place.locality, address: place.display_name });
      }).catch(() => { if (!controller.signal.aborted) setFailedKey(key); });
    }, 350);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [lat, lon, key]);
  if (!point) return { label: 'Gainesville, Florida', address: 'Choose a point to explore', loading: false };
  if (resolved.key === key) return { label: resolved.label, address: resolved.address, loading: false };
  return { label: failedKey === key ? 'Selected pin' : 'Locating pin…', address: `${point.latitude.toFixed(5)}, ${point.longitude.toFixed(5)}`, loading: failedKey !== key };
}
