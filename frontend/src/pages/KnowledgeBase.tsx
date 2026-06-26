import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Button } from '../components/Button';

interface Document {
  id: string;
  title: string;
  category: string | null;
  source: string | null;
  file_name: string;
  created_at: string;
}

export function KnowledgeBase() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/rag/documents');
      setDocuments(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', 'General');

    try {
      setUploading(true);
      setError(null);
      await api.post('/api/rag/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      await fetchDocuments();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
      event.target.value = ''; // Reset input
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await api.delete(`/api/rag/document/${id}`);
      await fetchDocuments();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-400 to-blue-500">
            Medical Knowledge Base
          </h1>
          <p className="text-gray-400 mt-2">
            Upload medical literature, guidelines, and manuals. The AI will use this evidence to ground its responses.
          </p>
        </div>
        
        <div className="relative">
          <input
            type="file"
            accept=".pdf,.txt,.md"
            onChange={handleFileUpload}
            disabled={uploading}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <Button disabled={uploading}>
            {uploading ? 'Processing...' : 'Upload Document'}
          </Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-lg">
          {error}
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/50 text-slate-300 text-sm uppercase tracking-wider">
                <th className="p-4 font-medium">Document Name</th>
                <th className="p-4 font-medium">Category</th>
                <th className="p-4 font-medium">Uploaded</th>
                <th className="p-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {loading ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-slate-500">
                    Loading documents...
                  </td>
                </tr>
              ) : documents.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-8 text-center text-slate-500">
                    No documents uploaded yet.
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center space-x-3">
                        <svg className="w-5 h-5 text-teal-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span className="font-medium text-slate-200">{doc.file_name}</span>
                      </div>
                    </td>
                    <td className="p-4 text-slate-400">{doc.category || 'General'}</td>
                    <td className="p-4 text-slate-400">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="text-red-400 hover:text-red-300 transition-colors text-sm font-medium p-2"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
