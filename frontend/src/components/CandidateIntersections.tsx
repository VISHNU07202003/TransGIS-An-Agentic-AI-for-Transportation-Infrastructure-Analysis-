import { MapPin, ArrowRight } from "lucide-react";
import type { IntersectionCandidate } from "../types";

interface CandidateIntersectionsProps {
  candidates: IntersectionCandidate[];
  onSelect: (candidate: IntersectionCandidate) => void;
  selectedId?: number;
}

export default function CandidateIntersections({
  candidates,
  onSelect,
  selectedId,
}: CandidateIntersectionsProps) {
  if (!candidates || candidates.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs font-medium text-slate-300">
        <span className="flex items-center gap-1.5 text-cyan-400 font-semibold uppercase tracking-wider text-[11px]">
          <MapPin className="w-3.5 h-3.5" /> Nearby Candidate Intersections
        </span>
        <span className="text-[11px] text-slate-400 font-mono">
          {candidates.length} candidate{candidates.length > 1 ? "s" : ""}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto pr-1">
        {candidates.map((candidate) => {
          const isSelected = selectedId === candidate.id;
          return (
            <button
              key={candidate.id}
              onClick={() => onSelect(candidate)}
              type="button"
              className={`w-full text-left p-2.5 rounded-xl border transition-all duration-200 flex items-center justify-between group ${
                isSelected
                  ? "bg-cyan-950/50 border-cyan-500/80 shadow-md shadow-cyan-950/50 ring-1 ring-cyan-500/50"
                  : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/60"
              }`}
            >
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      isSelected ? "bg-cyan-400 animate-pulse" : "bg-slate-500"
                    }`}
                  />
                  <div className="font-semibold text-slate-100 text-xs truncate">
                    {candidate.name}
                  </div>
                </div>
                <div className="text-[11px] text-slate-400 mt-1 pl-4 flex items-center gap-2 font-mono">
                  <span>ID: #{candidate.id}</span>
                  <span>•</span>
                  <span className="text-cyan-400/90 font-medium">
                    {Math.round(candidate.distance_m)}m away
                  </span>
                </div>
              </div>

              <div
                className={`p-1.5 rounded-lg ml-2 transition-colors ${
                  isSelected
                    ? "bg-cyan-500 text-slate-950"
                    : "text-slate-400 group-hover:text-cyan-300 group-hover:bg-slate-800"
                }`}
              >
                <ArrowRight className="w-3.5 h-3.5" />
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

