import { MapPin, Activity, CheckCircle2, AlertCircle, BarChart3 } from "lucide-react";
import type { TrafficResult, IntersectionCandidate } from "../types";
import ProvenancePanel from "./ProvenancePanel";
import CandidateIntersections from "./CandidateIntersections";

interface ResultCardProps {
  result?: TrafficResult;
  intersection?: IntersectionCandidate | null;
  candidates?: IntersectionCandidate[];
  onCandidateSelect?: (candidate: IntersectionCandidate) => void;
}

export default function ResultCard({
  result,
  intersection,
  candidates,
  onCandidateSelect,
}: ResultCardProps) {
  if (!result && (!candidates || candidates.length === 0) && !intersection) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-6 bg-slate-900/30 border border-slate-800/80 rounded-2xl">
        <div className="w-12 h-12 rounded-2xl bg-cyan-950/40 border border-cyan-800/40 flex items-center justify-center text-cyan-400 mb-3 shadow-inner">
          <MapPin className="w-6 h-6 animate-bounce" />
        </div>
        <h4 className="text-sm font-semibold text-slate-200 mb-1">Select an Intersection</h4>
        <p className="text-xs text-slate-400 max-w-xs leading-relaxed">
          Click anywhere on the Gainesville map or search an address above to inspect traffic volume, signals, and authoritative GIS data.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {intersection && (
        <div className="bg-gradient-to-br from-slate-900/90 to-slate-950/90 border border-cyan-500/30 rounded-2xl p-4 shadow-lg shadow-black/40 relative overflow-hidden backdrop-blur-md">
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-full blur-2xl pointer-events-none" />
          
          <div className="flex items-start justify-between gap-2 mb-2">
            <div>
              <div className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> Active Selected Intersection
              </div>
              <h3 className="text-sm font-bold text-white mt-1 leading-snug">
                {intersection.name}
              </h3>
            </div>
            <span className="px-2 py-0.5 rounded-full bg-cyan-950/70 border border-cyan-800/60 text-cyan-300 font-mono text-[10px] font-medium">
              ID #{intersection.id}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2 mt-3 pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
            <div>
              Lat: <span className="text-slate-200">{intersection.latitude.toFixed(5)}</span>
            </div>
            <div>
              Lng: <span className="text-slate-200">{intersection.longitude.toFixed(5)}</span>
            </div>
          </div>
        </div>
      )}

      {candidates && candidates.length > 0 && (
        <CandidateIntersections
          candidates={candidates}
          onSelect={onCandidateSelect!}
          selectedId={intersection?.id}
        />
      )}

      {result && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 shadow-lg backdrop-blur-md">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5 uppercase tracking-wider text-[11px]">
              <BarChart3 className="w-4 h-4 text-cyan-400" /> Spatial Intelligence Metric
            </span>
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-mono uppercase font-semibold border ${
                result.result_type === "UNAVAILABLE"
                  ? "bg-amber-950/60 text-amber-300 border-amber-800/50"
                  : "bg-emerald-950/60 text-emerald-300 border-emerald-800/50"
              }`}
            >
              {result.result_type}
            </span>
          </div>

          {result.result_type === "UNAVAILABLE" ? (
            <div className="flex items-start gap-2.5 p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 text-xs text-amber-200/90">
              <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <span>{result.message || "No data recorded within the spatial radius for this metric."}</span>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800/80 flex items-baseline justify-between">
                <span className="text-xs text-slate-400 font-medium">Authoritative Value</span>
                <div className="text-right">
                  <span className="text-2xl font-black tracking-tight text-white font-mono bg-gradient-to-r from-cyan-300 to-blue-400 bg-clip-text text-transparent">
                    {result.value}
                  </span>
                  {result.unit && (
                    <span className="text-xs text-slate-400 ml-1.5 font-sans font-medium">
                      {result.unit}
                    </span>
                  )}
                </div>
              </div>

              {result.message && (
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-800/30 p-2.5 rounded-xl border border-slate-800/60">
                  {result.message}
                </p>
              )}

              {result.provenance && <ProvenancePanel provenance={result.provenance} />}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

