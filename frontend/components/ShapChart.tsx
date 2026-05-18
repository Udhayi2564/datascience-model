'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

interface ShapChartProps {
  data: Record<string, any>
}

export default function ShapChart({ data }: ShapChartProps) {
  if (!data || !data.feature_importance || Object.keys(data.feature_importance).length === 0) {
    if (data?.error) {
      return (
        <div className="h-full w-full flex items-center justify-center text-amber-500/70 font-mono text-sm text-center px-4">
          [ SHAP not applicable or failed for this model ]<br />
          {data.error}
        </div>
      )
    }
    return (
      <div className="h-full w-full flex items-center justify-center text-slate-500 font-mono text-sm">
        [ Waiting for SHAP feature importance... ]
      </div>
    )
  }

  // Format data for Recharts (Top 10 features)
  const chartData = Object.entries(data.feature_importance)
    .slice(0, 10)
    .map(([feature, importance]) => ({
      feature: feature.length > 20 ? feature.substring(0, 20) + '...' : feature,
      fullFeature: feature,
      importance: Number(importance) || 0,
    }))
    .reverse() // Reverse for vertical bar chart

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="glass-card p-3 shadow-xl border-brand-500/30">
          <p className="font-semibold text-white mb-1">{data.fullFeature}</p>
          <p className="text-xs text-slate-400">
            Impact: <span className="font-mono text-accent-400">{data.importance.toFixed(6)}</span>
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full h-full flex flex-col">
      <h3 className="text-sm font-semibold text-brand-400 mb-4 tracking-wide flex justify-between">
        <span>Global Feature Importance (SHAP)</span>
        <span className="text-slate-500 font-normal">mean(|SHAP value|)</span>
      </h3>
      <div className="flex-1 min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 20, left: 40, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
            <XAxis
              type="number"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
            />
            <YAxis
              type="category"
              dataKey="feature"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#f1f5f9', fontSize: 11 }}
              width={120}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99,102,241,0.05)' }} />
            <Bar dataKey="importance" radius={[0, 4, 4, 0]} barSize={20}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={`hsl(34, 100%, ${50 + (index * 4)}%)`} // Gradient from amber to lighter amber
                  fillOpacity={0.8}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-slate-500 text-center mt-2 font-mono">
        Model Used: {data.model_used}
      </p>
    </div>
  )
}
