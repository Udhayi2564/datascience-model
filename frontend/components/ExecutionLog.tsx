'use client'

import { useRef, useEffect } from 'react'

interface AgentUpdate {
  agent: string
  status: string
  message: string
  timestamp: string
}

interface ExecutionLogProps {
  updates: AgentUpdate[]
}

export default function ExecutionLog({ updates }: ExecutionLogProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [updates])

  return (
    <div className="glass-card flex-1 flex flex-col overflow-hidden">
      <div className="p-3 border-b border-white/5 bg-black/20 flex justify-between items-center">
        <h3 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
          System Execution Log
        </h3>
        <span className="text-[10px] text-slate-500 font-mono bg-white/5 px-2 py-0.5 rounded">Live</span>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-1.5 font-mono text-xs">
        {updates.length === 0 ? (
          <div className="text-slate-600 text-center mt-4">No logs yet...</div>
        ) : (
          updates.map((u, i) => (
            <div key={i} className="flex gap-3 hover:bg-white/5 px-2 py-1 rounded transition-colors">
              <span className="text-slate-600 flex-shrink-0">
                {new Date(u.timestamp).toISOString().split('T')[1].slice(0, 8)}
              </span>
              <span className={`flex-shrink-0 font-semibold w-[140px] truncate ${
                u.agent === 'System' ? 'text-slate-400' : 'text-brand-400'
              }`}>
                [{u.agent}]
              </span>
              <span className={`flex-1 ${
                u.status === 'failed' ? 'text-red-400' :
                u.status === 'completed' ? 'text-emerald-400' :
                'text-slate-300'
              }`}>
                {u.message}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
