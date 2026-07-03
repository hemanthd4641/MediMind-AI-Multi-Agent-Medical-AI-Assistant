import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { api } from '../services/api';

interface ReportList {
  id: string;
  title: string;
  report_type: string;
  status: string;
  upload_date: string;
  confidence: number | null;
}

export function MedicalReports() {
  const navigate = useNavigate();
  const [reports, setReports] = useState<ReportList[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [search, setSearch] = useState('');

  const fetchReports = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/reports');
      setReports(res.data);
    } catch (err) {
      console.error("Failed to load reports", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      const res = await api.post('/api/reports/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Refresh list to show the new 'pending' report
      fetchReports();
    } catch (err) {
      console.error("Upload failed", err);
      alert("Failed to upload report.");
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
    if (!window.confirm("Are you sure you want to delete this report?")) return;
    try {
      await api.delete(`/api/reports/${id}`);
      setReports(prev => prev.filter(r => r.id !== id));
    } catch (err) {
      alert("Failed to delete report.");
    }
  };

  const filteredReports = reports.filter(r => 
    r.title.toLowerCase().includes(search.toLowerCase()) || 
    r.report_type.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-100 mb-2">Medical Reports</h1>
        <p className="text-slate-400">Upload your lab reports and let AI explain them to you in plain English.</p>
      </div>

      {/* Upload Area */}
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors ${
          isDragActive 
            ? 'border-teal-400 bg-teal-400/10' 
            : 'border-slate-700 bg-slate-900 hover:border-slate-500 hover:bg-slate-800'
        }`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-slate-200">Uploading and initiating analysis...</p>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-4xl">📄</div>
            <p className="text-lg font-medium text-slate-200">
              {isDragActive ? "Drop the report here" : "Drag & drop a medical report"}
            </p>
            <p className="text-sm text-slate-500">Supports PDF, PNG, JPG. We'll automatically extract the data.</p>
          </div>
        )}
      </div>

      {/* Reports List Area */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden">
        <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-800/50">
          <h2 className="text-xl font-bold text-slate-200">Your Reports</h2>
          <input 
            type="text" 
            placeholder="Search by title or type..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-teal-500 w-64"
          />
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500">Loading reports...</div>
        ) : filteredReports.length === 0 ? (
          <div className="p-12 text-center text-slate-500 italic">No reports found. Upload one above.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs text-slate-400 uppercase bg-slate-800/30">
                <tr>
                  <th className="px-6 py-4">Title</th>
                  <th className="px-6 py-4">Report Type</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Confidence</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filteredReports.map(report => (
                  <tr key={report.id} className="hover:bg-slate-800/50 transition-colors cursor-pointer" onClick={() => navigate(`/reports/${report.id}`)}>
                    <td className="px-6 py-4 font-medium text-slate-200">{report.title}</td>
                    <td className="px-6 py-4">{report.report_type}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-semibold uppercase tracking-wider ${
                        report.status === 'completed' ? 'bg-teal-900/40 text-teal-400' :
                        report.status === 'failed' ? 'bg-red-900/40 text-red-400' :
                        'bg-blue-900/40 text-blue-400 animate-pulse'
                      }`}>
                        {report.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {report.confidence !== null ? `${(report.confidence * 100).toFixed(0)}%` : '-'}
                    </td>
                    <td className="px-6 py-4 text-slate-400">
                      {new Date(report.upload_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button 
                        onClick={(e) => handleDelete(report.id, e)}
                        className="text-red-400 hover:text-red-300 p-1"
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
  );
}
