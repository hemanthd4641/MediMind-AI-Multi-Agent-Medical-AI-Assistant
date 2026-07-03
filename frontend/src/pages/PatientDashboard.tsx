import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

export function PatientDashboard() {
  const [timeline, setTimeline] = useState<any[]>([]);
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [timelineRes, insightsRes] = await Promise.all([
          api.get('/api/timeline'),
          api.get('/api/timeline/insights')
        ]);
        setTimeline(timelineRes.data);
        setInsights(insightsRes.data);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleExport = async () => {
    try {
      const res = await api.get('/api/timeline/export', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Health_Summary.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Failed to export summary.");
    }
  };

  if (loading) {
    return <div className="p-12 text-center text-slate-400">Loading your intelligence dashboard...</div>;
  }

  const reportsCount = timeline.filter(t => t.event_type === 'REPORT').length;
  const consultationsCount = timeline.filter(t => t.event_type === 'CONSULTATION').length;
  const prescriptionsCount = timeline.filter(t => t.event_type === 'PRESCRIPTION').length;

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12 mt-8">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-bold text-slate-100 mb-3 bg-gradient-to-r from-emerald-400 to-teal-500 bg-clip-text text-transparent">Health Intelligence Dashboard</h1>
          <p className="text-slate-400 text-lg">Your personalized, longitudinal health memory system.</p>
        </div>
        <button onClick={handleExport} className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-4 rounded-lg transition-colors flex items-center gap-2">
          <span>📥</span> Download PDF Summary
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Col - Overview Cards */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link to="/reports" className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl hover:border-emerald-500/50 transition-colors">
              <div className="text-3xl mb-2">📄</div>
              <div className="text-2xl font-bold text-slate-200">{reportsCount}</div>
              <div className="text-slate-400 text-sm">Medical Reports</div>
            </Link>
            <Link to="/consultation" className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl hover:border-emerald-500/50 transition-colors">
              <div className="text-3xl mb-2">🩺</div>
              <div className="text-2xl font-bold text-slate-200">{consultationsCount}</div>
              <div className="text-slate-400 text-sm">Consultations</div>
            </Link>
            <Link to="/medications" className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl hover:border-emerald-500/50 transition-colors">
              <div className="text-3xl mb-2">💊</div>
              <div className="text-2xl font-bold text-slate-200">{prescriptionsCount}</div>
              <div className="text-slate-400 text-sm">Prescriptions</div>
            </Link>
          </div>

          {/* AI Insights Engine */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden">
            <div className="p-6 border-b border-slate-800 bg-slate-800/50 flex justify-between items-center">
              <h2 className="text-xl font-bold text-slate-200 flex items-center gap-2">
                <span>🧠</span> Latest AI Health Insights
              </h2>
            </div>
            <div className="p-6 space-y-4">
              {insights.length === 0 ? (
                <div className="text-center text-slate-500 italic py-8">
                  No insights generated yet. Upload reports or consult the AI to build your profile.
                </div>
              ) : (
                insights.slice(0, 5).map(insight => (
                  <div key={insight.id} className="p-4 rounded-xl border border-slate-700/50 bg-slate-800/30">
                    <div className="flex items-start justify-between mb-2">
                      <div className="font-bold text-emerald-400">{insight.title}</div>
                      <span className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300 uppercase tracking-wider">{insight.category}</span>
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed">{insight.description}</p>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>

        {/* Right Col - Quick Links / Mini Timeline */}
        <div className="space-y-6">
          
          <Link to="/timeline" className="block bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl hover:border-emerald-500/50 transition-colors">
            <div className="text-3xl mb-4">⏱️</div>
            <h3 className="text-lg font-bold text-slate-200 mb-2">Full Health Timeline</h3>
            <p className="text-sm text-slate-400 mb-4">View your complete chronological medical history across all modules.</p>
            <div className="text-emerald-400 text-sm font-semibold flex items-center gap-1">
              View Timeline <span className="text-lg">→</span>
            </div>
          </Link>

          <Link to="/trends" className="block bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl hover:border-emerald-500/50 transition-colors">
            <div className="text-3xl mb-4">📈</div>
            <h3 className="text-lg font-bold text-slate-200 mb-2">Laboratory Trends</h3>
            <p className="text-sm text-slate-400 mb-4">Visualize how your biomarkers (HbA1c, Cholesterol) change over time.</p>
            <div className="text-emerald-400 text-sm font-semibold flex items-center gap-1">
              View Charts <span className="text-lg">→</span>
            </div>
          </Link>

        </div>

      </div>
    </div>
  );
}
