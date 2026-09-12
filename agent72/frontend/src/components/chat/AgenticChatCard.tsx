import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Sparkles, Database, ArrowRight } from 'lucide-react';
import { api } from '../../api/client';
import { AgentQueryResponse } from '../../api/types';
import { StructuredMessageView } from './StructuredMessageView';

interface ChatMessage {
  id: string;
  sender: 'assistant' | 'user';
  text: string;
  time: string;
  confidence?: number;
  groundingSources?: any[];
  relatedMetrics?: string[];
  suggestedQuestions?: string[];
}

interface AgenticChatCardProps {
  institutionId: string;
  period: string;
}

export const AgenticChatCard: React.FC<AgenticChatCardProps> = ({ institutionId, period }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'msg-1',
      sender: 'assistant',
      text: "Welcome! I am **Agent 72**, the Institutional Strategic Planning and Decision-Support Agent for **Vignan's University** (NAAC A+, NIRF Rank 70).\n\nI deliver evidence-grounded intelligence for academic leadership, faculty, and students—analyzing baseline performance gaps, longitudinal trajectories, strategic options, scenario forecasts, and execution governance. I also provide official event intelligence for **CSE Presents Agentic AI Day 2026** (AI Musical, AI Reels, AI Quiz rules and prizes).\n\nHow can I assist you with institutional strategic intelligence or event details today?",
      time: '10:30 AM',
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isStandby, setIsStandby] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const getTimeString = () => {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSend = async (queryText?: string) => {
    const query = (queryText || inputText).trim();
    if (!query || isLoading) return;

    setIsStandby(false);
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: query,
      time: getTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);

    try {
      const response: AgentQueryResponse = await api.askAgent72(institutionId, query, period);
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: response.answer,
        time: getTimeString(),
        confidence: response.confidence,
        groundingSources: response.grounding_sources,
        relatedMetrics: response.related_metrics,
        suggestedQuestions: response.suggested_questions,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg: ChatMessage = {
        id: `error-${Date.now()}`,
        sender: 'assistant',
        text: "I encountered an issue connecting to the institutional strategic decision engine. Please verify the Agent 72 server is active.",
        time: getTimeString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      setIsStandby(true);
    }
  };

  const toggleVoice = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    if (isListening) {
      setIsListening(false);
    } else {
      try {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => setIsListening(true);
        recognition.onresult = (event: any) => {
          const speechResult = event.results[0][0].transcript;
          setInputText(speechResult);
          setIsListening(false);
          handleSend(speechResult);
        };
        recognition.onerror = () => setIsListening(false);
        recognition.onend = () => setIsListening(false);
        recognition.start();
      } catch (e) {
        setIsListening(false);
      }
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs flex flex-col h-[400px] sm:h-[440px] overflow-hidden">
      {/* Scrollable Messages Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5 divide-y divide-slate-100">
        {messages.map((m, idx) => (
          <div key={m.id} className={idx > 0 ? 'pt-3.5' : ''}>
            {m.sender === 'assistant' ? (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-[#1d4ed8] font-black tracking-wider uppercase text-[11px]">
                    ASSISTANT
                  </span>
                  <span className="text-[11px] text-slate-400 font-medium">{m.time}</span>
                </div>
                <div className="text-xs sm:text-sm text-slate-800 leading-relaxed">
                  <StructuredMessageView content={m.text} />
                </div>

                {/* Grounding Sources */}
                {m.groundingSources && m.groundingSources.length > 0 && (
                  <div className="pt-2 flex flex-wrap gap-1">
                    {m.groundingSources.slice(0, 3).map((src, sIdx) => (
                      <span
                        key={sIdx}
                        className="inline-flex items-center gap-1 bg-slate-50 border border-slate-200 px-1.5 py-0.2 rounded font-mono text-[9.5px] text-slate-600"
                      >
                        <Database className="w-2.5 h-2.5 text-blue-600" />
                        {src.type}: {src.metric || src.title || 'Data'}
                      </span>
                    ))}
                  </div>
                )}

                {/* Follow up chips */}
                {m.suggestedQuestions && m.suggestedQuestions.length > 0 && (
                  <div className="pt-2 flex flex-wrap gap-1.5">
                    {m.suggestedQuestions.slice(0, 3).map((q, qIdx) => (
                      <button
                        key={qIdx}
                        onClick={() => handleSend(q)}
                        className="inline-flex items-center gap-1 text-[10.5px] bg-blue-50/70 hover:bg-blue-100 text-blue-800 px-2 py-0.5 rounded-lg border border-blue-200/80 transition"
                      >
                        <ArrowRight className="w-2.5 h-2.5 text-blue-600" />
                        <span>{q}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-600 font-bold uppercase text-[11px]">YOU</span>
                  <span className="text-[11px] text-slate-400 font-medium">{m.time}</span>
                </div>
                <div className="text-xs sm:text-sm text-slate-900 bg-slate-100/70 p-2.5 rounded-xl">
                  {m.text}
                </div>
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 pt-2 text-xs text-blue-600 font-medium animate-pulse">
            <Sparkles className="w-4 h-4 animate-spin" />
            <span>Assistant is thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form Bar matching reference screenshot */}
      <div className="p-3 bg-white border-t border-slate-200/90">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Start the assistant to start chatting"
            disabled={isLoading}
            className="flex-1 bg-slate-50/90 hover:bg-slate-50 focus:bg-white border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition shadow-2xs"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="w-9 h-9 rounded-xl bg-[#3b82f6] hover:bg-blue-600 disabled:bg-slate-200 text-white flex items-center justify-center shadow-xs transition shrink-0"
            title="Send inquiry"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>

        {/* Bottom Status Bar matching reference screenshot */}
        <div className="pt-2 flex items-center justify-between text-[11px] text-slate-500 select-none">
          {/* Left: Standby indicator with green dot */}
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${isStandby ? 'bg-emerald-500 animate-pulse' : 'bg-blue-600 animate-ping'}`} />
            <span className="font-medium text-slate-600">Standby</span>
          </div>

          {/* Right: Voice + transcript toggle */}
          <button
            onClick={toggleVoice}
            className={`flex items-center gap-1 px-2 py-0.5 rounded-lg border transition ${
              isListening
                ? 'bg-red-50 text-red-600 border-red-200 animate-pulse'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border-slate-200'
            }`}
            title="Voice + transcript toggle"
          >
            {isListening ? <MicOff className="w-3 h-3 text-red-600" /> : <Mic className="w-3 h-3 text-slate-500" />}
            <span className="text-[10px]">Voice + transcript (assistant & your speech)</span>
          </button>
        </div>
      </div>
    </div>
  );
};
