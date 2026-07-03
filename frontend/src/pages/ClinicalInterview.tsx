import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';

interface Symptom {
  symptom: string;
  body_location?: string;
  severity?: string;
  duration?: string;
}

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  loading?: boolean;
}

export function ClinicalInterview() {
  const navigate = useNavigate();
  const [consultationId, setConsultationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Consultation State
  const [stage, setStage] = useState<string>('Initializing...');
  const [progress, setProgress] = useState<number>(0);
  const [urgency, setUrgency] = useState<string>('Routine');
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    startConsultation();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startConsultation = async () => {
    try {
      setLoading(true);
      const res = await api.post('/api/consultation/start');
      setConsultationId(res.data.consultation_id);
      setMessages([{
        id: 'start',
        role: 'ai',
        content: res.data.response
      }]);
      setStage(res.data.stage);
      setProgress(res.data.progress);
      setUrgency(res.data.urgency);
    } catch (err) {
      setMessages([{ id: 'error', role: 'ai', content: 'Failed to start consultation.' }]);
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !consultationId || loading) return;

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input.trim() };
    const loadingMsg: Message = { id: 'loading', role: 'ai', content: '', loading: true };

    setMessages(prev => [...prev, userMsg, loadingMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post(`/api/consultation/${consultationId}/message`, {
        message: userMsg.content
      });
      
      const data = res.data;
      
      const aiMsg: Message = {
        id: Date.now().toString(),
        role: 'ai',
        content: data.response
      };

      setMessages(prev => prev.filter(m => m.id !== 'loading').concat(aiMsg));
      setStage(data.stage);
      setProgress(data.progress);
      setUrgency(data.urgency);
      setSymptoms(data.symptoms || []);

      if (data.is_complete) {
        // Redirect to summary after a short delay
        setTimeout(() => {
          navigate(`/consultation/${consultationId}/summary`);
        }, 3000);
      }

    } catch (err: any) {
      setMessages(prev => prev.filter(m => m.id !== 'loading').concat({
        id: Date.now().toString(),
        role: 'ai',
        content: 'Sorry, an error occurred while processing your message.'
      }));
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const isEmergency = urgency === 'Emergency' || urgency === 'Urgent';

  return (
    <div className="flex h-[calc(100vh-140px)] gap-6 animate-in fade-in duration-500">
      
      {/* Sidebar: Status & Symptoms */}
      <div className="w-80 flex flex-col gap-4">
        {/* Progress Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
          <h2 className="text-lg font-semibold text-slate-200 mb-4">Consultation Progress</h2>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-teal-400 font-medium">{stage}</span>
            <span className="text-slate-400">{progress}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2.5">
            <div 
              className="bg-gradient-to-r from-teal-400 to-blue-500 h-2.5 rounded-full transition-all duration-500" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Urgency Badge */}
        <div className={`border rounded-xl p-5 shadow-lg transition-colors ${
          urgency === 'Emergency' ? 'bg-red-900/20 border-red-500/50' :
          urgency === 'Urgent' ? 'bg-orange-900/20 border-orange-500/50' :
          urgency === 'Soon' ? 'bg-yellow-900/20 border-yellow-500/50' :
          'bg-slate-900 border-slate-800'
        }`}>
          <h2 className="text-sm text-slate-400 uppercase tracking-wider mb-2">Assessed Urgency</h2>
          <div className="flex items-center gap-3">
            <span className="text-2xl">
              {urgency === 'Emergency' ? '🚨' : urgency === 'Urgent' ? '⚠️' : '🏥'}
            </span>
            <span className={`font-bold text-xl ${
              urgency === 'Emergency' ? 'text-red-400' :
              urgency === 'Urgent' ? 'text-orange-400' :
              urgency === 'Soon' ? 'text-yellow-400' :
              'text-teal-400'
            }`}>
              {urgency}
            </span>
          </div>
        </div>

        {/* Symptoms List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex-1 overflow-y-auto">
          <h2 className="text-sm text-slate-400 uppercase tracking-wider mb-4">Extracted Symptoms</h2>
          {symptoms.length === 0 ? (
            <p className="text-slate-500 text-sm italic">No symptoms extracted yet.</p>
          ) : (
            <div className="space-y-4">
              {symptoms.map((s, i) => (
                <div key={i} className="bg-slate-800/50 rounded-lg p-3 text-sm">
                  <div className="font-semibold text-slate-200 capitalize">{s.symptom}</div>
                  {s.body_location && <div className="text-slate-400 mt-1"><span className="text-slate-500">Location:</span> {s.body_location}</div>}
                  {s.severity && <div className="text-slate-400"><span className="text-slate-500">Severity:</span> {s.severity}</div>}
                  {s.duration && <div className="text-slate-400"><span className="text-slate-500">Duration:</span> {s.duration}</div>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden">
        
        {/* Emergency Banner */}
        {isEmergency && (
          <div className="bg-red-500/10 border-b border-red-500/20 p-4 flex items-center justify-center gap-3">
            <span className="text-2xl animate-pulse">🚨</span>
            <span className="text-red-400 font-medium">
              This information may indicate a medical emergency. Please seek immediate medical attention or contact your local emergency services (e.g., 911).
            </span>
          </div>
        )}

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[75%] rounded-2xl p-4 ${
                msg.role === 'user' 
                  ? 'bg-gradient-to-br from-teal-500 to-blue-600 text-white rounded-br-sm' 
                  : 'bg-slate-800 text-slate-200 rounded-bl-sm border border-slate-700'
              }`}>
                {msg.loading ? (
                  <div className="flex gap-1 items-center h-6">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                ) : (
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                )}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-slate-800/50 border-t border-slate-800">
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Describe your symptoms or answer the question..."
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl p-3 text-slate-200 resize-none focus:outline-none focus:border-teal-500 transition-colors"
              rows={2}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-gradient-to-r from-teal-500 to-blue-600 text-white rounded-xl px-6 font-medium hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Send
            </button>
          </div>
          <div className="text-center mt-2 text-xs text-slate-500">
            MediMind AI is for educational purposes only and does not provide medical diagnoses.
          </div>
        </div>

      </div>
    </div>
  );
}
