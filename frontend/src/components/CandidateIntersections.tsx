import type { IntersectionCandidate } from '../types';

interface CandidateIntersectionsProps {
  candidates: IntersectionCandidate[];
  onSelect: (candidate: IntersectionCandidate) => void;
  selectedId?: number;
}

export default function CandidateIntersections({ candidates, onSelect, selectedId }: CandidateIntersectionsProps) {
  if (!candidates || candidates.length === 0) return null;

  return (
    <div className="candidate-intersections">
      <h4>Select an Intersection</h4>
      <ul>
        {candidates.map(candidate => (
          <li 
            key={candidate.id} 
            className={selectedId === candidate.id ? 'selected' : ''}
            onClick={() => onSelect(candidate)}
          >
            <div className="candidate-name">{candidate.name}</div>
            <div className="candidate-distance">{Math.round(candidate.distance_m)}m away</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
