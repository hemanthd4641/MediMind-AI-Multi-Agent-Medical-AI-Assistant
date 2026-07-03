import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export function PromptManager() {
  const [prompts, setPrompts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Form State
  const [agentName, setAgentName] = useState("");
  const [title, setTitle] = useState("");
  const [promptText, setPromptText] = useState("");

  useEffect(() => {
    fetchPrompts();
  }, []);

  const fetchPrompts = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/ai/prompts');
      setPrompts(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/api/ai/prompts', {
        agent_name: agentName,
        title,
        prompt: promptText
      });
      alert("New Prompt Version Created & Activated!");
      setAgentName("");
      setTitle("");
      setPromptText("");
      fetchPrompts();
    } catch (err) {
      console.error(err);
      alert("Failed to create prompt");
    }
  };

  const handleRollback = async (agent: str, version: number) => {
    try {
      await api.put(`/api/ai/prompts/${agent}/rollback`, { version });
      alert(`Rolled back ${agent} to version ${version}`);
      fetchPrompts();
    } catch (err) {
      console.error(err);
      alert("Rollback failed");
    }
  };

  if (loading && prompts.length === 0) return <div className="p-12 text-slate-400">Loading Prompts...</div>;

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12 mt-8 animate-in fade-in">
      <h1 className="text-3xl font-bold text-slate-100">Centralized Prompt Management</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Create Form */}
        <div className="lg:col-span-1 bg-slate-900 border border-slate-800 p-6 rounded-xl h-fit">
          <h2 className="text-xl font-bold text-slate-200 mb-4">New Prompt Version</h2>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-1">Agent Name</label>
              <input 
                required
                type="text" 
                value={agentName}
                onChange={e => setAgentName(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white" 
                placeholder="e.g. TimelineAgent" 
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Version Title / Note</label>
              <input 
                required
                type="text" 
                value={title}
                onChange={e => setTitle(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded p-2 text-white" 
                placeholder="e.g. Added safety constraints" 
              />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1">Prompt Body</label>
              <textarea 
                required
                value={promptText}
                onChange={e => setPromptText(e.target.value)}
                className="w-full h-64 bg-slate-800 border border-slate-700 rounded p-2 text-white font-mono text-sm"
                placeholder="You are an expert AI..."
              />
            </div>
            <button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 rounded">
              Save & Activate Version
            </button>
          </form>
        </div>

        {/* List */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-bold text-slate-200">Prompt Registry</h2>
          {prompts.map(p => (
            <div key={p.id} className={`p-4 rounded-xl border ${p.is_active ? 'border-emerald-500 bg-emerald-900/10' : 'border-slate-800 bg-slate-900'}`}>
              <div className="flex justify-between items-start mb-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-lg text-slate-200">{p.agent_name}</span>
                    <span className="bg-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded-full">v{p.version}</span>
                    {p.is_active && <span className="bg-emerald-600 text-white text-xs px-2 py-0.5 rounded-full">ACTIVE</span>}
                  </div>
                  <div className="text-slate-400 text-sm mt-1">"{p.title}"</div>
                </div>
                {!p.is_active && (
                  <button onClick={() => handleRollback(p.agent_name, p.version)} className="text-sm bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1 rounded">
                    Rollback to this
                  </button>
                )}
              </div>
              <div className="mt-4 bg-slate-950 p-3 rounded border border-slate-800 max-h-32 overflow-y-auto custom-scrollbar font-mono text-xs text-slate-400">
                {p.prompt}
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
