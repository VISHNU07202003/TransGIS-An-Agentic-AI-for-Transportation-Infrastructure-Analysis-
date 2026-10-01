import { useEffect, useRef, useState } from 'react';
import { ArrowRight, CornerDownLeft, Loader2, MapPin, Search, X } from 'lucide-react';
import { api } from '../api/client';
import type { PlaceResult } from '../types';

interface Props {
  onLocationSelect: (lat: number, lng: number) => void;
  bias?: { latitude: number; longitude: number } | null;
}
export default function SearchBar({ onLocationSelect, bias }: Props) {
  const [address, setAddress] = useState('');
  const [results, setResults] = useState<PlaceResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const [searched, setSearched] = useState(false);
  const wrapper = useRef<HTMLDivElement>(null);
  const controller = useRef<AbortController | null>(null);
  const version = useRef(0);
  const lat = bias?.latitude ?? 29.6516;
  const lon = bias?.longitude ?? -82.3248;

  useEffect(() => {
    if (open && active >= 0) wrapper.current?.querySelector('#place-option-' + active)?.scrollIntoView({ block: 'nearest' });
  }, [active, open]);

  const lookup = async (query: string) => {
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    const requestId = ++version.current;
    setLoading(true); setError(null); setSearched(false);
    try {
      const matches = await api.searchPlaces(query, lat, lon, current.signal);
      if (current.signal.aborted || requestId !== version.current) return;
      setResults(matches); setActive(-1); setSearched(true);
    } catch {
      if (!current.signal.aborted && requestId === version.current) {
        setResults([]); setError('Search is unavailable. Try again or choose a point on the map.');
      }
    } finally {
      if (!current.signal.aborted && requestId === version.current) setLoading(false);
    }
  };

  useEffect(() => {
    if (!open || address.trim().length < 3) { setLoading(false); return; }
    const timer = setTimeout(() => void lookup(address.trim()), 500);
    return () => { clearTimeout(timer); controller.current?.abort(); };
  }, [address, lat, lon, open]);

  useEffect(() => {
    const dismiss = (event: PointerEvent) => {
      if (!wrapper.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener('pointerdown', dismiss);
    return () => { document.removeEventListener('pointerdown', dismiss); controller.current?.abort(); };
  }, []);

  const choose = (place: PlaceResult) => {
    version.current++; controller.current?.abort();
    setAddress(place.display_name); setOpen(false); setLoading(false); setError(null);
    onLocationSelect(place.latitude, place.longitude);
  };
  const change = (value: string) => {
    version.current++; controller.current?.abort();
    setAddress(value); setResults([]); setActive(-1); setError(null);
    setSearched(false); setLoading(false); setOpen(true);
  };
  return (
    <div ref={wrapper} className="place-search" onBlur={e => {
      if (!e.currentTarget.contains(e.relatedTarget as Node)) setOpen(false);
    }}>
      <form className="search-form" onSubmit={e => {
        e.preventDefault();
        if (active >= 0 && results[active]) choose(results[active]);
        else if (results.length === 1) choose(results[0]);
        else if (address.trim().length >= 3) { setOpen(true); void lookup(address.trim()); }
      }}>
        <Search size={19} />
        <input role="combobox" aria-label="Search an address or city" aria-autocomplete="list"
          aria-expanded={open} aria-controls="place-options"
          aria-activedescendant={open && active >= 0 ? 'place-option-' + active : undefined}
          value={address} onChange={e => change(e.target.value)} onFocus={() => setOpen(true)}
          placeholder="Search an address, street, or city…" autoComplete="off"
          onKeyDown={e => {
            if (e.key === 'Escape') { setOpen(false); setActive(-1); }
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
              e.preventDefault(); setOpen(true);
              if (results.length) setActive(i => e.key === 'ArrowDown' ? (i + 1) % results.length : (i <= 0 ? results.length - 1 : i - 1));
            }
          }} />
        {address && <button className="search-clear" type="button" aria-label="Clear address" onClick={() => change('')}><X size={15} /></button>}
        <button className="search-submit" type="submit" disabled={loading || address.trim().length < 3} aria-label="Find places">
          {loading ? <Loader2 className="spinning" size={18} /> : <ArrowRight size={19} />}
        </button>
      </form>
      {open && <div className="search-dropdown">
        <div className="suggestion-heading"><span>{results.length ? 'MATCHING PLACES' : 'FIND YOUR NEXT LOCATION'}</span><span>↑ ↓ to navigate</span></div>
        <div role="listbox" id="place-options" aria-label="Place suggestions">
          {results.map((place, i) => <button type="button" role="option" aria-selected={i === active}
            tabIndex={-1} id={'place-option-' + i} key={place.display_name + place.latitude + place.longitude}
            className={'place-option ' + (i === active ? 'active' : '')}
            onPointerDown={e => e.preventDefault()} onClick={() => choose(place)}>
            <span className="suggestion-icon"><MapPin size={17} /></span>
            <span><strong>{place.name}</strong><small>{place.display_name}</small></span><CornerDownLeft size={14} />
          </button>)}
        </div>
        <div className="search-feedback" role="status">
          {loading ? 'Finding places…' : error || (address.trim().length < 3 ? 'Type at least 3 characters. Try “Ocala” or “University Avenue”.' : searched && !results.length ? 'No matching places. Try a city name or a fuller address.' : !results.length ? 'Waiting for your search…' : 'Select a place to move the pin.')}
        </div>
        <div className="search-attribution">Place search by <a href="https://photon.komoot.io/" target="_blank" rel="noopener noreferrer">Photon</a> · OpenStreetMap</div>
      </div>}
    </div>
  );
}

