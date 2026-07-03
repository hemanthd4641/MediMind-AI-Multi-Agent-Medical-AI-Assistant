import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { ReportCharts } from '../components/ReportCharts';

interface ReportItem {
  id: string;
  parameter_name: string;
  observed_value: string;
  unit: string;
  reference_min: number | null;
  reference_max: number | null;
  status: string;
  explanation: string;
}

interface ReportDetail {
  id: string;
  title: string;
  report_type: string;
  status: string;
  upload_date: string;
  summary: string;
  confidence: number;
  discussion_points: string[];
  citations: any[];
  items: ReportItem[];
}

export function ReportDetails() {
  const { id } = useParams();
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await api.get(`/api/reports/${id}`);
        setReport(res.data);
      } catch (err) {
        console.error("Failed to fetch report", err);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [id]);

  if (loading) {
    return <div className="p-12 text-center text-slate-400">Loading report...</div>;
  }

  if (!report) {
    return <div className="p-12 text-center text-slate-400">Report not found.</div>;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <Link to="/reports" className="text-teal-400 hover:text-teal-300 text-sm flex items-center gap-2">
        ← Back to Reports
      </Link>

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">{report.title}</h1>
          <p className="text-slate-400">
            {report.report_type} • Uploaded {new Date(report.upload_date).toLocaleDateString()}
          </p>
        </div>
        <div>
          <span className={`px-3 py-1.5 rounded-lg text-sm font-semibold uppercase tracking-wider ${
            report.status === 'completed' ? 'bg-teal-900/40 text-teal-400 border border-teal-800' :
            report.status === 'failed' ? 'bg-red-900/40 text-red-400 border border-red-800' :
            'bg-blue-900/40 text-blue-400 animate-pulse border border-blue-800'
          }`}>
            {report.status}
          </span>
        </div>
      </div>

      {report.status === 'completed' && (
        <>
          {/* Summary Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4">
                  <div className="flex items-center gap-2 bg-slate-800/80 backdrop-blur rounded-full px-3 py-1 border border-slate-700">
                    <span className="text-xs text-slate-400">AI Confidence</span>
                    <span className="text-sm font-bold text-teal-400">{(report.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
                
                <h2 className="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
                  <span>🧠</span> Clinical Summary
                </h2>
                <div className="prose prose-invert prose-teal max-w-none text-slate-300">
                  <p>{report.summary}</p>
                </div>

                {report.discussion_points && report.discussion_points.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">Key Discussion Points</h3>
                    <ul className="space-y-2">
                      {report.discussion_points.map((pt, i) => (
                        <li key={i} className="flex items-start gap-3 bg-slate-800/40 p-3 rounded-lg border border-slate-700/50">
                          <span className="text-teal-500 mt-0.5">•</span>
                          <span className="text-sm text-slate-300">{pt}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Data Table */}
              <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden">
                <div className="p-4 border-b border-slate-800 bg-slate-800/50">
                  <h2 className="text-lg font-bold text-slate-200">Detailed Findings</h2>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm text-slate-300">
                    <thead className="text-xs text-slate-400 uppercase bg-slate-800/30">
                      <tr>
                        <th className="px-6 py-4">Parameter</th>
                        <th className="px-6 py-4">Value</th>
                        <th className="px-6 py-4">Reference Range</th>
                        <th className="px-6 py-4">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {report.items.map(item => (
                        <tr key={item.id} className="hover:bg-slate-800/30">
                          <td className="px-6 py-4">
                            <div className="font-medium text-slate-200">{item.parameter_name}</div>
                            {item.explanation && (
                              <div className="text-xs text-slate-500 mt-1 max-w-xs">{item.explanation}</div>
                            )}
                          </td>
                          <td className="px-6 py-4 font-mono text-slate-300">
                            {item.observed_value} <span className="text-slate-500 text-xs">{item.unit}</span>
                          </td>
                          <td className="px-6 py-4 text-slate-400 text-xs font-mono">
                            {item.reference_min !== null && item.reference_max !== null 
                              ? `${item.reference_min} - ${item.reference_max}` 
                              : '-'}
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${
                              item.status === 'NORMAL' ? 'text-slate-400' :
                              item.status === 'LOW' ? 'bg-blue-900/40 text-blue-400' :
                              item.status === 'HIGH' ? 'bg-orange-900/40 text-orange-400' :
                              'bg-red-900/40 text-red-400 shadow-[0_0_10px_rgba(239,68,68,0.2)]'
                            }`}>
                              {item.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

            </div>

            {/* Sidebar (Charts & Citations) */}
            <div className="space-y-8">
              
              <ReportCharts items={report.items} />

              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                <h2 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                  <span>📚</span> Educational Citations
                </h2>
                {report.citations && report.citations.length > 0 ? (
                  <div className="space-y-4">
                    {report.citations.map((cite, i) => (
                      <div key={i} className="text-sm bg-slate-800/40 p-4 rounded-lg border border-slate-700/50">
                        <div className="font-semibold text-teal-400 mb-1">{cite.parameter}</div>
                        <p className="text-slate-300 italic mb-2 leading-relaxed">"{cite.text}"</p>
                        <div className="text-xs text-slate-500 text-right">
                          — {cite.source} (Page {cite.page})
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500 italic">No citations found in knowledge base.</p>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {report.status === 'processing' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center shadow-xl space-y-4">
          <div className="w-12 h-12 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <h2 className="text-xl font-bold text-slate-200">Analyzing Report</h2>
          <p className="text-slate-400">Our medical AI agents are currently extracting and interpreting the data...</p>
        </div>
      )}
      
      {report.status === 'failed' && (
        <div className="bg-red-950/30 border border-red-900/50 rounded-xl p-8 text-center">
          <p className="text-red-400">{report.summary || "Failed to process the report."}</p>
        </div>
      )}
    </div>
  );
}
