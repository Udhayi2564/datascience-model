'use client'

import { useCallback, useState } from 'react'
import { motion } from 'framer-motion'

interface UploadPanelProps {
  onUpload: (file: File) => void
  mini?: boolean
}

export default function UploadPanel({ onUpload, mini = false }: UploadPanelProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) { setFileName(file.name); onUpload(file) }
  }, [onUpload])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) { setFileName(file.name); onUpload(file) }
  }, [onUpload])

  if (mini) {
    return (
      <label className="glass-card p-3 flex items-center gap-3 cursor-pointer hover:border-brand-500/40 transition-colors group">
        <div className="w-8 h-8 rounded-lg bg-brand-600/20 flex items-center justify-center group-hover:bg-brand-600/30 transition-colors">
          <svg className="w-4 h-4 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
        </div>
        <span className="text-sm text-slate-400 group-hover:text-slate-300">Upload new dataset</span>
        <input type="file" accept=".csv,.xlsx,.json,.parquet" className="hidden" onChange={handleFileInput} />
      </label>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="text-center mb-8">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-2xl shadow-brand-600/30"
        >
          <svg className="w-10 h-10 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </motion.div>
        <h2 className="text-3xl font-bold gradient-text mb-2">AutoML Copilot</h2>
        <p className="text-slate-400 text-lg">Upload a dataset. AI does the rest.</p>
        <p className="text-slate-500 text-sm mt-1">Supports CSV, Excel, JSON, and Parquet</p>
      </div>

      <label
        className={`
          glass-card p-12 flex flex-col items-center justify-center cursor-pointer
          transition-all duration-300 group relative overflow-hidden
          ${isDragging ? 'border-brand-400 glow-brand scale-[1.02]' : 'hover:border-brand-500/30'}
        `}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        {/* Animated background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-brand-600/5 to-accent-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        <motion.div
          animate={isDragging ? { scale: 1.1, y: -5 } : { scale: 1, y: 0 }}
          className="relative z-10 flex flex-col items-center"
        >
          <div className="w-16 h-16 rounded-2xl bg-brand-600/10 flex items-center justify-center mb-4 group-hover:bg-brand-600/20 transition-colors">
            <svg className="w-8 h-8 text-brand-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>

          <p className="text-lg font-semibold text-slate-300 mb-1">
            {isDragging ? 'Drop it here!' : 'Drag & drop your dataset'}
          </p>
          <p className="text-sm text-slate-500 mb-4">or click to browse</p>

          <div className="flex gap-2">
            {['.csv', '.xlsx', '.json', '.parquet'].map(ext => (
              <span key={ext} className="px-2 py-1 rounded-md bg-white/5 text-xs text-slate-400 font-mono">{ext}</span>
            ))}
          </div>
        </motion.div>

        <input
          type="file"
          accept=".csv,.xlsx,.json,.parquet"
          className="hidden"
          onChange={handleFileInput}
        />
      </label>

      {/* Feature highlights */}
      <div className="grid grid-cols-4 gap-3 mt-6">
        {[
          { icon: '🤖', label: '8 AI Agents' },
          { icon: '⚡', label: 'Async Pipeline' },
          { icon: '🔬', label: 'SHAP Analysis' },
          { icon: '📊', label: 'Auto Benchmarks' },
        ].map((feat) => (
          <motion.div
            key={feat.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="glass-card p-3 text-center"
          >
            <div className="text-xl mb-1">{feat.icon}</div>
            <p className="text-xs text-slate-400">{feat.label}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
