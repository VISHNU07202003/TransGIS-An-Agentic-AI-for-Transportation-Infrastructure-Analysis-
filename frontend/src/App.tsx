import { Activity, ShieldCheck, GitBranch, Sparkles, Navigation, Layers } from "lucide-react";
import MapView from "./components/MapView";
import SearchBar from "./components/SearchBar";
import ChatPanel from "./components/ChatPanel";
import ResultCard from "./components/ResultCard";
import { useMapSelection } from "./hooks/useMapSelection";
import { useChat } from "./hooks/useChat";

export default function App() {
  const {
    selectedLocation,
    candidates,
    selectedIntersection,
    selectLocation,
    selectIntersection,
    loading: mapLoading,
  } = useMapSelection();

  const {
    messages,
    sendMessage,
    loading: chatLoading,
    lastResponse,
  } = useChat();

  const handleSearch = async (_address: string) => {
    // Search coordinates are passed via selectLocation callback
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-[#070b14] text-slate-100 overflow-hidden font-sans selection:bg-cyan-500 selection:text-slate-950">
      {/* Sleek Top Navigation Bar */}
      <header className="h-16 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl px-5 flex items-center justify-between z-30 flex-shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-blue-600 to-indigo-600 p-0.5 shadow-lg shadow-cyan-900/30 flex items-center justify-center">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Activity className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-300 bg-clip-text text-transparent">
                TransGIS
              </h1>
              <span className="text-[10px] px-1.5 py-0.5 rounded font-mono font-bold bg-cyan-950/80 text-cyan-300 border border-cyan-800/50">
                v1.0-PROTOTYPE
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">
              Agentic AI Transportation Infrastructure Analysis
            </p>
          </div>
        </div>

        {/* Center Search Bar */}
        <div className="flex-1 max-w-xl mx-6">
          <SearchBar
            onSearch={handleSearch}
            onLocationSelect={(lat, lng) => selectLocation(lat, lng, "geocoder")}
          />
        </div>

        {/* Right Status & Links */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-xl text-xs">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-slate-300 font-mono text-[11px]">FDOT & SODA Validated</span>
          </div>

          <a
            href="https://github.com/VISHNU07202003/TransGIS-An-Agentic-AI-for-Transportation-Infrastructure-Analysis-"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white transition-all text-xs font-medium"
          >
            <GitBranch className="w-4 h-4 text-cyan-400" />
            <span className="hidden sm:inline">GitHub</span>
          </a>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden p-3 gap-3">
        {/* Left Side: Interactive Geospatial Map */}
        <div className="flex-1 relative rounded-2xl overflow-hidden border border-slate-800/90 shadow-2xl bg-slate-950">
          <MapView
            onMapClick={(lat, lng) => selectLocation(lat, lng, "map_click")}
            markers={candidates}
            selectedIntersection={selectedIntersection}
            mapFeatures={lastResponse?.map_features}
            selectedLocation={selectedLocation}
          />
        </div>

        {/* Right Side: Agent Intelligence & Contextual Results */}
        <div className="w-full lg:w-[480px] xl:w-[540px] flex flex-col gap-3 h-[45vh] lg:h-full flex-shrink-0">
          {/* Top Panel: Agent Chat & Natural Language Query */}
          <div className="flex-1 min-h-0">
            <ChatPanel
              messages={messages}
              onSendMessage={(msg) =>
                sendMessage(msg, selectedLocation, selectedIntersection?.id)
              }
              isLoading={chatLoading}
            />
          </div>

          {/* Bottom Panel: Structured Metrics & Provenance Card */}
          <div className="h-[220px] xl:h-[250px] overflow-y-auto bg-slate-950/50 backdrop-blur-md rounded-2xl border border-slate-800/90 p-3 shadow-xl flex-shrink-0">
            <ResultCard
              result={lastResponse?.result}
              intersection={selectedIntersection}
              candidates={candidates}
              onCandidateSelect={selectIntersection}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

