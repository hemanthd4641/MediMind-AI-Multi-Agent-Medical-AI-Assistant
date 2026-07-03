import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function HealthTrends() {
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const res = await api.get('/api/timeline/trends');
        setTrends(res.data.trends);
      } catch (err) {
        console.error("Failed to load trends", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTrends();
  }, []);

  if (loading) {
    return <div className="p-12 text-center text-slate-400">Loading lab trends...</div>;
  }

  if (!trends || Object.keys(trends).length === 0) {
    return (
      <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12 mt-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-100 mb-2 bg-gradient-to-r from-emerald-400 to-teal-500 bg-clip-text text-transparent">Laboratory Trends</h1>
        </div>
        <div className="p-12 text-center text-slate-500 italic bg-slate-900 rounded-xl border border-slate-800">
          Not enough historical lab data to generate trends. Upload more medical reports.
        </div>
      </div>
    );
  }

  // Format data for Recharts
  const formatDataForChart = (series: any[]) => {
    return series.map(s => ({
      date: new Date(s.date).toLocaleDateString(),
      value: s.value,
      flag: s.flag
    }));
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12 mt-8">
      
      <div>
        <h1 className="text-3xl font-bold text-slate-100 mb-2 bg-gradient-to-r from-emerald-400 to-teal-500 bg-clip-text text-transparent">Laboratory Trends</h1>
        <p className="text-slate-400">Visualize how your key biomarkers are changing over time.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {Object.entries(trends).map(([param, data]: [string, any]) => {
          const chartData = formatDataForChart(data.series);
          const isStable = data.overall_direction === 'Stable';
          const isInc = data.overall_direction === 'Increasing';
          
          return (
            <div key={param} className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-xl font-bold text-slate-200">{param}</h2>
                  <div className="text-sm text-slate-400 mt-1">
                    Direction: 
                    <span className={`ml-2 font-semibold ${
                      isStable ? 'text-blue-400' : isInc ? 'text-orange-400' : 'text-emerald-400'
                    }`}>
                      {data.overall_direction} ({data.pct_change > 0 ? '+' : ''}{data.pct_change}%)
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={chartData}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis 
                      dataKey="date" 
                      stroke="#94a3b8" 
                      fontSize={12}
                      tickMargin={10}
                    />
                    <YAxis 
                      stroke="#94a3b8" 
                      fontSize={12}
                      domain={['auto', 'auto']}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }}
                      itemStyle={{ color: '#34d399' }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#34d399" 
                      strokeWidth={3}
                      dot={{ r: 5, fill: '#0f172a', stroke: '#34d399', strokeWidth: 2 }}
                      activeDot={{ r: 8 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
}
