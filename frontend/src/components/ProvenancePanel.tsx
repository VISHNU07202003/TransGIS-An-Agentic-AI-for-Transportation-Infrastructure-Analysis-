import { useState } from 'react';
import type { Provenance } from '../types';

export default function ProvenancePanel({ provenance }: { provenance: Provenance }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="provenance-panel">
      <button className="provenance-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? 'Hide Data Source' : 'View Data Source'}
      </button>
      
      {isOpen && (
        <div className="provenance-details">
          <dl>
            <dt>Agency</dt>
            <dd>{provenance.agency}</dd>
            
            <dt>Dataset</dt>
            <dd>{provenance.dataset}</dd>
            
            <dt>Source URL</dt>
            <dd><a href={provenance.source_url} target="_blank" rel="noopener noreferrer">Link</a></dd>
            
            {provenance.record_id && (
              <>
                <dt>Record ID</dt>
                <dd>{provenance.record_id}</dd>
              </>
            )}
            
            {provenance.observation_date && (
              <>
                <dt>Observation Date</dt>
                <dd>{provenance.observation_date}</dd>
              </>
            )}
            
            <dt>Retrieved At</dt>
            <dd>{new Date(provenance.retrieval_timestamp).toLocaleString()}</dd>
            
            {provenance.spatial_relation && (
              <>
                <dt>Spatial Relation</dt>
                <dd>{provenance.spatial_relation}</dd>
              </>
            )}
          </dl>
        </div>
      )}
    </div>
  );
}
