import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export function HealthTimeline() {
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('ALL'); // ALL, REPORT, CONSULTATION, PRESCRIPTION

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        const res = await api.get('/api/timeline');
        setTimeline(res.data);
      } catch (err) {
        console.error("Failed to load timeline", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimeline();
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      await api.post('/api/timeline/history/compare');
      const res = await api.get('/api/timeline');
      setTimeline(res.data);
    } catch (err) {
      console.error("Failed to refresh timeline", err);
    } finally {
      setLoading(false);
    }
  };

  const filteredTimeline = filter === 'ALL' 
    ? timeline 
    : timeline.filter(t => t.event_type === filter);

  if (loading && timeline.length === 0) {
    return <div className="p-12 text-center text-slate-400">Loading timeline...</div>;
  }

  const getIcon = (type: string) => {
    switch(type) {
      case 'REPORT': return '📄';
      case 'CONSULTATION': return '🩺';
      case 'PRESCRIPTION': return '💊';
      default: return '📅';
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12 mt-8">
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2 bg-gradient-to-r from-emerald-400 to-teal-500 bg-clip-text text-transparent">Unified Health Timeline</h1>
          <p className="text-slate-400">A chronological record of all your health events.</p>
        </div>
        <button onClick={handleRefresh} className="text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 py-2 px-4 rounded-lg transition-colors border border-slate-700">
          🔄 Sync & Analyze Recent Changes
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {['ALL', 'REPORT', 'CONSULTATION', 'PRESCRIPTION'].map(f => (
          <button 
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-semibold transition-colors ${
              filter === f 
                ? 'bg-emerald-600 text-white' 
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200'
            }`}
          >
            {f === 'ALL' ? 'All Events' : f + 's'}
          </button>
        ))}
      </div>

      {/* Timeline */}
      {filteredTimeline.length === 0 ? (
        <div className="p-12 text-center text-slate-500 italic bg-slate-900 rounded-xl border border-slate-800">
          No events found in this category.
        </div>
      ) : (
        <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent pt-4">
          {filteredTimeline.map((event, index) => (
            <div key={event.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border border-slate-700 bg-slate-900 text-slate-300 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                {getIcon(event.event_type)}
              </div>
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-5 rounded-xl border border-slate-800 bg-slate-900/80 shadow-xl hover:border-emerald-500/30 transition-colors">
                <div className="flex flex-col md:flex-row md:items-center justify-between mb-2 gap-2">
                  <div className="font-bold text-slate-200 text-lg">{event.title}</div>
                  <time className="font-mono text-emerald-400/80 text-xs shrink-0 bg-emerald-900/20 px-2 py-1 rounded">
                    {new Date(event.event_date).toLocaleString()}
                  </time>
                </div>
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-3">
                  {event.event_type}
                </div>
                <p className="text-sm text-slate-300 leading-relaxed max-h-32 overflow-y-auto custom-scrollbar">
                  {event.summary || "No summary available."}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
