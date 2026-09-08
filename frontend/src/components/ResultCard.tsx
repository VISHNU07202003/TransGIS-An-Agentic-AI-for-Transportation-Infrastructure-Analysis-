import type { TrafficResult, IntersectionCandidate } from '../types';
import ProvenancePanel from './ProvenancePanel';
import CandidateIntersections from './CandidateIntersections';

interface ResultCardProps {
  result?: TrafficResult;
  intersection?: IntersectionCandidate | null;
  candidates?: IntersectionCandidate[];
  onCandidateSelect?: (candidate: IntersectionCandidate) => void;
}

export default function ResultCard({ result, intersection, candidates, onCandidateSelect }: ResultCardProps) {
  if (!result && (!candidates || candidates.length === 0)) {
    return <div className="result-card empty">Select a location and ask a question to see results.</div>;
  }

  return (
    <div className="result-card">
      {intersection && (
        <div className="selected-intersection">
          <h3>Intersection</h3>
          <p>{intersection.name}</p>
        </div>
      )}

      {candidates && candidates.length > 0 && !intersection && (
        <CandidateIntersections 
          candidates={candidates} 
          onSelect={onCandidateSelect!} 
        />
      )}

      {result && (
        <div className="traffic-result">
          <h3>Result</h3>
          {result.result_type === 'UNAVAILABLE' ? (
            <div className="no-data">No data available. {result.message}</div>
          ) : (
            <>
              <div className="result-value">
                <span className="value">{result.value}</span>
                <span className="unit">{result.unit}</span>
              </div>
              <div className="result-type badge">{result.result_type}</div>
              {result.provenance && <ProvenancePanel provenance={result.provenance} />}
            </>
          )}
        </div>
      )}
    </div>
  );
}
