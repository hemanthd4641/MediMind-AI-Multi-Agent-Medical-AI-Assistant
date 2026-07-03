import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { api } from '../services/api';

interface PrescriptionList {
  id: string;
  doctor_name: string;
  hospital_name: string;
  status: string;
  created_at: string;
}

export function MedicationCenter() {
  const navigate = useNavigate();
  const [prescriptions, setPrescriptions] = useState<PrescriptionList[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  const fetchPrescriptions = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/prescriptions');
      setPrescriptions(res.data);
    } catch (err) {
      console.error("Failed to load prescriptions", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrescriptions();
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      const res = await api.post('/api/prescriptions/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchPrescriptions();
    } catch (err) {
      console.error("Upload failed", err);
      alert("Failed to upload prescription.");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpeg', '.jpg'],
      'image/png': ['.png']
    },
    maxFiles: 1
  });

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    if (!window.confirm("Are you sure you want to delete this prescription?")) return;
    try {
      await api.delete(`/api/prescriptions/${id}`);
      setPrescriptions(prev => prev.filter(p => p.id !== id));
    } catch (err) {
      alert("Failed to delete prescription.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-slate-100 mb-3 bg-gradient-to-r from-teal-400 to-emerald-500 bg-clip-text text-transparent">Medication Intelligence Center</h1>
        <p className="text-slate-400 text-lg">Upload prescriptions. We'll automatically extract medicines, check for interactions, flag allergies, and build your schedule.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column - Upload and List */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Upload Area */}
          <div 
            {...getRootProps()} 
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-300 ${
              isDragActive 
                ? 'border-emerald-400 bg-emerald-900/20 scale-[1.02]' 
                : 'border-slate-700 bg-slate-900 hover:border-slate-500 hover:bg-slate-800'
            }`}
          >
            <input {...getInputProps()} />
            {uploading ? (
              <div className="flex flex-col items-center gap-4">
                <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-slate-200 font-medium text-lg">Extracting & Analyzing Prescription...</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-5xl drop-shadow-lg">💊</div>
                <p className="text-xl font-bold text-slate-200">
                  {isDragActive ? "Drop prescription here" : "Drag & drop a prescription"}
                </p>
                <p className="text-sm text-slate-400">Supports PDF, PNG, JPG. Handwritten or Printed.</p>
              </div>
            )}
          </div>

          {/* Prescriptions List */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden">
            <div className="p-6 border-b border-slate-800 bg-slate-800/50">
              <h2 className="text-xl font-bold text-slate-200">Prescription Library</h2>
            </div>
            {loading ? (
              <div className="p-12 text-center text-slate-500">Loading prescriptions...</div>
            ) : prescriptions.length === 0 ? (
              <div className="p-12 text-center text-slate-500 italic">No prescriptions found. Upload one to get started.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="text-xs text-slate-400 uppercase bg-slate-800/30">
                    <tr>
                      <th className="px-6 py-4">Doctor / Clinic</th>
                      <th className="px-6 py-4">Status</th>
                      <th className="px-6 py-4">Date</th>
                      <th className="px-6 py-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {prescriptions.map(p => (
                      <tr key={p.id} className="hover:bg-slate-800/50 transition-colors cursor-pointer group" onClick={() => navigate(`/medications/prescription/${p.id}`)}>
                        <td className="px-6 py-4">
                          <div className="font-bold text-slate-200 group-hover:text-emerald-400 transition-colors">{p.doctor_name || "Unknown Doctor"}</div>
                          <div className="text-xs text-slate-500">{p.hospital_name || "Unknown Clinic"}</div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded text-xs font-semibold uppercase tracking-wider ${
                            p.status === 'completed' ? 'bg-emerald-900/40 text-emerald-400' :
                            p.status === 'failed' ? 'bg-red-900/40 text-red-400' :
                            'bg-blue-900/40 text-blue-400 animate-pulse'
                          }`}>
                            {p.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-slate-400">
                          {new Date(p.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button 
                            onClick={(e) => handleDelete(p.id, e)}
                            className="text-red-400 hover:text-red-300 p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Nav to Timeline / Ad-hoc checker */}
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl hover:border-emerald-500/50 transition-colors cursor-pointer" onClick={() => navigate('/medications/timeline')}>
            <div className="text-3xl mb-4">📅</div>
            <h3 className="text-lg font-bold text-slate-200 mb-2">Medication Timeline</h3>
            <p className="text-sm text-slate-400 mb-4">View your active medications, schedule, and full medication history.</p>
            <div className="text-emerald-400 text-sm font-semibold flex items-center gap-1">
              View Timeline <span className="text-lg">→</span>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
            <div className="text-3xl mb-4">⚠️</div>
            <h3 className="text-lg font-bold text-slate-200 mb-2">Quick Interaction Check</h3>
            <p className="text-sm text-slate-400 mb-4">Check a new medicine against your profile before taking it.</p>
            <input type="text" placeholder="e.g. Ibuprofen" className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-emerald-500 mb-3" />
            <button className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2 px-4 rounded-lg transition-colors">
              Check Safety
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
