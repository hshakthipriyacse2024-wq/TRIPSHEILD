'use client';

import { useState, useEffect } from 'react';
import { guardianApi, journeyApi } from '@/services/api';
import { Shield, Send, Bot, User, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function GuardianPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [journeyId, setJourneyId] = useState<string>('');

  useEffect(() => {
    journeyApi.list().then(res => {
      if (res.data && res.data.length > 0) {
        setJourneyId(res.data[0].id);
      }
    }).catch(console.error);
  }, []);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg = { role: 'user', content: text, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await guardianApi.chat({
        message: text,
        journey_id: journeyId || undefined
      });
      
      const botResponse = res.data.response || res.data.reply || "I am monitoring your journey for disruptions.";
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: botResponse,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } catch (e: any) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: e.response?.data?.detail || 'I encountered an issue accessing your Digital Twin context. Please try again.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    'What happens if my flight is delayed by 3 hours?',
    'Show me my cheapest recovery option',
    'Which option preserves my hotel reservation?',
    'Why did you recommend this flight strategy?'
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="p-4 bg-indigo-600 text-white flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-indigo-500/50 rounded-lg">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="font-bold text-base leading-tight">TripShield Guardian AI</h2>
            <p className="text-xs text-indigo-100">Live Journey Digital Twin Assistant</p>
          </div>
        </div>
        <span className="text-xs px-2.5 py-1 bg-indigo-500/50 text-white rounded-full font-medium flex items-center gap-1">
          <Sparkles className="h-3 w-3" /> Active Monitor
        </span>
      </div>
      
      {/* Chat Messages */}
      <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-gray-50/50">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 my-auto py-12 max-w-md mx-auto">
            <div className="w-14 h-14 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-3">
              <Bot className="w-8 h-8" />
            </div>
            <h3 className="font-bold text-gray-900 text-base">TripShield Guardian AI</h3>
            <p className="text-xs text-gray-500 mt-1">
              Ask me anything about your trip, disruption impacts, recovery options, or preference tweaks.
            </p>

            <div className="mt-6 space-y-2">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Suggested Questions</p>
              <div className="flex flex-col gap-2">
                {samplePrompts.map(p => (
                  <button
                    key={p}
                    onClick={() => handleSend(p)}
                    className="px-3.5 py-2 bg-white border border-gray-200 hover:border-indigo-300 rounded-lg text-xs font-medium text-gray-700 hover:text-indigo-600 transition shadow-sm text-left flex items-center justify-between"
                  >
                    <span>{p}</span>
                    <Sparkles className="h-3 w-3 text-indigo-400 opacity-70" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {messages.map((m, i) => (
          <div key={i} className={cn("flex w-full gap-2.5", m.role === 'user' ? "justify-end" : "justify-start")}>
            {m.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
                <Bot className="w-5 h-5" />
              </div>
            )}
            
            <div className={cn("max-w-[75%] rounded-xl p-3.5 text-sm shadow-sm space-y-1",
              m.role === 'user'
                ? "bg-indigo-600 text-white rounded-br-none"
                : "bg-white border border-gray-200 text-gray-900 rounded-bl-none"
            )}>
              <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>
              <div className={cn("text-[10px] text-right font-medium opacity-70", m.role === 'user' ? "text-indigo-100" : "text-gray-400")}>
                {m.timestamp}
              </div>
            </div>

            {m.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                <User className="w-5 h-5" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-indigo-600 font-medium">
            <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <span>Guardian is analyzing your Digital Twin graph...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="p-3 bg-white border-t border-gray-200">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(input);
          }}
          className="flex gap-2"
        >
          <input 
            type="text" 
            value={input} 
            onChange={e => setInput(e.target.value)}
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" 
            placeholder="Ask TripShield Guardian about delays, costs, or options..." 
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-4 py-2.5 rounded-lg transition flex items-center justify-center shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
