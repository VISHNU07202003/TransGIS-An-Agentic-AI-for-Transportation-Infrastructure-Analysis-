import { ArrowUpRight, Check, FileText, Loader2, MessageCircle, Search, ShieldCheck } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ChatResponse } from '../types';
import ResultCard from './ResultCard';

interface Props {
  response: ChatResponse | null;
  question: string;
  loading: boolean;
  error: string | null;
  hasSelection: boolean;
  onAsk: () => void;
}
export default function AnalysisResults({ response, question, loading, error, hasSelection, onAsk }: Props) {
  const pending = loading && !!question;
  return <section className="analysis-results" aria-label="Analysis results" aria-busy={pending}>
    <div className="results-section-header"><div className="section-label"><span>02</span> Analysis & insights</div><span className="results-state">{pending ? 'IN PROGRESS' : response ? 'LATEST ANSWER' : 'READY WHEN YOU ARE'}</span></div>
    {question && <div className="analysis-question"><MessageCircle size={14} /><span>{question}</span></div>}
    {pending ? <div className="analysis-pending" role="status"><Loader2 size={23} className="spinning" /><h3>Looking into your question</h3><p>Checking available transportation records for your selection.</p><div className="skeleton-line" /><div className="skeleton-line short" /></div>
      : error ? <div className="analysis-empty"><Search size={24} /><h3>Let's try that again</h3><p role="alert">{error}</p><button onClick={onAsk}>Open Ask TransGIS <ArrowUpRight size={15} /></button></div>
      : response ? <div className="analysis-answer"><div className={'answer-status ' + response.status}>{response.status === 'no_data' ? 'No matching authoritative data' : response.status === 'needs_clarification' ? 'Your input is needed' : response.status === 'error' ? 'Analysis needs attention' : 'Response received'}</div><div className="message-content"><ReactMarkdown remarkPlugins={[remarkGfm]}>{response.message}</ReactMarkdown></div>{response.result && <ResultCard result={response.result} />}<button className="followup-button" onClick={onAsk}>Ask a follow-up <ArrowUpRight size={15} /></button></div>
      : <div className="analysis-empty"><div className="report-illustration" aria-hidden="true"><FileText size={31} /><span><Check size={12} /></span></div><span className="eyebrow">A PLACE FOR YOUR FINDINGS</span><h3>{hasSelection ? 'Your location. Your questions.' : 'Turn a place into an insight.'}</h3><p>{hasSelection ? 'Ask TransGIS about this intersection. Your latest answer and available source records will appear here.' : 'Choose an intersection, then ask about traffic or infrastructure. We’ll keep the answer and its sources together here.'}</p><button onClick={onAsk}><MessageCircle size={16} /> Ask TransGIS <ArrowUpRight size={15} /></button><div className="output-preview"><span><FileText size={14} /> Clear answers</span><span><ShieldCheck size={14} /> Source records</span></div></div>}
  </section>;
}
