import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceArea
} from 'recharts';

interface ReportItem {
  id: string;
  parameter_name: string;
  observed_value: string;
  unit: string;
  reference_min: number | null;
  reference_max: number | null;
  status: string;
}

export function ReportCharts({ items }: { items: ReportItem[] }) {
  // Only plot numeric items that have reference ranges
  const plotData = items
    .filter(i => i.reference_min !== null && i.reference_max !== null)
    .map(i => {
      const val = parseFloat(i.observed_value.replace(/[^0-9.]/g, ''));
      // Normalize values to percentage of range to show them on same chart (simplified for MVP)
      // For a real app, separate charts per unit or a custom normalized scale is better.
      // We will just do a simple bar chart of the raw values and rely on tooltips.
      return {
        name: i.parameter_name,
        value: isNaN(val) ? 0 : val,
        min: i.reference_min,
        max: i.reference_max,
        status: i.status
      };
    })
    .filter(i => i.value > 0);

  if (plotData.length === 0) return null;

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-800 border border-slate-700 p-3 rounded-lg shadow-xl text-sm">
          <p className="font-bold text-slate-200 mb-1">{label}</p>
          <p className="text-teal-400">Value: {data.value}</p>
          <p className="text-slate-400 text-xs mt-1">Normal Range: {data.min} - {data.max}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
      <h2 className="text-lg font-bold text-slate-200 mb-6 flex items-center gap-2">
        <span>📊</span> Parameter Overview
      </h2>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={plotData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis 
              dataKey="name" 
              stroke="#94a3b8" 
              fontSize={10} 
              tickMargin={10}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis stroke="#94a3b8" fontSize={10} />
            <Tooltip content={<CustomTooltip />} cursor={{fill: '#1e293b'}} />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {plotData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={
                    entry.status === 'LOW' ? '#3b82f6' : 
                    entry.status === 'HIGH' ? '#f97316' : 
                    entry.status === 'CRITICAL' ? '#ef4444' : 
                    '#14b8a6' // Normal (teal)
                  } 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="flex gap-4 justify-center mt-4 text-xs font-semibold uppercase tracking-wider">
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-sm bg-teal-500"></div><span className="text-slate-400">Normal</span></div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-sm bg-blue-500"></div><span className="text-slate-400">Low</span></div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-sm bg-orange-500"></div><span className="text-slate-400">High</span></div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded-sm bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"></div><span className="text-slate-400">Critical</span></div>
      </div>
    </div>
  );
}
