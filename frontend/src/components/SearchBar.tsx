import { useState } from 'react';
import { api } from '../api/client';

interface SearchBarProps {
  onSearch: (address: string) => void;
  onLocationSelect: (lat: number, lng: number) => void;
}

export default function SearchBar({ onSearch, onLocationSelect }: SearchBarProps) {
  const [address, setAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!address.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await api.geocode(address);
      onLocationSelect(res.latitude, res.longitude);
      onSearch(address);
    } catch (err) {
      setError('Geocoding failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="search-bar" onSubmit={handleSearch}>
      <input
        type="text"
        value={address}
        onChange={(e) => setAddress(e.target.value)}
        placeholder="Search address..."
        disabled={loading}
      />
      <button type="submit" disabled={loading || !address.trim()}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      {error && <span className="error-text">{error}</span>}
    </form>
  );
}
