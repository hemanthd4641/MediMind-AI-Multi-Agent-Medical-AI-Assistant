import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

export function AIOperationsDashboard() {
  const [metrics, setMetrics] = useState<any>(null);
  const [evals, setEvals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metRes, evalsRes] = await Promise.all([
          api.get('/api/ai/metrics'),
          api.get('/api/ai/evaluations?limit=10')
        ]);
        setMetrics(metRes.data);
        setEvals(evalsRes.data);
      } catch (err) {
        console.error("Failed to load AI ops data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-12 text-center text-slate-400">Loading AI Operations...</div>;
  }

  const runTestSuite = async () => {
    try {
      alert("Triggering AI test suite. Check logs/backend for details.");
      await api.post('/api/ai/test-suite');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12 mt-8">
      
      {/* Header */}
      <div className="flex justify-between items-end border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-4xl font-bold text-slate-100 mb-2">AI Operations Center</h1>
          <p className="text-slate-400">LLMOps, Guardrails, and Observability</p>
        </div>
        <div className="flex gap-4">
          <Link to="/ai-ops/prompts" className="bg-slate-800 hover:bg-slate-700 text-white py-2 px-4 rounded transition-colors">
            Prompt Manager
          </Link>
          <Link to="/ai-ops/executions" className="bg-slate-800 hover:bg-slate-700 text-white py-2 px-4 rounded transition-colors">
            Execution Inspector
          </Link>
          <button onClick={runTestSuite} className="bg-emerald-600 hover:bg-emerald-500 text-white py-2 px-4 rounded transition-colors font-bold">
            Run Test Suite
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="text-sm text-slate-400 mb-1">Total Executions</div>
          <div className="text-3xl font-mono text-emerald-400">{metrics?.total_executions || 0}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="text-sm text-slate-400 mb-1">Total Tokens</div>
          <div className="text-3xl font-mono text-blue-400">{metrics?.total_tokens || 0}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="text-sm text-slate-400 mb-1">Avg Latency</div>
          <div className="text-3xl font-mono text-orange-400">{metrics?.average_latency_ms || 0}ms</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="text-sm text-slate-400 mb-1">Est. Groq Cost</div>
          <div className="text-3xl font-mono text-emerald-500">${metrics?.estimated_cost_usd || 0.00}</div>
        </div>
      </div>

      {/* Evaluations Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 font-bold text-slate-200">Recent LLM-as-a-Judge Evaluations</div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800 text-slate-400">
              <tr>
                <th className="px-4 py-3">Exec ID</th>
                <th className="px-4 py-3">Groundedness</th>
                <th className="px-4 py-3">Hallucination</th>
                <th className="px-4 py-3">Safety Score</th>
                <th className="px-4 py-3">Overall</th>
                <th className="px-4 py-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {evals.map((e) => (
                <tr key={e.id} className="hover:bg-slate-800/50">
                  <td className="px-4 py-3 font-mono text-xs">{e.execution_id.substring(0, 8)}...</td>
                  <td className="px-4 py-3">
                    <span className={e.groundedness >= 0.8 ? "text-emerald-400" : "text-orange-400"}>{e.groundedness}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={e.hallucination_score > 20 ? "text-red-400" : "text-emerald-400"}>{e.hallucination_score}</span>
                  </td>
                  <td className="px-4 py-3">{e.safety_score}</td>
                  <td className="px-4 py-3 font-bold">{e.overall_score}</td>
                  <td className="px-4 py-3 text-xs">{new Date(e.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
