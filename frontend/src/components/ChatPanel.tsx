import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ArrowUp, ArrowUpRight, ChartNoAxesCombined, Clock3, Loader2, Route, TrafficCone, MessageCircle, X, GripHorizontal, Sparkles, PanelRight } from 'lucide-react';

export interface ChatMessage { role: 'user' | 'agent'; content: string; timestamp: Date; }
interface Props {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  hasSelection: boolean;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  placeLabel: string;
  hasResult: boolean;
  onViewResult: () => void;
}
const prompts = [
  { icon: ChartNoAxesCombined, label: 'Daily traffic volume', message: 'What is the AADT near this intersection?' },
  { icon: TrafficCone, label: 'Traffic signal records', message: 'Are there traffic signals nearby?' },
  { icon: Clock3, label: 'Hourly traffic counts', message: 'What was the traffic volume from 5 PM to 6 PM here?' },
];
function clampPosition(position: { x: number; y: number }) {
  const width = Math.min(400, window.innerWidth - 24);
  const height = Math.min(590, window.innerHeight - 100);
  return {
    x: Math.max(12, Math.min(position.x, window.innerWidth - width - 12)),
    y: Math.max(12, Math.min(position.y, window.innerHeight - height - 12)),
  };
}
export default function ChatPanel({ messages, onSendMessage, isLoading, hasSelection, isOpen, onOpenChange, placeLabel, hasResult, onViewResult }: Props) {
  const [input, setInput] = useState('');
  const [position, setPosition] = useState(() => clampPosition({ x: window.innerWidth - 424, y: window.innerHeight - 614 }));
  const [isDragging, setIsDragging] = useState(false);
  const dragStart = useRef({ x: 0, y: 0 });
  const stream = useRef<HTMLDivElement>(null);
  const launcher = useRef<HTMLButtonElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  const wasOpen = useRef(false);

  useEffect(() => {
    if (isOpen && stream.current) stream.current.scrollTop = stream.current.scrollHeight;
  }, [messages, isLoading, isOpen]);
  useEffect(() => {
    if (isOpen) {
      setPosition(current => clampPosition(current));
      textarea.current?.focus({ preventScroll: true });
    } else if (wasOpen.current) launcher.current?.focus({ preventScroll: true });
    wasOpen.current = isOpen;
  }, [isOpen]);
  useEffect(() => {
    const resize = () => setPosition(current => clampPosition(current));
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, []);

  const send = () => {
    if (input.trim() && !isLoading) { onSendMessage(input.trim()); setInput(''); }
  };
  const handlePointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if ((e.target as Element).closest('button') || e.button !== 0) return;
    setIsDragging(true);
    dragStart.current = { x: e.clientX - position.x, y: e.clientY - position.y };
    e.currentTarget.setPointerCapture(e.pointerId);
  };
  const handlePointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (isDragging) setPosition(clampPosition({ x: e.clientX - dragStart.current.x, y: e.clientY - dragStart.current.y }));
  };
  const stopDrag = (e: React.PointerEvent<HTMLDivElement>) => {
    setIsDragging(false);
    if (e.currentTarget.hasPointerCapture(e.pointerId)) e.currentTarget.releasePointerCapture(e.pointerId);
  };

  return <>
    <button ref={launcher} className={'chat-bubble-toggle ' + (isOpen ? 'launcher-hidden' : '')}
      onClick={() => onOpenChange(true)} aria-label="Open Ask TransGIS" aria-expanded={isOpen} aria-controls="transgis-chat"
      tabIndex={isOpen ? -1 : 0}>
      <span className="launcher-symbol">{isLoading ? <Loader2 className="spinning" size={23} /> : <MessageCircle size={23} />}<Sparkles size={12} /></span>
      <span className="launcher-copy"><strong>Ask TransGIS</strong><small>{isLoading ? 'Working on your question…' : hasResult ? 'Continue the conversation' : 'Your map, explained'}</small></span>
      <ArrowUpRight size={18} className="launcher-arrow" />
    </button>
    {isOpen && <section id="transgis-chat" role="dialog" aria-modal="false" aria-labelledby="chat-title"
      className={'floating-chat-window ' + (isDragging ? 'dragging' : '')}
      style={{ left: position.x, top: position.y }}
      onKeyDown={e => { if (e.key === 'Escape') onOpenChange(false); }}>
      <div className="chat-window-header" onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove} onPointerUp={stopDrag} onPointerCancel={stopDrag}>
        <span className="chat-header-symbol"><Route size={20} /></span>
        <div className="chat-header-title"><strong id="chat-title">Ask TransGIS</strong><span>Explore with a little context</span></div>
        <GripHorizontal size={18} className="header-drag-handle" aria-hidden="true" />
        <button className="close-chat" onClick={() => onOpenChange(false)} aria-label="Close chat"><X size={18} /></button>
      </div>
      <div className="chat-place-context"><span className={'context-indicator ' + (hasSelection ? 'selected' : '')} /><span>{hasSelection ? placeLabel : 'Select an intersection for specific answers'}</span><span className="ai-tag">AI ASSISTANT</span></div>
      <div ref={stream} className="chat-stream" role="log" aria-live="polite" aria-busy={isLoading}>
        {!messages.length ? <div className="chat-welcome"><h3>A question worth<br /> exploring.</h3><p>Ask about your selected intersection.<br /> Your findings stay in the analysis sheet.</p><div className="prompt-list">{prompts.map(({ icon: Icon, label, message }) => <button key={label} onClick={() => onSendMessage(message)} disabled={isLoading}><Icon size={17} /><span>{label}</span><ArrowUpRight size={15} /></button>)}</div></div>
          : messages.map((message, i) => <article key={i} className={'chat-message ' + message.role}><span className="message-author">{message.role === 'user' ? 'You' : 'TransGIS'}</span><div className="message-content">{message.role === 'agent' ? <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown> : message.content}</div></article>)}
        {isLoading && <div className="thinking" role="status"><Loader2 size={15} className="spinning" /> Checking transportation records…</div>}
      </div>
      {hasResult && !isLoading && <button className="view-analysis" onClick={onViewResult}><PanelRight size={15} /> View answer & sources in analysis sheet <ArrowUpRight size={15} /></button>}
      <form className="chat-composer" onSubmit={e => { e.preventDefault(); send(); }}>
        <label className="sr-only" htmlFor="question">Ask a transportation question</label>
        <textarea ref={textarea} id="question" rows={2} value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
          placeholder={hasSelection ? 'Ask about this intersection…' : 'What would you like to explore?'} disabled={isLoading} />
        <div className="composer-bottom"><span>{hasSelection ? 'Using your selected intersection' : 'Add a location for better context'}</span><button type="submit" aria-label="Send question" disabled={!input.trim() || isLoading}><ArrowUp size={18} /></button></div>
      </form>
      <p className="chat-note">Available records only. Always review the source.</p>
    </section>}
  </>;
}
