import { useState, useEffect, useRef } from 'react';
import { ArrowUpRight, Compass, Map, PanelRightClose, PanelRightOpen, Route, X } from 'lucide-react';
import MapView from './components/MapView';
import SearchBar from './components/SearchBar';
import ChatPanel from './components/ChatPanel';
import ResultCard from './components/ResultCard';
import { useMapSelection } from './hooks/useMapSelection';
import { useChat } from './hooks/useChat';
import { usePlaceLabel } from './hooks/usePlaceLabel';
import AnalysisResults from './components/AnalysisResults';

export default function App() {
  const selection = useMapSelection();
  const chat = useChat();
  const [panelOpen, setPanelOpen] = useState(true);
  const [showGuide, setShowGuide] = useState(false);
  const [showHeading, setShowHeading] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);
  const [revealAnswer, setRevealAnswer] = useState(0);
  const analysisPanel = useRef<HTMLElement>(null);
  const pin = selection.selectedIntersection || selection.selectedLocation;
  const place = usePlaceLabel(pin);

  useEffect(() => {
    if (revealAnswer) analysisPanel.current?.querySelector('.analysis-results')?.scrollIntoView({ block: 'start' });
  }, [revealAnswer]);

  useEffect(() => {
    const timer = setTimeout(() => setShowHeading(false), 7000);
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
        <span className="rail-caption" title={place.label}>{place.label.toUpperCase()}</span>
        <a className="rail-button rail-bottom" href="https://github.com/VISHNU07202003/TransGIS-An-Agentic-AI-for-Transportation-Infrastructure-Analysis-" target="_blank" rel="noopener noreferrer" aria-label="Open project on GitHub" title="Project on GitHub"><ArrowUpRight size={21} /></a>
      </aside>
      <div className="workspace-body">
        <header className="topbar">
          <div className="wordmark">TransGIS<span>Research workspace</span></div>
          <div className="topbar-context" aria-live="polite" title={place.address}><span className="context-dot" /><span className="current-place">{place.label}</span><span className="prototype-tag">PROTOTYPE</span></div>
          <button className="icon-button" onClick={() => setPanelOpen(v => !v)} aria-label={panelOpen ? 'Hide analysis panel' : 'Show analysis panel'} aria-expanded={panelOpen}>{panelOpen ? <PanelRightClose size={20} /> : <PanelRightOpen size={20} />}</button>
        </header>
        <main className={panelOpen ? 'main-workspace' : 'main-workspace panel-hidden'}>
          <section className="map-workspace" aria-label="Transportation map">
            <MapView onMapClick={(lat, lon) => selectLocation(lat, lon, 'map_click')} markers={selection.candidates} selectedIntersection={selection.selectedIntersection} selectedLocation={selection.selectedLocation} onCandidateSelect={selectIntersection} mapFeatures={chat.lastResponse?.map_features} />
            <div className="map-search"><SearchBar bias={pin} onLocationSelect={(lat, lon) => selectLocation(lat, lon, 'geocoder')} /></div>
            {showHeading && <div className="map-heading"><span className="eyebrow">THE EXPLORER</span><h1>A new perspective<br />on every intersection.</h1><p>Local context. Authoritative sources.</p></div>}
            {showGuide && <div className="guide-card"><button className="icon-button" aria-label="Close guide" onClick={() => setShowGuide(false)}><X size={17} /></button><span className="eyebrow">A LITTLE GUIDANCE</span><h2>Start with a place.</h2><ol><li>Search an address or click the map.</li><li>Choose an intersection from the nearby results.</li><li>Ask about traffic counts or signal records.</li></ol><p>Hourly counts may be unavailable. Check each measurement against its source.</p></div>}
            <div className="map-bottom"><div className="map-location" title={place.address}><span className="location-dot" /><span><strong className="pin-place-name">{place.label}</strong>{pin ? Math.abs(pin.latitude).toFixed(5) + (pin.latitude >= 0 ? '° N · ' : '° S · ') + Math.abs(pin.longitude).toFixed(5) + (pin.longitude >= 0 ? '° E' : '° W') : '29.6516° N · 82.3248° W'}<small>{selection.selectedIntersection ? 'Intersection selected' : selection.selectedLocation ? 'Selected map pin' : 'Click the map to begin exploring'}</small></span></div><span className="map-legend"><i /> FDOT intersections</span></div>
          </section>
          {panelOpen && <aside ref={analysisPanel} className="analysis-panel" aria-label="Analysis panel">
            <div className="panel-heading"><div><span className="eyebrow">YOUR ANALYSIS SHEET</span><h2>From place to insight<span>.</span></h2><p className="panel-subtitle">Your selected location, answers, and sources.</p></div></div>
            <div className="selection-section"><div className="section-label"><span>01</span> Selected location {selection.loading && <span className="inline-loading" role="status">Searching…</span>}</div>
              {pin && <div className="pin-locality"><span className="context-dot" />{place.label}<small>{selection.selectedIntersection ? 'Ready to analyze' : 'Choose a nearby intersection'}</small></div>}
              <ResultCard intersection={selection.selectedIntersection} candidates={selection.candidates} onCandidateSelect={selectIntersection} loading={selection.loading} error={selection.error} hasLocation={!!selection.selectedLocation} />
            </div>
            <AnalysisResults response={chat.lastResponse} question={chat.lastQuestion} loading={chat.loading} error={chat.error} hasSelection={!!selection.selectedIntersection} onAsk={() => setChatOpen(true)} />
            <footer className="panel-footer"><span className="source-dot" /> FDOT + City of Gainesville <span>Source-backed exploration</span></footer>
          </aside>}
        </main>
        <ChatPanel isOpen={chatOpen} onOpenChange={setChatOpen} messages={chat.messages} onSendMessage={msg => chat.sendMessage(msg, selection.selectedLocation, selection.selectedIntersection?.id)} isLoading={chat.loading} hasSelection={!!selection.selectedIntersection} placeLabel={place.label} hasResult={!!chat.lastResponse} onViewResult={() => { setChatOpen(false); setPanelOpen(true); setRevealAnswer(value => value + 1); }} />
      </div>
    </div>
  );
}

