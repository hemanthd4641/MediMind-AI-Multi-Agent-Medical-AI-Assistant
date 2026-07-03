import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export function VectorDatabaseDashboard() {
  const [health, setHealth] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [healthRes, statsRes] = await Promise.all([
          api.get('/api/vector/health'),
          api.get('/api/vector/stats')
        ]);
        setHealth(healthRes.data);
        setStats(statsRes.data);
      } catch (err) {
        console.error("Failed to load Vector DB data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-12 text-center text-slate-400">Loading Vector Database Info...</div>;
  }

  const isHealthy = health?.status === "healthy";

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12 mt-8">
      
      {/* Header */}
      <div className="flex justify-between items-end border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-4xl font-bold text-slate-100 mb-2">Vector Database Admin</h1>
          <p className="text-slate-400">Manage Pinecone Cloud resources and namespaces.</p>
        </div>
        <div className="flex items-center gap-2">
            <span className="text-slate-400 text-sm">Status:</span>
            {isHealthy ? (
                <span className="bg-emerald-900/30 text-emerald-400 px-3 py-1 rounded font-bold text-sm border border-emerald-800">HEALTHY</span>
            ) : (
                <span className="bg-red-900/30 text-red-400 px-3 py-1 rounded font-bold text-sm border border-red-800">UNHEALTHY / WARNING</span>
            )}
        </div>
      </div>

      {!isHealthy && health?.reason && (
          <div className="bg-red-900/20 border border-red-800 p-4 rounded text-red-400 font-mono text-sm">
              {health.reason}
          </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="text-sm text-slate-400 mb-1">Total Vector Count</div>
          <div className="text-3xl font-mono text-blue-400">{health?.total_vector_count || 0}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="text-sm text-slate-400 mb-1">Index Name</div>
          <div className="text-2xl font-mono text-emerald-400 mt-2">{health?.index_name || stats?.index_name || "N/A"}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="text-sm text-slate-400 mb-1">Dimensions</div>
          <div className="text-3xl font-mono text-purple-400">{health?.dimension || stats?.embedding_dimension || 0}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <div className="text-sm text-slate-400 mb-1">Ping Latency</div>
          <div className="text-3xl font-mono text-orange-400">{health?.latency_ms || 0}ms</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Namespaces Details */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden h-fit">
            <div className="p-4 border-b border-slate-800 font-bold text-slate-200">Namespaces in Pinecone</div>
            <div className="p-4 space-y-3">
                {health?.namespaces && Object.keys(health.namespaces).length > 0 ? (
                    Object.entries(health.namespaces).map(([name, nsData]: [string, any]) => (
                        <div key={name} className="flex justify-between items-center bg-slate-800/50 p-3 rounded border border-slate-700">
                            <span className="font-bold text-blue-300">{name}</span>
                            <span className="text-slate-400 text-sm">{nsData.vector_count} vectors</span>
                        </div>
                    ))
                ) : (
                    <div className="text-slate-500 italic">No namespaces found (Index might be empty).</div>
                )}
            </div>
          </div>

          {/* Configuration */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden h-fit">
            <div className="p-4 border-b border-slate-800 font-bold text-slate-200">Active Configuration</div>
            <div className="p-4 space-y-4 text-sm">
                <div>
                    <div className="text-slate-500 mb-1">Embedding Model</div>
                    <div className="font-mono text-emerald-400 bg-emerald-900/10 p-2 rounded border border-emerald-900">{stats?.embedding_model}</div>
                </div>
                <div>
                    <div className="text-slate-500 mb-1">Cloud Environment</div>
                    <div className="font-mono text-slate-300 bg-slate-800 p-2 rounded">{stats?.environment}</div>
                </div>
                <div>
                    <div className="text-slate-500 mb-1">Target Namespaces</div>
                    <div className="space-y-1 mt-2">
                        {stats?.active_namespaces?.map((ns: str) => (
                            <div key={ns} className="font-mono text-xs text-slate-400">✅ {ns}</div>
                        ))}
                    </div>
                </div>
            </div>
          </div>
      </div>
    </div>
  );
}
