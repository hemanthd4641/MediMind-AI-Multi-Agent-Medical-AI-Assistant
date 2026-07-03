import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { InteractionDashboard } from '../components/InteractionDashboard';

interface Medicine {
  id: string;
  medicine_name: string;
  strength: string;
  unit: string;
  frequency: string;
  duration: string;
  route: string;
  instructions: string;
  educational_explanation: string;
}

interface PrescriptionDetail {
  id: string;
  doctor_name: string;
  hospital_name: string;
  status: string;
  created_at: string;
  medicines: Medicine[];
  analysis: any; // summary, interactions, allergy_warnings, contraindications, schedule
}

export function PrescriptionDetails() {
  const { id } = useParams();
  const [prescription, setPrescription] = useState<PrescriptionDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPrescription = async () => {
      try {
        const res = await api.get(`/api/prescriptions/${id}`);
        setPrescription(res.data);
      } catch (err) {
        console.error("Failed to fetch prescription", err);
      } finally {
        setLoading(false);
      }
    };
    fetchPrescription();
  }, [id]);

  if (loading) {
    return <div className="p-12 text-center text-slate-400">Loading prescription details...</div>;
  }

  if (!prescription) {
    return <div className="p-12 text-center text-slate-400">Prescription not found.</div>;
  }

  const { summary, interactions, allergy_warnings, contraindications, schedule } = prescription.analysis || {};

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <Link to="/medications" className="text-emerald-400 hover:text-emerald-300 text-sm flex items-center gap-2">
        ← Back to Medication Center
      </Link>

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-100">{prescription.hospital_name}</h1>
          <p className="text-slate-400">
            Dr. {prescription.doctor_name} • Uploaded {new Date(prescription.created_at).toLocaleDateString()}
          </p>
        </div>
        <div>
          <span className={`px-3 py-1.5 rounded-lg text-sm font-semibold uppercase tracking-wider ${
            prescription.status === 'completed' ? 'bg-emerald-900/40 text-emerald-400 border border-emerald-800' :
            prescription.status === 'failed' ? 'bg-red-900/40 text-red-400 border border-red-800' :
            'bg-blue-900/40 text-blue-400 animate-pulse border border-blue-800'
          }`}>
            {prescription.status}
          </span>
        </div>
      </div>

      {prescription.status === 'processing' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center shadow-xl space-y-4">
          <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <h2 className="text-xl font-bold text-slate-200">Analyzing Prescription</h2>
          <p className="text-slate-400">Extracting medications and running safety checks against your profile...</p>
        </div>
      )}

      {prescription.status === 'completed' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* Summary Block */}
            {summary && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                <h2 className="text-xl font-bold text-slate-200 mb-4 flex items-center gap-2">
                  <span>🧠</span> Prescription Summary
                </h2>
                <p className="text-slate-300 leading-relaxed mb-6">{summary.prescription_summary}</p>
                
                {summary.questions_to_ask && summary.questions_to_ask.length > 0 && (
                  <div className="mt-4">
                    <h3 className="text-sm font-semibold text-emerald-400 uppercase tracking-wider mb-3">Questions to Ask Your Doctor</h3>
                    <ul className="space-y-2">
                      {summary.questions_to_ask.map((q: string, i: number) => (
                        <li key={i} className="flex items-start gap-3 bg-slate-800/40 p-3 rounded-lg border border-slate-700/50">
                          <span className="text-emerald-500 mt-0.5">?</span>
                          <span className="text-sm text-slate-300">{q}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Safety Alerts (Allergies & Contraindications) */}
            {(allergy_warnings?.length > 0 || contraindications?.length > 0) && (
              <div className="bg-red-950/20 border border-red-900/50 rounded-xl p-6 shadow-xl">
                <h2 className="text-xl font-bold text-red-400 mb-4 flex items-center gap-2">
                  <span>🚨</span> Critical Safety Warnings
                </h2>
                <div className="space-y-4">
                  {allergy_warnings?.map((a: any, i: number) => (
                    <div key={`a-${i}`} className="bg-red-900/20 p-4 rounded-lg border border-red-800/30">
                      <div className="font-bold text-red-300">Allergy Warning: {a.medicine}</div>
                      <div className="text-sm text-red-400/80 mb-2">Known Allergen: {a.allergen}</div>
                      <p className="text-sm text-slate-300">{a.warning}</p>
                    </div>
                  ))}
                  {contraindications?.map((c: any, i: number) => (
                    <div key={`c-${i}`} className="bg-red-900/20 p-4 rounded-lg border border-red-800/30">
                      <div className="font-bold text-red-300">Contraindication: {c.medicine}</div>
                      <div className="text-sm text-red-400/80 mb-2">Condition: {c.condition}</div>
                      <p className="text-sm text-slate-300">{c.warning}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Extracted Medicines Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-xl overflow-hidden">
              <div className="p-4 border-b border-slate-800 bg-slate-800/50">
                <h2 className="text-lg font-bold text-slate-200">Prescribed Medications</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="text-xs text-slate-400 uppercase bg-slate-800/30">
                    <tr>
                      <th className="px-6 py-4">Medicine</th>
                      <th className="px-6 py-4">Dosage</th>
                      <th className="px-6 py-4">Frequency</th>
                      <th className="px-6 py-4">Duration</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {prescription.medicines.map(med => (
                      <tr key={med.id} className="hover:bg-slate-800/30">
                        <td className="px-6 py-4">
                          <div className="font-bold text-slate-200">{med.medicine_name}</div>
                          {med.educational_explanation && (
                            <div className="text-xs text-slate-400 mt-2 max-w-xs leading-relaxed italic">
                              "{med.educational_explanation}"
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 font-mono text-slate-300">
                          {med.strength} {med.unit}
                        </td>
                        <td className="px-6 py-4">
                          <div>{med.frequency}</div>
                          <div className="text-xs text-slate-500 mt-1">{med.instructions}</div>
                        </td>
                        <td className="px-6 py-4">
                          {med.duration}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          {/* Sidebar */}
          <div className="space-y-8">
            <InteractionDashboard interactions={interactions || []} />
            
            {/* Daily Schedule Preview */}
            {schedule && Object.keys(schedule).length > 0 && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
                <h2 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                  <span>⏰</span> Daily Schedule
                </h2>
                <div className="space-y-4">
                  {['Morning', 'Afternoon', 'Evening', 'Night'].map((timeOfDay) => (
                    <div key={timeOfDay} className="bg-slate-800/40 rounded-lg p-4 border border-slate-700/50">
                      <h3 className="font-bold text-emerald-400 mb-2">{timeOfDay}</h3>
                      {schedule[timeOfDay] && schedule[timeOfDay].length > 0 ? (
                        <ul className="space-y-2">
                          {schedule[timeOfDay].map((med: string, i: number) => (
                            <li key={i} className="text-sm text-slate-300 flex items-start gap-2">
                              <span className="text-emerald-500 mt-0.5">💊</span> {med}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <div className="text-sm text-slate-500 italic">No medications</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Disclaimer */}
            <div className="bg-slate-800/30 rounded-xl p-4 border border-slate-700/50">
              <p className="text-xs text-slate-500 text-center">
                {summary?.medical_disclaimer || "This tool does not provide medical advice. Always consult a healthcare professional."}
              </p>
            </div>
            
          </div>
        </div>
      )}
    </div>
  );
}
