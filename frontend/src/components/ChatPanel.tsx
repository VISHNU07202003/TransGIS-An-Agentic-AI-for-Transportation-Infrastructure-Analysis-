import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ArrowUp, ArrowUpRight, ChartNoAxesCombined, Clock3, Loader2, Route, TrafficCone } from 'lucide-react';
export interface ChatMessage { role: 'user' | 'agent'; content: string; timestamp: Date; }
interface Props { messages: ChatMessage[]; onSendMessage: (message: string) => void; isLoading: boolean; hasSelection: boolean; }
const prompts = [
  { icon: ChartNoAxesCombined, label: 'Daily traffic volume', message: 'What is the AADT near this intersection?' },
  { icon: TrafficCone, label: 'Traffic signal records', message: 'Are there traffic signals nearby?' },
  { icon: Clock3, label: 'Hourly traffic counts', message: 'What was the traffic volume from 5 PM to 6 PM here?' },
];
export default function ChatPanel({ messages, onSendMessage, isLoading, hasSelection }: Props) {
  const [input, setInput] = useState('');
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => { if (messages.length || isLoading) end.current?.scrollIntoView({ behavior: 'auto', block: 'nearest' }); }, [messages, isLoading]);
  const send = () => { if (input.trim() && !isLoading) { onSendMessage(input.trim()); setInput(''); } };
  return <section className="chat-panel" aria-label="Ask TransGIS">
    <div className="section-label"><span>02</span> Ask TransGIS <span className="ai-tag">AI ASSISTANT</span></div>
    <div className="chat-stream" role="log" aria-live="polite" aria-busy={isLoading}>
      {!messages.length ? <div className="chat-welcome"><div className="assistant-symbol"><Route size={24} /></div><h3>What would you like<br />to know?</h3><p>Explore traffic and infrastructure,<br />one question at a time.</p><div className="prompt-list">{prompts.map(({ icon: Icon, label, message }) => <button key={label} onClick={() => onSendMessage(message)} disabled={isLoading}><Icon size={17} /><span>{label}</span><ArrowUpRight size={15} /></button>)}</div></div> : messages.map((message, i) => <article key={i} className={'chat-message ' + message.role}><span className="message-author">{message.role === 'user' ? 'You' : 'TransGIS'}</span><div className="message-content">{message.role === 'agent' ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown> : message.content}</div></article>)}
      {isLoading && <div className="thinking" role="status"><Loader2 size={15} className="spinning" /> Checking transportation records…</div>}<div ref={end} />
    </div>
    <form className="chat-composer" onSubmit={e => { e.preventDefault(); send(); }}><label className="sr-only" htmlFor="question">Ask a transportation question</label><textarea id="question" rows={2} value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }} placeholder={hasSelection ? 'Ask about this intersection…' : 'Ask a transportation question…'} disabled={isLoading} /><div className="composer-bottom"><span><span className={'context-indicator ' + (hasSelection ? 'selected' : '')} />{hasSelection ? 'Intersection in context' : 'Select a location for context'}</span><button type="submit" aria-label="Send question" disabled={!input.trim() || isLoading}><ArrowUp size={18} /></button></div></form>
    <p className="chat-note">Answers depend on available records. Review the source.</p>
  </section>;
}

