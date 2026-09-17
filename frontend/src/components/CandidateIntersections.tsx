import { ArrowUpRight, Check, MapPin } from 'lucide-react';
import type { IntersectionCandidate } from '../types';
export default function CandidateIntersections({ candidates, onSelect, selectedId }: { candidates: IntersectionCandidate[]; onSelect: (candidate: IntersectionCandidate) => void; selectedId?: number }) {
  return <div className="candidate-list" aria-label="Nearby intersections">{candidates.map(candidate => <button className={'candidate-row ' + (selectedId === candidate.id ? 'selected' : '')} key={candidate.id} onClick={() => onSelect(candidate)} aria-pressed={selectedId === candidate.id}><MapPin size={16} /><span><strong>{candidate.name}</strong><small>{Math.round(candidate.distance_m)} m from your point · #{candidate.id}</small></span>{selectedId === candidate.id ? <Check size={17} /> : <ArrowUpRight size={16} />}</button>)}</div>;
}

