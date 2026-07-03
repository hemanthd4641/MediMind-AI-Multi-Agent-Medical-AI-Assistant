// src/pages/Chat.tsx
import React, { useState, useRef, useEffect } from 'react';

interface Citation {
  document: string;
  page?: number | null;
  chunk_index?: number | null;
}

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  intent?: string;
  agents_used?: string[];
  emergency_level?: string | null;
  loading?: boolean;
  confidence?: number;
  sources?: Citation[];
  evidence_summary?: string | null;
}

const EMERGENCY_HIGH = ['HIGH', 'CRITICAL'];

const AgentBadge: React.FC<{ name: string }> = ({ name }) => (
  <span style={{
    display: 'inline-block',
    background: 'rgba(99,102,241,0.15)',
    color: '#818cf8',
    border: '1px solid rgba(99,102,241,0.3)',
    borderRadius: '9999px',
    padding: '2px 10px',
    fontSize: '11px',
    marginRight: '4px',
    marginBottom: '4px',
  }}>
    {name}
  </span>
);

const EmergencyBanner: React.FC<{ level: string }> = ({ level }) => (
  <div style={{
    background: 'linear-gradient(135deg,#ef4444,#b91c1c)',
    color: '#fff',
    borderRadius: '10px',
    padding: '10px 16px',
    marginBottom: '10px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    fontWeight: 600,
    boxShadow: '0 0 20px rgba(239,68,68,0.4)',
  }}>
    <span style={{ fontSize: '20px' }}>🚨</span>
    {level === 'CRITICAL'
      ? 'CRITICAL EMERGENCY — Call 911 immediately!'
      : 'HIGH URGENCY — Seek emergency care now!'}
  </div>
);

