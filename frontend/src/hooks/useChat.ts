import { useState } from 'react';
import { api } from '../api/client';
import type { ChatMessage } from '../components/ChatPanel';
import type { ChatResponse, MapLocation } from '../types';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);

  const sendMessage = async (message: string, location?: MapLocation | null, selectedIntersectionId?: number) => {
    const newUserMsg: ChatMessage = { role: 'user', content: message, timestamp: new Date() };
    setMessages(prev => [...prev, newUserMsg]);
    setLoading(true);
    setError(null);

    try {
      const res = await api.chat({
        message,
        location: location || undefined,
        selected_intersection_id: selectedIntersectionId,
        conversation_id: conversationId,
      });

      if (res.conversation_id && !conversationId) {
        setConversationId(res.conversation_id);
      }

      setLastResponse(res);
      setMessages(prev => [...prev, { role: 'agent', content: res.message, timestamp: new Date() }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setMessages(prev => [...prev, { role: 'agent', content: 'An error occurred while processing your request.', timestamp: new Date() }]);
    } finally {
      setLoading(false);
    }
  };

  return { messages, sendMessage, loading, error, lastResponse };
}
