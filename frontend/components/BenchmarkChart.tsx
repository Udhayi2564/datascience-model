'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface BenchmarkChartProps {
  data: Record<string, any>
  taskType?: string | null
}

export default function BenchmarkChart({ data, taskType }: BenchmarkChartProps) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="h-full w-full flex items-center justify-center text-slate-500 font-mono text-sm">
        [ Waiting for benchmarking data... ]
      </div>
    )
  }

  // Format data for Recharts
  const chartData = Object.entries(data)
    .filter(([_, metrics]) => !metrics.error)
    .map(([name, metrics]) => {
      return {
        name: name.replace('Regressor', '').replace('Classifier', ''),
        primaryMetric: Number(metrics.primary_metric) || 0,
        original: metrics,
      }
    })
    .sort((a, b) => b.primaryMetric - a.primaryMetric) // Descending order

  const getMetricLabel = () => {
    switch (taskType) {
      case 'classification': return 'F1 Score (Weighted)'
      case 'regression': return 'R² Score'
      case 'clustering': return 'Silhouette Score'
      case 'forecasting': return 'Information Criteria (Negative AIC)'
      default: return 'Primary Metric'
    }
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const metrics = payload[0].payload.original
      return (
        <div className="glass-card p-3 shadow-xl shadow-black/50 border-brand-500/30">
          <p className="font-semibold text-white mb-2">{label}</p>
          <div className="space-y-1 text-xs">
            {Object.entries(metrics)
              .filter(([k]) => k !== 'primary_metric' && k !== 'forecast_values')
              .map(([k, v]) => (
                <div key={k} className="flex justify-between gap-4">
                  <span className="text-slate-400 capitalize">{k.replace('_', ' ')}:</span>
                  <span className="font-mono text-brand-400">{typeof v === 'number' ? v.toFixed(4) : String(v)}</span>
                </div>
              ))}
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-full flex flex-col">
      <h3 className="text-sm font-semibold text-brand-400 mb-4 tracking-wide flex justify-between">
        <span>Model Performance Comparison</span>
        <span className="text-slate-500 font-normal">{getMetricLabel()}</span>
      </h3>
      <div className="flex-1 min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              dy={10}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94a3b8', fontSize: 12, fontFamily: 'monospace' }}
              domain={['auto', 'auto']}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99,102,241,0.05)' }} />
            <Bar dataKey="primaryMetric" radius={[4, 4, 0, 0]} maxBarSize={60}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={index === 0 ? '#10b981' : '#6366f1'} // Winner is accent color
                  fillOpacity={index === 0 ? 0.9 : 0.6}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
