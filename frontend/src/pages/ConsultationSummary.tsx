import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

interface Symptom {
  symptom: string;
  body_location?: string;
  severity?: string;
  duration?: string;
}

interface SummaryData {
  chief_complaint: string;
  symptoms: Symptom[];
  timeline: string;
  relevant_medical_history: string;
  current_medications: string;
  allergies: string;
  lifestyle_factors: string;
  risk_factors: string[];
  urgency_level: string;
  recommended_next_steps: string[];
  medical_disclaimer: string;
}

export function ConsultationSummary() {
  const { id } = useParams<{ id: string }>();
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSummary();
  }, [id]);

  const fetchSummary = async () => {
    try {
      const res = await api.get(`/api/consultation/${id}/summary`);
      setSummary(res.data);
    } catch (err) {
      setError('Failed to load consultation summary. It may still be generating or the consultation was not found.');
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = () => {
    if (!summary) return;

    const doc = new jsPDF();
    
    // Header
    doc.setFontSize(20);
    doc.setTextColor(15, 118, 110); // Teal 600
    doc.text('MediMind AI Clinical Summary', 14, 20);
    
    doc.setFontSize(10);
    doc.setTextColor(100, 116, 139); // Slate 500
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 28);
    
    doc.setFontSize(12);
    doc.setTextColor(15, 23, 42); // Slate 900
    
    // Urgency
    doc.setFont(undefined, 'bold');
    doc.text(`Urgency Assessment: ${summary.urgency_level}`, 14, 40);
    doc.setFont(undefined, 'normal');

    // Chief Complaint
    doc.setFont(undefined, 'bold');
    doc.text('Chief Complaint:', 14, 50);
    doc.setFont(undefined, 'normal');
    doc.text(summary.chief_complaint, 14, 56, { maxWidth: 180 });

    let currentY = 66;

    // Symptoms Table
    if (summary.symptoms.length > 0) {
      const tableData = summary.symptoms.map(s => [
        s.symptom || 'N/A',
        s.body_location || 'N/A',
        s.severity || 'N/A',
        s.duration || 'N/A'
      ]);

      autoTable(doc, {
        startY: currentY,
        head: [['Symptom', 'Location', 'Severity', 'Duration']],
        body: tableData,
        theme: 'grid',
        headStyles: { fillColor: [15, 118, 110] }
      });
      currentY = (doc as any).lastAutoTable.finalY + 10;
    }

    // Timeline & History
    const details = [
      { title: 'Timeline:', content: summary.timeline },
      { title: 'Medical History:', content: summary.relevant_medical_history },
      { title: 'Current Medications:', content: summary.current_medications },
      { title: 'Allergies:', content: summary.allergies },
      { title: 'Lifestyle Factors:', content: summary.lifestyle_factors },
      { title: 'Risk Factors:', content: summary.risk_factors.join(', ') || 'None reported' },
    ];

    details.forEach(detail => {
      if (currentY > 270) {
        doc.addPage();
        currentY = 20;
      }
      doc.setFont(undefined, 'bold');
      doc.text(detail.title, 14, currentY);
      doc.setFont(undefined, 'normal');
      const textLines = doc.splitTextToSize(detail.content, 180);
      doc.text(textLines, 14, currentY + 6);
      currentY += 6 + (textLines.length * 6);
    });

    // Next Steps
    if (summary.recommended_next_steps.length > 0) {
      if (currentY > 260) {
        doc.addPage();
        currentY = 20;
      }
      doc.setFont(undefined, 'bold');
      doc.text('Recommended Next Steps:', 14, currentY);
      doc.setFont(undefined, 'normal');
      currentY += 6;
      summary.recommended_next_steps.forEach(step => {
        const textLines = doc.splitTextToSize(`• ${step}`, 180);
        doc.text(textLines, 14, currentY);
        currentY += (textLines.length * 6);
      });
    }

    // Disclaimer
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    const disclaimer = doc.splitTextToSize(summary.medical_disclaimer, 180);
    doc.text(disclaimer, 14, 280); // Bottom of page

    doc.save(`clinical_summary_${id?.substring(0, 8)}.pdf`);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <div className="w-12 h-12 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-400">Compiling your clinical summary...</p>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-center max-w-2xl mx-auto mt-12">
        <p className="text-red-400 mb-4">{error}</p>
        <Link to="/consultation" className="text-teal-400 hover:underline">Start a new consultation</Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500 pb-12">
      
      {/* Header */}
      <div className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 mb-2">Clinical Consultation Summary</h1>
          <p className="text-slate-400 text-sm">Review this summary or share it with your healthcare provider.</p>
        </div>
        <button 
          onClick={downloadPDF}
          className="bg-gradient-to-r from-teal-500 to-blue-600 text-white rounded-xl px-6 py-3 font-medium hover:opacity-90 transition-all flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
          Download PDF
        </button>
      </div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Left Column (Urgency & Chief Complaint) */}
        <div className="md:col-span-1 space-y-6">
          <div className={`border rounded-xl p-6 shadow-lg ${
            summary.urgency_level === 'Emergency' ? 'bg-red-900/20 border-red-500/50' :
            summary.urgency_level === 'Urgent' ? 'bg-orange-900/20 border-orange-500/50' :
            summary.urgency_level === 'Soon' ? 'bg-yellow-900/20 border-yellow-500/50' :
            'bg-teal-900/20 border-teal-500/50'
          }`}>
            <h2 className="text-xs text-slate-400 uppercase tracking-wider mb-2">Urgency Level</h2>
            <div className="text-2xl font-bold text-slate-100">{summary.urgency_level}</div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-xs text-slate-400 uppercase tracking-wider mb-3">Chief Complaint</h2>
            <p className="text-slate-200">{summary.chief_complaint}</p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-xs text-slate-400 uppercase tracking-wider mb-3">Risk Factors</h2>
            {summary.risk_factors.length > 0 ? (
              <ul className="list-disc pl-4 text-slate-200 space-y-1">
                {summary.risk_factors.map((rf, i) => <li key={i}>{rf}</li>)}
              </ul>
            ) : (
              <p className="text-slate-500 italic text-sm">None reported</p>
            )}
          </div>
        </div>

        {/* Right Column (Details) */}
        <div className="md:col-span-2 space-y-6">
          
          {/* Symptoms */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <span className="text-teal-400">●</span> Reported Symptoms
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 border-b border-slate-700">
                  <tr>
                    <th className="px-4 py-3">Symptom</th>
                    <th className="px-4 py-3">Location</th>
                    <th className="px-4 py-3">Severity</th>
                    <th className="px-4 py-3">Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.symptoms.map((s, i) => (
                    <tr key={i} className="border-b border-slate-800 last:border-0 hover:bg-slate-800/30">
                      <td className="px-4 py-3 font-medium text-slate-200 capitalize">{s.symptom}</td>
                      <td className="px-4 py-3">{s.body_location || '-'}</td>
                      <td className="px-4 py-3">{s.severity || '-'}</td>
                      <td className="px-4 py-3">{s.duration || '-'}</td>
                    </tr>
                  ))}
                  {summary.symptoms.length === 0 && (
                    <tr><td colSpan={4} className="px-4 py-3 text-center text-slate-500 italic">No symptoms recorded</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Medical History Section */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg grid grid-cols-2 gap-6">
            <div className="col-span-2">
              <h2 className="text-xs text-slate-400 uppercase tracking-wider mb-2">Timeline</h2>
              <p className="text-slate-200 text-sm">{summary.timeline}</p>
            </div>
            <div className="col-span-2">
              <h2 className="text-xs text-slate-400 uppercase tracking-wider mb-2">Medical History</h2>
              <p className="text-slate-200 text-sm">{summary.relevant_medical_history}</p>
            </div>
            <div>
              <h2 className="text-xs text-slate-400 uppercase tracking-wider mb-2">Current Medications</h2>
              <p className="text-slate-200 text-sm">{summary.current_medications}</p>
            </div>
            <div>
              <h2 className="text-xs text-slate-400 uppercase tracking-wider mb-2">Allergies</h2>
              <p className="text-slate-200 text-sm">{summary.allergies}</p>
            </div>
            <div className="col-span-2">
              <h2 className="text-xs text-slate-400 uppercase tracking-wider mb-2">Lifestyle Factors</h2>
              <p className="text-slate-200 text-sm">{summary.lifestyle_factors}</p>
            </div>
          </div>

          {/* Next Steps */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
            <h2 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
              <span className="text-blue-400">●</span> Recommended Next Steps
            </h2>
            <ul className="list-disc pl-5 text-slate-200 space-y-2">
              {summary.recommended_next_steps.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ul>
          </div>
        </div>

      </div>

      {/* Disclaimer */}
      <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4 mt-6">
        <p className="text-xs text-slate-400 text-center uppercase tracking-wide">
          {summary.medical_disclaimer}
        </p>
      </div>

    </div>
  );
}
