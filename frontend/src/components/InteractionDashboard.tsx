import React from 'react';

interface Interaction {
  medicine_1: string;
  medicine_2: string;
  severity: string;
  explanation: string;
}

export function InteractionDashboard({ interactions }: { interactions: Interaction[] }) {
  if (!interactions || interactions.length === 0) {
    return (
      <div className="bg-emerald-900/20 border border-emerald-800/50 rounded-xl p-6 shadow-xl flex items-center gap-4">
        <div className="text-3xl">✅</div>
        <div>
          <h3 className="text-lg font-bold text-emerald-400">No Interactions Detected</h3>
          <p className="text-sm text-slate-300">These medicines appear safe to take with your current medications and conditions.</p>
        </div>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'major': return 'bg-red-900/40 border-red-500 text-red-400';
      case 'moderate': return 'bg-orange-900/40 border-orange-500 text-orange-400';
      case 'minor': return 'bg-yellow-900/40 border-yellow-500 text-yellow-400';
      default: return 'bg-slate-800 border-slate-600 text-slate-300';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'major': return '⛔';
      case 'moderate': return '⚠️';
      case 'minor': return 'ℹ️';
      default: return '•';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden">
      <div className="p-4 border-b border-slate-800 bg-slate-800/50 flex justify-between items-center">
        <h2 className="text-lg font-bold text-slate-200">Interaction Alerts</h2>
        <span className="text-xs bg-slate-800 px-2 py-1 rounded text-slate-400 border border-slate-700">
          {interactions.length} detected
        </span>
      </div>
      <div className="p-6 space-y-4">
        {interactions.map((interaction, i) => (
          <div key={i} className={`p-4 rounded-xl border-l-4 ${getSeverityColor(interaction.severity)}`}>
            <div className="flex items-start gap-3">
              <div className="text-xl mt-0.5">{getSeverityIcon(interaction.severity)}</div>
              <div>
                <div className="font-bold mb-1">
                  {interaction.medicine_1} <span className="text-slate-400 font-normal mx-2">↔</span> {interaction.medicine_2}
                </div>
                <div className="text-xs font-semibold uppercase tracking-wider mb-2 opacity-80">
                  {interaction.severity} Interaction
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">
                  {interaction.explanation}
                </p>
              </div>
            </div>
          </div>
        ))}
        <div className="text-xs text-slate-500 italic mt-4 text-center">
          * Always consult your doctor before modifying any medication regime.
        </div>
      </div>
    </div>
  );
}
