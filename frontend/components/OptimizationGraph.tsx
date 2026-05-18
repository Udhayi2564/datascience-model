'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface OptimizationGraphProps {
  data: Record<string, any>
}

export default function OptimizationGraph({ data }: OptimizationGraphProps) {
  if (!data || Object.keys(data).length === 0 || data.skipped) {
    return (
      <div className="h-full w-full flex items-center justify-center text-slate-500 font-mono text-sm text-center px-4">
        {data?.skipped ? '[ Optuna tuning skipped for this task ]' : '[ Waiting for optimization history... ]'}
      </div>
    )
  }

  // Find the model with the most trials to display
  let bestModelKey = ''
  let maxTrials = 0
  Object.entries(data).forEach(([key, res]: [string, any]) => {
    if (res.trials && res.trials.length > maxTrials) {
      maxTrials = res.trials.length
      bestModelKey = key
    }
  })

  if (!bestModelKey) return null

  const chartData = data[bestModelKey].trials.map((t: any) => ({
    trial: `T${t.number}`,
    score: Number(t.value),
    params: t.params,
  }))

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="glass-card p-3 shadow-xl border-brand-500/30">
          <p className="font-semibold text-white mb-1">Trial {data.trial}</p>
          <p className="text-xs text-brand-400 mb-2 font-mono">Score: {data.score.toFixed(4)}</p>
          <div className="space-y-1">
            {Object.entries(data.params).map(([k, v]: [string, any]) => (
              <div key={k} className="flex justify-between gap-4 text-xs">
                <span className="text-slate-400">{k}:</span>
                <span className="text-slate-200">{typeof v === 'number' ? v.toFixed(4).replace(/\.0000$/, '') : String(v)}</span>
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
        <span>Hyperparameter Tuning History</span>
        <span className="text-slate-500 font-normal">{bestModelKey}</span>
      </h3>
      <div className="flex-1 min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis
              dataKey="trial"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              dy={10}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'monospace' }}
              domain={['auto', 'auto']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#6366f1"
              strokeWidth={3}
              dot={{ r: 4, fill: '#16162a', stroke: '#6366f1', strokeWidth: 2 }}
              activeDot={{ r: 6, fill: '#818cf8', stroke: '#fff', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
