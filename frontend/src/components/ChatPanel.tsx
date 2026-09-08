import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Send, Bot, User, Sparkles, Loader2, Info } from "lucide-react";

export interface ChatMessage {
  role: "user" | "agent";
  content: string;
  timestamp: Date;
}

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (msg: string) => void;
  isLoading: boolean;
}

export default function ChatPanel({ messages, onSendMessage, isLoading }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input);
    setInput("");
  };

  const samplePrompts = [
    "How many vehicles go in this intersection?",
    "Is there traffic in this intersection?",
    "Are there traffic signals nearby?",
    "Show traffic monitoring sites",
  ];

  return (
    <div className="flex flex-col h-full bg-slate-900/50 backdrop-blur-md rounded-2xl border border-slate-800/90 overflow-hidden shadow-2xl">
      {/* Panel Header */}
      <div className="px-4 py-3 border-b border-slate-800/80 bg-slate-950/40 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
            TransGIS Agent
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950/70 text-cyan-300 border border-cyan-800/50 font-mono">
            NaviGator OSS-20B
          </span>
        </div>
        <span className="text-[11px] text-slate-400 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-cyan-400" />
          Autonomous GIS Tools
        </span>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-3">
            <div className="w-10 h-10 rounded-2xl bg-cyan-950/60 border border-cyan-800/40 flex items-center justify-center text-cyan-400 shadow-inner">
              <Bot className="w-5 h-5" />
            </div>
            <div className="max-w-xs">
              <h4 className="text-sm font-semibold text-slate-200">Start an Analysis</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Click on any intersection or try one of the instant questions below:
              </p>
            </div>
            <div className="grid grid-cols-1 gap-1.5 w-full max-w-sm pt-2">
              {samplePrompts.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => onSendMessage(p)}
                  className="text-left text-xs bg-slate-950/60 hover:bg-cyan-950/40 hover:border-cyan-500/50 border border-slate-800 text-slate-300 hover:text-cyan-200 px-3 py-2 rounded-xl transition-all duration-200 group flex items-center justify-between"
                >
                  <span className="truncate">{p}</span>
                  <Sparkles className="w-3 h-3 text-slate-500 group-hover:text-cyan-400 transition-colors" />
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={i}
                className={`flex gap-3 max-w-[92%] ${
                  isUser ? "ml-auto flex-row-reverse" : "mr-auto"
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5 shadow-md ${
                    isUser
                      ? "bg-gradient-to-tr from-cyan-600 to-blue-600 text-white"
                      : "bg-slate-800 border border-slate-700 text-cyan-400"
                  }`}
                >
                  {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                </div>

                <div
                  className={`rounded-2xl p-3.5 text-xs shadow-lg ${
                    isUser
                      ? "bg-blue-600 text-white font-medium rounded-tr-sm"
                      : "bg-slate-900/90 border border-slate-800/90 text-slate-100 rounded-tl-sm prose prose-invert prose-xs max-w-none prose-p:my-1 prose-headings:my-1.5 prose-table:my-2 prose-th:px-2 prose-th:py-1 prose-td:px-2 prose-td:py-1 prose-table:border prose-table:border-slate-700 prose-th:border-b prose-th:border-slate-700"
                  }`}
                >
                  {isUser ? (
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  ) : (
                    <div className="space-y-1.5 text-slate-200 leading-relaxed overflow-x-auto">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  )}

                  <div
                    className={`text-[10px] mt-2 font-mono flex items-center gap-1 ${
                      isUser ? "text-blue-200 justify-end" : "text-slate-400 justify-start"
                    }`}
                  >
                    <span>{msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</span>
                  </div>
                </div>
              </div>
            );
          })
        )}

        {isLoading && (
          <div className="flex items-center gap-2.5 text-xs text-cyan-400 bg-slate-950/60 border border-cyan-900/40 px-3.5 py-2.5 rounded-xl w-fit animate-pulse">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
            <span>Agent reasoning with FDOT & Gainesville spatial tools...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form
        onSubmit={handleSubmit}
        className="p-3 border-t border-slate-800/80 bg-slate-950/60 flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about this intersection or corridor..."
          disabled={isLoading}
          className="flex-1 bg-slate-900/90 text-slate-100 placeholder-slate-400 text-xs rounded-xl px-3.5 py-2.5 border border-slate-700/60 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all"
        />

        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="px-4 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold rounded-xl shadow-md shadow-cyan-900/20 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-1.5"
        >
          <span>Ask</span>
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}

