import { ArrowUpRight, Database } from 'lucide-react';
import type { Provenance } from '../types';
export default function ProvenancePanel({ provenance }: { provenance: Provenance }) {
  return <details className="provenance"><summary><Database size={15} />Source & provenance<span>View record</span></summary><dl><div><dt>Agency</dt><dd>{provenance.agency}</dd></div><div><dt>Dataset</dt><dd>{provenance.dataset}</dd></div>{provenance.record_id && <div><dt>Record</dt><dd>{provenance.record_id}</dd></div>}{provenance.observation_date && <div><dt>Observation date</dt><dd>{provenance.observation_date}</dd></div>}{provenance.spatial_relation && <div><dt>Location relation</dt><dd>{provenance.spatial_relation}</dd></div>}<div><dt>Retrieved</dt><dd>{new Date(provenance.retrieval_timestamp).toLocaleString()}</dd></div></dl><a href={provenance.source_url} target="_blank" rel="noopener noreferrer">Open official source <ArrowUpRight size={14} /></a></details>;
}

