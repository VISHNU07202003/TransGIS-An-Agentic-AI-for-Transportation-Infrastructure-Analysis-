import { useState } from 'react';
import MapView from './components/MapView';
import SearchBar from './components/SearchBar';
import ChatPanel from './components/ChatPanel';
import ResultCard from './components/ResultCard';
import { useMapSelection } from './hooks/useMapSelection';
import { useChat } from './hooks/useChat';

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

  const handleSearch = async (address: string) => {
    // Handled in SearchBar for now, but could be hoisted
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Transportation Infrastructure Analysis</h1>
        <SearchBar onSearch={handleSearch} onLocationSelect={(lat, lng) => selectLocation(lat, lng, 'geocoder')} />
      </header>
      
      <main className="app-main">
        <div className="map-section">
          <MapView 
            onMapClick={(lat, lng) => selectLocation(lat, lng, 'map_click')}
            markers={candidates}
            selectedIntersection={selectedIntersection}
            mapFeatures={lastResponse?.map_features}
            selectedLocation={selectedLocation}
          />
        </div>
        
        <div className="bottom-section">
          <div className="chat-panel-container">
            <ChatPanel 
              messages={messages} 
              onSendMessage={(msg) => sendMessage(msg, selectedLocation, selectedIntersection?.id)} 
              isLoading={chatLoading} 
            />
          </div>
          
          <div className="result-panel-container">
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
