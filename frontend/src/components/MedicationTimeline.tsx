import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

interface MedHistory {
  id: string;
  medicine_name: string;
  start_date: string;
  end_date: string | null;
  status: string;
  source_prescription_id: string | null;
}

export function MedicationTimeline() {
  const [history, setHistory] = useState<MedHistory[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await api.get('/api/prescriptions/history/medications');
        setHistory(res.data);
      } catch (err) {
        console.error("Failed to load medication history", err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  if (loading) {
    return <div className="p-12 text-center text-slate-400">Loading medication history...</div>;
  }

  const activeMeds = history.filter(h => h.status === 'active');
  const pastMeds = history.filter(h => h.status !== 'active');

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12 mt-8">
      
      <div>
        <h1 className="text-3xl font-bold text-slate-100 mb-2 bg-gradient-to-r from-emerald-400 to-teal-500 bg-clip-text text-transparent">Medication Timeline</h1>
        <p className="text-slate-400">Track your current and historical medications over time.</p>
      </div>

      {/* Active Medications */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-emerald-400 flex items-center gap-2">
          <span>🟢</span> Currently Active
        </h2>
        {activeMeds.length === 0 ? (
          <p className="text-slate-500 italic">No active medications recorded.</p>
        ) : (
          <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
            {activeMeds.map((med, index) => (
              <div key={med.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-slate-900 group-[.is-active]:bg-emerald-500 text-slate-500 group-[.is-active]:text-emerald-50 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                  💊
                </div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border border-emerald-500/30 bg-emerald-900/10 shadow-xl">
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-bold text-slate-200">{med.medicine_name}</div>
                    <time className="font-caveat font-medium text-emerald-400 text-sm">
                      Since {new Date(med.start_date).toLocaleDateString()}
                    </time>
                  </div>
                  {med.source_prescription_id && (
                    <div className="text-slate-400 text-xs mt-2">
                      Source: Prescription Record
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Past Medications */}
      <div className="space-y-4 pt-8">
        <h2 className="text-xl font-bold text-slate-400 flex items-center gap-2">
          <span>⚪</span> Historical Medications
        </h2>
        {pastMeds.length === 0 ? (
          <p className="text-slate-500 italic">No past medications recorded.</p>
        ) : (
          <div className="space-y-4 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-700 before:to-transparent">
            {pastMeds.map((med, index) => (
              <div key={med.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-slate-700 bg-slate-800 text-slate-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                  📋
                </div>
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border border-slate-800 bg-slate-900/50 shadow-xl opacity-60 hover:opacity-100 transition-opacity">
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-bold text-slate-300">{med.medicine_name}</div>
                    <time className="font-caveat font-medium text-slate-500 text-xs">
                      {new Date(med.start_date).toLocaleDateString()} - {med.end_date ? new Date(med.end_date).toLocaleDateString() : 'N/A'}
                    </time>
                  </div>
                  <div className="text-slate-500 text-xs mt-2 uppercase tracking-wide">
                    {med.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
