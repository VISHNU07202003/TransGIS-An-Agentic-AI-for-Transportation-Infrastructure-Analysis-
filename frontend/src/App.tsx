import { useState, useEffect } from 'react';
import { ArrowUpRight, Compass, Map, PanelRightClose, PanelRightOpen, Route, X } from 'lucide-react';
import MapView from './components/MapView';
import SearchBar from './components/SearchBar';
import ChatPanel from './components/ChatPanel';
import ResultCard from './components/ResultCard';
import { useMapSelection } from './hooks/useMapSelection';
import { useChat } from './hooks/useChat';

export default function App() {
  const selection = useMapSelection();
  const chat = useChat();
  const [panelOpen, setPanelOpen] = useState(true);
  const [showGuide, setShowGuide] = useState(false);
  const [showHeading, setShowHeading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShowHeading(false), 20000);
    return () => clearTimeout(timer);
  }, []);
  const selectLocation = (lat: number, lon: number, source: 'map_click' | 'geocoder') => {
    chat.clearResult();
    void selection.selectLocation(lat, lon, source);
  };
  const selectIntersection = (candidate: Parameters<typeof selection.selectIntersection>[0]) => {
    chat.clearResult();
    selection.selectIntersection(candidate);
  };
  return (
    <div className="workspace">
      <aside className="app-rail" aria-label="Workspace navigation">
        <a className="brand-mark" href="#" aria-label="TransGIS home"><Route size={25} /></a>
        <div className="rail-divider" />
        <button className="rail-button active" title="Map workspace" aria-label="Map workspace" onClick={() => setShowGuide(false)}><Map size={21} /></button>
        <button className={showGuide ? 'rail-button active' : 'rail-button'} title="How to explore" aria-label="How to explore" onClick={() => setShowGuide(v => !v)}><Compass size={21} /></button>
        <span className="rail-caption">GAINESVILLE, FL</span>
        <a className="rail-button rail-bottom" href="https://github.com/VISHNU07202003/TransGIS-An-Agentic-AI-for-Transportation-Infrastructure-Analysis-" target="_blank" rel="noopener noreferrer" aria-label="Open project on GitHub" title="Project on GitHub"><ArrowUpRight size={21} /></a>
      </aside>
      <div className="workspace-body">
        <header className="topbar">
          <div className="wordmark">TransGIS<span>Research workspace</span></div>
          <div className="topbar-context"><span className="context-dot" /> Gainesville, Florida <span className="prototype-tag">PROTOTYPE</span></div>
          <button className="icon-button" onClick={() => setPanelOpen(v => !v)} aria-label={panelOpen ? 'Hide analysis panel' : 'Show analysis panel'} aria-expanded={panelOpen}>{panelOpen ? <PanelRightClose size={20} /> : <PanelRightOpen size={20} />}</button>
        </header>
        <main className={panelOpen ? 'main-workspace' : 'main-workspace panel-hidden'}>
          <section className="map-workspace" aria-label="Gainesville transportation map">
            <MapView onMapClick={(lat, lon) => selectLocation(lat, lon, 'map_click')} markers={selection.candidates} selectedIntersection={selection.selectedIntersection} selectedLocation={selection.selectedLocation} onCandidateSelect={selectIntersection} mapFeatures={chat.lastResponse?.map_features} />
            <div className="map-search"><SearchBar onLocationSelect={(lat, lon) => selectLocation(lat, lon, 'geocoder')} /></div>
            {showHeading && <div className="map-heading"><span className="eyebrow">THE EXPLORER</span><h1>A new perspective<br />on every intersection.</h1><p>Local context. Authoritative sources.</p></div>}
            {showGuide && <div className="guide-card"><button className="icon-button" aria-label="Close guide" onClick={() => setShowGuide(false)}><X size={17} /></button><span className="eyebrow">A LITTLE GUIDANCE</span><h2>Start with a place.</h2><ol><li>Search an address or click the map.</li><li>Choose an intersection from the nearby results.</li><li>Ask about traffic counts or signal records.</li></ol><p>Hourly counts may be unavailable. Check each measurement against its source.</p></div>}
            <div className="map-bottom"><div className="map-location"><span className="location-dot" /><span>{selection.selectedLocation ? selection.selectedLocation.latitude.toFixed(5) + '° N · ' + Math.abs(selection.selectedLocation.longitude).toFixed(5) + '° W' : '29.6516° N · 82.3248° W'}<small>{selection.selectedIntersection ? 'Intersection selected' : 'Click the map to begin exploring'}</small></span></div><span className="map-legend"><i /> FDOT intersections</span></div>
          </section>
          {panelOpen && <aside className="analysis-panel" aria-label="Analysis panel">
            <div className="panel-heading"><div><span className="eyebrow">YOUR WORKSPACE</span><h2>Explore & understand<span>.</span></h2></div><span className="panel-index">01 / 02</span></div>
            <div className="selection-section"><div className="section-label"><span>01</span> Location context {selection.loading && <span className="inline-loading" role="status">Searching…</span>}</div>
              <ResultCard intersection={selection.selectedIntersection} candidates={selection.candidates} onCandidateSelect={selectIntersection} loading={selection.loading} error={selection.error} hasLocation={!!selection.selectedLocation} />
            </div>
            <ChatPanel messages={chat.messages} onSendMessage={msg => chat.sendMessage(msg, selection.selectedLocation, selection.selectedIntersection?.id)} isLoading={chat.loading} hasSelection={!!selection.selectedIntersection} />
            {chat.lastResponse?.result && <div className="measurement-section"><ResultCard result={chat.lastResponse.result} /></div>}
            <footer className="panel-footer"><span className="source-dot" /> FDOT + City of Gainesville <span>Source-backed exploration</span></footer>
          </aside>}
        </main>
      </div>
    </div>
  );
}

