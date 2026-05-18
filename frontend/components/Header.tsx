'use client'

interface HeaderProps {
  pipelineStatus: 'idle' | 'running' | 'completed' | 'failed'
  jobId: string | null
  onStartOver?: () => void
}

export default function Header({ pipelineStatus, jobId, onStartOver }: HeaderProps) {
  const statusConfig = {
    idle: { color: 'text-slate-400', bg: 'bg-slate-500/20', label: 'Ready', dot: 'bg-slate-400' },
    running: { color: 'text-amber-400', bg: 'bg-amber-500/20', label: 'Running', dot: 'bg-amber-400 pulse-dot' },
    completed: { color: 'text-emerald-400', bg: 'bg-emerald-500/20', label: 'Completed', dot: 'bg-emerald-400' },
    failed: { color: 'text-red-400', bg: 'bg-red-500/20', label: 'Failed', dot: 'bg-red-400' },
  }

  const status = statusConfig[pipelineStatus]

  return (
    <header className="h-[72px] flex items-center justify-between px-6 border-b border-white/5 bg-surface-900/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="flex items-center gap-4">
        {/* Logo */}
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-lg shadow-brand-600/20">
          <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight">
            <span className="gradient-text">AutoML Copilot</span>
          </h1>
          <p className="text-xs text-slate-500">Adaptive Multi-Agent Data Science Platform</p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {jobId && (
          <>
            {onStartOver && (
              <button 
                onClick={onStartOver}
                className="text-xs px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 text-slate-300 transition-colors flex items-center gap-2"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                Start Over
              </button>
            )}
            <span className="text-xs text-slate-500 font-mono hidden sm:inline">
              Job: {jobId.slice(0, 8)}
            </span>
          </>
        )}
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${status.bg}`}>
          <div className={`w-2 h-2 rounded-full ${status.dot}`} />
          <span className={`text-xs font-semibold ${status.color}`}>{status.label}</span>
        </div>
      </div>
    </header>
  )
}
