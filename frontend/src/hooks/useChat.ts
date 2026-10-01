import { useRef, useState } from 'react';
import { api } from '../api/client';
import type { ChatMessage } from '../components/ChatPanel';
import type { ChatResponse, MapLocation } from '../types';
export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);
  const [lastQuestion, setLastQuestion] = useState('');
  const [error, setError] = useState<string | null>(null);
  const contextVersion = useRef(0);
  const conversationId = useRef<string>();
  const clearResult = () => { contextVersion.current++; setLastResponse(null); setLastQuestion(''); setError(null); };
  const sendMessage = async (message: string, location?: MapLocation | null, selectedIntersectionId?: number) => {
    if (loading) return;
    const version = contextVersion.current;
    setMessages(prev => [...prev, { role: 'user', content: message, timestamp: new Date() }]);
    setLoading(true); setLastResponse(null); setLastQuestion(message); setError(null);
    try {
      const res = await api.chat({ message, location: location || undefined, selected_intersection_id: selectedIntersectionId, conversation_id: conversationId.current });
      conversationId.current = res.conversation_id;
      if (version === contextVersion.current) {
        setLastResponse(res);
        setMessages(prev => [...prev, { role: 'agent', content: res.message, timestamp: new Date() }]);
      } else {
        setMessages(prev => [...prev, { role: 'agent', content: 'The location changed while this request was running. Ask again to analyze your new selection.', timestamp: new Date() }]);
      }
    } catch {
      if (version === contextVersion.current) setError('The analysis service could not be reached. Please try again.');
      setMessages(prev => [...prev, { role: 'agent', content: 'The analysis service could not be reached. Please try again.', timestamp: new Date() }]);
    } finally { setLoading(false); }
  };
  return { messages, sendMessage, loading, lastResponse, lastQuestion, error, clearResult };
}
