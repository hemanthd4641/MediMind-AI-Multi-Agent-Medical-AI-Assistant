import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export function ExecutionInspector() {
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedExec, setSelectedExec] = useState<any>(null);

  useEffect(() => {
    const fetchExecutions = async () => {
      try {
        const res = await api.get('/api/ai/executions?limit=100');
        setExecutions(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchExecutions();
  }, []);

  if (loading) return <div className="p-12 text-slate-400">Loading Executions...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12 mt-8 animate-in fade-in">
      <h1 className="text-3xl font-bold text-slate-100">LLM Execution Inspector</h1>
      <p className="text-slate-400">Trace every single agent call, measure latency, tokens, and inspect guardrail interventions.</p>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* List */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800 text-slate-400">
                <tr>
                  <th className="px-4 py-3">Timestamp</th>
                  <th className="px-4 py-3">Agent</th>
                  <th className="px-4 py-3">Tokens (In/Out)</th>
                  <th className="px-4 py-3">Latency</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {executions.map(e => (
                  <tr 
                    key={e.id} 
                    onClick={() => setSelectedExec(e)}
                    className={`cursor-pointer transition-colors ${selectedExec?.id === e.id ? 'bg-slate-800' : 'hover:bg-slate-800/50'}`}
                  >
                    <td className="px-4 py-3 text-xs whitespace-nowrap">{new Date(e.created_at).toLocaleTimeString()}</td>
                    <td className="px-4 py-3 font-semibold text-slate-200">{e.agent_name}</td>
                    <td className="px-4 py-3 font-mono text-xs">{e.input_tokens} / {e.output_tokens}</td>
                    <td className="px-4 py-3 font-mono text-xs text-orange-400">{e.latency_ms}ms</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        e.status === 'SUCCESS' ? 'bg-emerald-900/30 text-emerald-400' :
                        e.status === 'GUARDRAIL_BLOCKED' ? 'bg-orange-900/30 text-orange-400' :
                        'bg-red-900/30 text-red-400'
                      }`}>
                        {e.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Details Panel */}
        <div className="lg:col-span-1">
          {selectedExec ? (
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl sticky top-8">
              <h3 className="text-xl font-bold text-slate-200 mb-4">Execution Details</h3>
              <div className="space-y-4 text-sm">
                <div>
                  <span className="text-slate-500 block mb-1">ID</span>
                  <span className="font-mono text-slate-300 text-xs break-all">{selectedExec.id}</span>
                </div>
                <div>
                  <span className="text-slate-500 block mb-1">Model</span>
                  <span className="text-blue-400 font-mono bg-blue-900/20 px-2 py-1 rounded">{selectedExec.model}</span>
                </div>
                
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-800">
                  <div>
                    <span className="text-slate-500 block text-xs mb-1">Cost Estimate</span>
                    <span className="text-emerald-400 font-mono">
                      ${((selectedExec.input_tokens / 1000000 * 0.59) + (selectedExec.output_tokens / 1000000 * 0.79)).toFixed(5)}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-xs mb-1">Tokens / Sec</span>
                    <span className="text-orange-400 font-mono">
                      {selectedExec.latency_ms > 0 ? ((selectedExec.output_tokens / selectedExec.latency_ms) * 1000).toFixed(1) : 0}
                    </span>
                  </div>
                </div>

                {selectedExec.error_message && (
                  <div className="pt-4 border-t border-slate-800">
                    <span className="text-slate-500 block mb-1">Error / Guardrail Reason</span>
                    <div className="bg-red-900/20 text-red-400 p-3 rounded text-xs font-mono break-words">
                      {selectedExec.error_message}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 p-12 rounded-xl text-center text-slate-500 italic">
              Select an execution from the table to view details.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
