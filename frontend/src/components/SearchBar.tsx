import { useState } from 'react';
import { ArrowRight, Loader2, Search, X } from 'lucide-react';
import { api } from '../api/client';
export default function SearchBar({ onLocationSelect }: { onLocationSelect: (lat: number, lng: number) => void }) {
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const search = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!address.trim() || loading) return;
    setLoading(true); setError(null);
    try {
      const result = await api.geocode(address);
      if (result.confidence === 0) throw new Error('Location could not be verified. Try a more specific address.');
      onLocationSelect(result.latitude, result.longitude);
    } catch { setError('Location could not be verified. Try another address or click the map.'); }
    finally { setLoading(false); }
  };
  return <div><form className="search-form" onSubmit={search}><Search size={19} /><input aria-label="Search a Gainesville address" value={address} onChange={e => setAddress(e.target.value)} placeholder="Search a Gainesville address…" disabled={loading} />{address && <button className="search-clear" type="button" aria-label="Clear address" onClick={() => { setAddress(''); setError(null); }}><X size={15} /></button>}<button className="search-submit" type="submit" disabled={loading || !address.trim()} aria-label="Find address">{loading ? <Loader2 className="spinning" size={18} /> : <ArrowRight size={19} />}</button></form>{error && <p className="search-error" role="alert">{error}</p>}</div>;
}

