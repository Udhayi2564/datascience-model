'use client'

interface DetailedMetricsProps {
  benchmarking: Record<string, any>
  bestModel: string | null
  taskType: string | null
}

export default function DetailedMetrics({ benchmarking, bestModel, taskType }: DetailedMetricsProps) {
  if (!bestModel || !benchmarking || !benchmarking[bestModel]) return null

  const metrics = benchmarking[bestModel]

  // Filter out internal/array keys
  const ignoreKeys = ['error', 'primary_metric', 'confusion_matrix', 'forecast_values', 'forecast_steps']
  
  const displayMetrics = Object.entries(metrics)
    .filter(([k]) => !ignoreKeys.includes(k))
    .map(([k, v]) => ({
      name: k.replace(/_/g, ' ').toUpperCase(),
      value: typeof v === 'number' ? v.toFixed(4) : String(v)
    }))

  const cm = metrics.confusion_matrix

  return (
    <div className="glass-card p-5 flex flex-col gap-4 animate-fade-in">
      <h3 className="text-sm font-semibold text-brand-400 tracking-wide uppercase flex justify-between items-center">
        <span>{bestModel} — Deep Dive Metrics</span>
        <span className="px-2 py-1 bg-brand-500/20 rounded text-xs text-brand-300 capitalize">{taskType}</span>
      </h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {displayMetrics.map((m, i) => (
          <div key={i} className="flex flex-col bg-black/20 p-3 rounded-lg border border-white/5 hover:border-brand-500/30 transition-colors">
            <span className="text-[10px] text-slate-400 font-semibold mb-1 truncate" title={m.name}>{m.name}</span>
            <span className="text-lg font-mono font-semibold text-white">{m.value}</span>
          </div>
        ))}
      </div>
      
      {cm && Array.isArray(cm) && (
         <div className="mt-2 pt-4 border-t border-white/5">
            <span className="text-xs text-slate-400 font-semibold block mb-3 uppercase tracking-wider">Confusion Matrix (Heatmap)</span>
            <div className="flex flex-col gap-1 max-w-[200px]">
              {cm.map((row: number[], i: number) => (
                <div key={i} className="flex gap-1">
                  {row.map((cell: number, j: number) => {
                    // Simple heatmap opacity based on value relative to sum
                    const rowSum = row.reduce((a, b) => a + b, 0)
                    const intensity = rowSum > 0 ? Math.max(0.1, cell / rowSum) : 0.1
                    const isDiagonal = i === j // True Positives / True Negatives
                    return (
                      <div 
                        key={j} 
                        className={`flex-1 aspect-square flex items-center justify-center rounded font-mono text-sm ${isDiagonal ? 'bg-brand-500 text-white' : 'bg-rose-500 text-white'}`}
                        style={{ opacity: intensity * 0.8 + 0.2 }}
                        title={`True Class ${i}, Predicted Class ${j}`}
                      >
                        {cell}
                      </div>
                    )
                  })}
                </div>
              ))}
            </div>
            <div className="flex gap-4 mt-2 text-[10px] text-slate-500 uppercase">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-brand-500"></span> Correct</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-rose-500"></span> Error</span>
            </div>
         </div>
      )}
    </div>
  )
}