const TypingDots: React.FC = () => (
  <div style={{ display: 'flex', gap: '4px', padding: '4px 0' }}>
    {[0, 1, 2].map(i => (
      <div key={i} style={{
        width: 8, height: 8, borderRadius: '50%',
        background: '#818cf8',
        animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
      }} />
    ))}
    <style>{`
      @keyframes bounce {
        0%,80%,100% { transform: translateY(0); }
        40% { transform: translateY(-8px); }
      }
    `}</style>
  </div>
);

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'ai',
      content: 'Hello! I\'m MediMind AI, your intelligent medical assistant. How can I help you today?\n\n⚠️ *This is for educational purposes only. Always consult a healthcare professional for medical advice.*',
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: trimmed,
    };
    const loadingMsg: Message = {
      id: 'loading',
      role: 'ai',
      content: '',
      loading: true,
    };

    setMessages(prev => [...prev, userMsg, loadingMsg]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token') || '';
      
      const res = await fetch('http://localhost:8000/api/ai/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message: trimmed }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Error ${res.status}`);
      }

      const data = await res.json();
      const aiMsg: Message = {
        id: Date.now().toString(),
        role: 'ai',
        content: data.response || 'I apologize, I could not generate a response.',
        intent: data.intent,
        agents_used: data.agents_used || [],
        emergency_level: data.emergency_level,
        confidence: data.confidence,
        sources: data.sources || [],
        evidence_summary: data.evidence_summary,
      };

      setMessages(prev => prev.filter(m => m.id !== 'loading').concat(aiMsg));
    } catch (err: any) {
      const errMsg: Message = {
        id: Date.now().toString(),
        role: 'ai',
        content: `⚠️ ${err.message || 'An error occurred. Please try again.'}`,
      };
      setMessages(prev => prev.filter(m => m.id !== 'loading').concat(errMsg));
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

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      background: 'linear-gradient(135deg,#0f0f1a 0%,#1a1a2e 100%)',
      color: '#e2e8f0',
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 24px',
        borderBottom: '1px solid rgba(255,255,255,0.08)',
        background: 'rgba(255,255,255,0.03)',
        backdropFilter: 'blur(10px)',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}>
        <div style={{
          width: 40, height: 40, borderRadius: '50%',
          background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 20,
        }}>🧠</div>
        <div>
          <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#f1f5f9' }}>
            MediMind AI
          </h1>
          <p style={{ margin: 0, fontSize: '12px', color: '#64748b' }}>
            Multi-Agent Medical Assistant
          </p>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e', boxShadow: '0 0 6px #22c55e' }} />
          <span style={{ fontSize: '12px', color: '#64748b' }}>Online</span>
        </div>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
      }}>
        {messages.map(msg => (
          <div key={msg.id} style={{
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            alignItems: 'flex-start',
            gap: '10px',
          }}>
            {msg.role === 'ai' && (
              <div style={{
                width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
                background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 16,
              }}>🧠</div>
            )}
            <div style={{ maxWidth: '70%' }}>
              {/* Emergency banner */}
              {msg.emergency_level && EMERGENCY_HIGH.includes(msg.emergency_level) && (
                <EmergencyBanner level={msg.emergency_level} />
              )}
              {/* Bubble */}
              <div style={{
                padding: '12px 16px',
                borderRadius: msg.role === 'user'
                  ? '18px 18px 4px 18px'
                  : '18px 18px 18px 4px',
                background: msg.role === 'user'
                  ? 'linear-gradient(135deg,#6366f1,#8b5cf6)'
                  : 'rgba(255,255,255,0.06)',
                border: msg.role === 'ai' ? '1px solid rgba(255,255,255,0.08)' : 'none',
                backdropFilter: 'blur(10px)',
                fontSize: '14px',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap',
              }}>
                {msg.loading ? <TypingDots /> : msg.content}
              </div>
              {/* Meta info */}
              {msg.role === 'ai' && !msg.loading && msg.intent && (
                <div style={{ marginTop: '6px', fontSize: '11px', color: '#64748b' }}>
                  <span style={{
                    background: 'rgba(34,197,94,0.15)', color: '#4ade80',
                    border: '1px solid rgba(34,197,94,0.3)',
                    borderRadius: '9999px', padding: '2px 8px', marginRight: '6px',
                  }}>
                    {msg.intent.replace(/_/g, ' ')}
                  </span>
                  {msg.emergency_level && !EMERGENCY_HIGH.includes(msg.emergency_level) && (
                    <span style={{
                      background: 'rgba(234,179,8,0.15)', color: '#facc15',
                      border: '1px solid rgba(234,179,8,0.3)',
                      borderRadius: '9999px', padding: '2px 8px', marginRight: '6px',
                    }}>
                      {msg.emergency_level}
                    </span>
                  )}
                </div>
              )}
              {/* Agent badges */}
              {msg.agents_used && msg.agents_used.length > 0 && (
                <div style={{ marginTop: '6px' }}>
                  {msg.agents_used.map(a => <AgentBadge key={a} name={a} />)}
                </div>
              )}
              {/* RAG Citations */}
              {msg.role === 'ai' && !msg.loading && msg.sources && msg.sources.length > 0 && (
                <div style={{
                  marginTop: '12px', padding: '10px',
                  background: 'rgba(0,0,0,0.15)', borderRadius: '8px',
                  border: '1px solid rgba(255,255,255,0.05)',
                  fontSize: '12px', color: '#94a3b8'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 600, color: '#e2e8f0' }}>📚 Evidence Found</span>
                    {msg.confidence !== undefined && (
                      <span style={{ 
                        color: msg.confidence > 0.7 ? '#4ade80' : msg.confidence > 0.4 ? '#facc15' : '#ef4444' 
                      }}>
                        {Math.round(msg.confidence * 100)}% Match
                      </span>
                    )}
                  </div>
                  {msg.evidence_summary && (
                    <div style={{ marginBottom: '8px', fontStyle: 'italic' }}>
                      {msg.evidence_summary}
                    </div>
                  )}
                  <ul style={{ margin: 0, paddingLeft: '16px', listStyleType: 'disc' }}>
                    {msg.sources.map((src, idx) => (
                      <li key={idx} style={{ marginBottom: '4px' }}>
                        <span style={{ color: '#bae6fd' }}>{src.document}</span>
                        {src.page !== undefined && src.page !== null && ` (Page ${src.page})`}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            {msg.role === 'user' && (
              <div style={{
                width: 36, height: 36, borderRadius: '50%', flexShrink: 0,
                background: 'rgba(255,255,255,0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 16,
              }}>👤</div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Disclaimer */}
      <div style={{
        padding: '8px 24px',
        textAlign: 'center',
        fontSize: '11px',
        color: '#475569',
        borderTop: '1px solid rgba(255,255,255,0.04)',
      }}>
        ⚠️ MediMind AI is for educational purposes only. Not a substitute for professional medical advice.
      </div>

      {/* Input area */}
      <div style={{
        padding: '16px 24px',
        borderTop: '1px solid rgba(255,255,255,0.08)',
        background: 'rgba(255,255,255,0.02)',
        display: 'flex',
        gap: '12px',
        alignItems: 'flex-end',
      }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Ask MediMind AI anything about your health…"
          rows={2}
          style={{
            flex: 1,
            background: 'rgba(255,255,255,0.06)',
            border: '1px solid rgba(255,255,255,0.12)',
            borderRadius: '12px',
            padding: '12px 16px',
            color: '#e2e8f0',
            fontSize: '14px',
            resize: 'none',
            outline: 'none',
            fontFamily: 'inherit',
            lineHeight: '1.5',
            transition: 'border-color 0.2s',
          }}
          onFocus={e => (e.target.style.borderColor = 'rgba(99,102,241,0.5)')}
          onBlur={e => (e.target.style.borderColor = 'rgba(255,255,255,0.12)')}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{
            width: 48, height: 48,
            borderRadius: '12px',
            background: loading || !input.trim()
              ? 'rgba(99,102,241,0.3)'
              : 'linear-gradient(135deg,#6366f1,#8b5cf6)',
            border: 'none',
            cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '20px',
            transition: 'all 0.2s',
            boxShadow: loading || !input.trim() ? 'none' : '0 4px 15px rgba(99,102,241,0.4)',
            flexShrink: 0,
          }}
          title="Send (Enter)"
        >
          {loading ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
};

export default Chat;
