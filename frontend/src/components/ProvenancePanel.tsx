import { useState } from "react";
import { Database, ExternalLink, ShieldCheck, ChevronDown, ChevronUp, Calendar, Clock, Compass } from "lucide-react";
import type { Provenance } from "../types";

export default function ProvenancePanel({ provenance }: { provenance: Provenance }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="mt-3 bg-slate-900/60 border border-slate-700/50 rounded-xl overflow-hidden backdrop-blur-sm transition-all duration-200">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3.5 py-2.5 text-xs text-slate-300 hover:text-white hover:bg-slate-800/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-semibold text-slate-200">Data Provenance & Audit Trail</span>
          <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-950/60 text-emerald-300 border border-emerald-700/40">
            Authoritative
          </span>
        </div>
        {isOpen ? (
          <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
        )}
      </button>

      {isOpen && (
        <div className="p-3.5 border-t border-slate-800 bg-slate-950/40 text-xs space-y-2.5">
          <div className="grid grid-cols-2 gap-2 text-slate-300">
            <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <div className="text-[10px] uppercase font-mono text-slate-400 mb-1 flex items-center gap-1">
                <Database className="w-3 h-3 text-cyan-400" /> Source Agency
              </div>
              <div className="font-medium text-slate-100">{provenance.agency}</div>
            </div>

            <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
              <div className="text-[10px] uppercase font-mono text-slate-400 mb-1 flex items-center gap-1">
                <Compass className="w-3 h-3 text-cyan-400" /> Dataset Name
              </div>
              <div className="font-medium text-slate-100 truncate" title={provenance.dataset}>
                {provenance.dataset}
              </div>
            </div>
          </div>

          <div className="space-y-1.5 pt-1">
            {provenance.record_id && (
              <div className="flex items-center justify-between py-1 border-b border-slate-800/60 text-[11px]">
                <span className="text-slate-400">Record ID:</span>
                <span className="font-mono text-cyan-300 font-semibold">{provenance.record_id}</span>
              </div>
            )}

            {provenance.observation_date && (
              <div className="flex items-center justify-between py-1 border-b border-slate-800/60 text-[11px]">
                <span className="text-slate-400 flex items-center gap-1">
                  <Calendar className="w-3 h-3 text-slate-400" /> Count Year:
                </span>
                <span className="text-slate-200">{provenance.observation_date}</span>
              </div>
            )}

            {provenance.spatial_relation && (
              <div className="flex items-center justify-between py-1 border-b border-slate-800/60 text-[11px]">
                <span className="text-slate-400">Spatial Proximity:</span>
                <span className="text-slate-200 font-medium">{provenance.spatial_relation}</span>
              </div>
            )}

            <div className="flex items-center justify-between py-1 border-b border-slate-800/60 text-[11px]">
              <span className="text-slate-400 flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-400" /> Ingested Timestamp:
              </span>
              <span className="text-slate-300 font-mono text-[10px]">
                {new Date(provenance.retrieval_timestamp).toLocaleString()}
              </span>
            </div>

            {provenance.source_url && (
              <div className="pt-2">
                <a
                  href={provenance.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs text-cyan-400 hover:text-cyan-300 hover:underline transition-colors"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>Verify at Official Source API endpoint</span>
                </a>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

