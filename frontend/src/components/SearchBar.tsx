import { useState } from "react";
import { Search, Loader2, MapPin, X } from "lucide-react";
import { api } from "../api/client";

interface SearchBarProps {
  onSearch: (address: string) => void;
  onLocationSelect: (lat: number, lng: number) => void;
}

export default function SearchBar({ onSearch, onLocationSelect }: SearchBarProps) {
  const [address, setAddress] = useState("");
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
    } catch {
      setError("Location not found. Try street or intersection.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setAddress("");
    setError(null);
  };

  return (
    <div className="relative w-full max-w-xl">
      <form onSubmit={handleSearch} className="relative flex items-center">
        <div className="absolute left-3.5 text-slate-400 pointer-events-none">
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
          ) : (
            <Search className="w-4 h-4 text-slate-400" />
          )}
        </div>

        <input
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Search street, intersection, or Gainesville address..."
          disabled={loading}
          className="w-full bg-slate-900/90 text-slate-100 placeholder-slate-400 text-sm rounded-xl pl-10 pr-24 py-2.5 border border-slate-700/60 shadow-inner focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all duration-200"
        />

        {address && !loading && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-20 text-slate-400 hover:text-slate-200 p-1 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}

        <button
          type="submit"
          disabled={loading || !address.trim()}
          className="absolute right-1.5 px-3.5 py-1.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium text-xs rounded-lg shadow-md shadow-cyan-900/20 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-1"
        >
          <MapPin className="w-3 h-3" />
          <span>Locate</span>
        </button>
      </form>

      {error && (
        <div className="absolute top-full mt-1.5 left-0 right-0 bg-red-950/90 border border-red-500/40 text-red-300 text-xs px-3 py-1.5 rounded-lg backdrop-blur-md flex items-center gap-2 z-50">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse"></span>
          {error}
        </div>
      )}
    </div>
  );
}

