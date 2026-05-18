'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import UploadPanel from '@/components/UploadPanel'
import WorkflowTimeline from '@/components/WorkflowTimeline'
import BenchmarkChart from '@/components/BenchmarkChart'
import ShapChart from '@/components/ShapChart'
import OptimizationGraph from '@/components/OptimizationGraph'
import AICopilotChat from '@/components/AICopilotChat'
import MetricsCard from '@/components/MetricsCard'
import ExecutionLog from '@/components/ExecutionLog'
import Header from '@/components/Header'
import DetailedMetrics from '@/components/DetailedMetrics'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

// ---------- types ----------
interface AgentUpdate {
  type: string
  agent: string
  status: string
  message: string
  timestamp: string
  data?: any
}

// ---------- component ----------
export default function Dashboard() {
  const [jobId, setJobId] = useState<string | null>(null)
  const [updates, setUpdates] = useState<AgentUpdate[]>([])
  const [results, setResults] = useState<any>(null)
  const [pipelineStatus, setPipelineStatus] = useState<'idle' | 'running' | 'completed' | 'failed'>('idle')
  const [activeTab, setActiveTab] = useState<'benchmark' | 'shap' | 'optimization'>('benchmark')
  const wsRef = useRef<WebSocket | null>(null)
  const pollRef = useRef<NodeJS.Timeout | null>(null)

  // ---- WebSocket connection ----
  const connectWebSocket = useCallback((id: string) => {
    const ws = new WebSocket(`${WS_URL}/ws/${id}`)
    wsRef.current = ws

    ws.onmessage = (event) => {
      try {
        const update: AgentUpdate = JSON.parse(event.data)
        setUpdates(prev => [...prev, update])

        if (update.agent === 'System' && update.status === 'completed' && update.data?.status === 'completed') {
          setResults(update.data)
          setPipelineStatus('completed')
        }
        if (update.status === 'failed') {
          setPipelineStatus('failed')
        }
      } catch (err) { /* ignore parse errors */ }
    }

    ws.onclose = () => {
      // Start polling as fallback
      startPolling(id)
    }
  }, [])

  // ---- Polling fallback ----
  const startPolling = useCallback((id: string) => {
    if (pollRef.current) clearInterval(pollRef.current)
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/api/status/${id}`)
        const data = await res.json()

        if (data.updates && data.updates.length) {
          setUpdates(data.updates)
        }

        if (data.status === 'completed') {
          clearInterval(pollRef.current!)
          const resResult = await fetch(`${API_URL}/api/results/${id}`)
          if (resResult.ok) {
            const resultData = await resResult.json()
            setResults(resultData)
            setPipelineStatus('completed')
          }
        } else if (data.status === 'failed') {
          clearInterval(pollRef.current!)
          setPipelineStatus('failed')
        }
      } catch (err) { /* retry */ }
    }, 2000)
  }, [])

  // ---- Upload handler ----
  const handleUpload = useCallback(async (file: File) => {
    setUpdates([])
    setResults(null)
    setPipelineStatus('running')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      const newJobId = data.job_id
      setJobId(newJobId)
      connectWebSocket(newJobId)
      startPolling(newJobId)
    } catch (err) {
      setPipelineStatus('failed')
      setUpdates([{
        type: 'error', agent: 'System', status: 'failed',
        message: 'Failed to connect to backend. Ensure the server is running.',
        timestamp: new Date().toISOString(),
      }])
    }
  }, [connectWebSocket, startPolling])

  // ---- Start over handler ----
  const handleStartOver = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
    }
    if (pollRef.current) {
      clearInterval(pollRef.current)
    }
    setJobId(null)
    setUpdates([])
    setResults(null)
    setPipelineStatus('idle')
    setActiveTab('benchmark')
  }, [])

  // Cleanup
  useEffect(() => {
    return () => {
      wsRef.current?.close()
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [])

  // ---- Derived state ----
  const benchmarking = results?.benchmarking || {}
  const shapValues = results?.shap_values || {}
  const optimizationResults = results?.optimization_results || {}
  const detectedTask = results?.detected_task || updates.find(u => u.agent === 'TaskAgent' && u.status === 'completed')?.data?.task_type || null
  const bestModel = results?.best_model || null
  const aiReport = results?.ai_report || ''
  const datasetSummary = results?.dataset_summary || updates.find(u => u.agent === 'DataAgent' && u.status === 'completed')?.data || null

  return (
    <div className="min-h-screen bg-surface-900 bg-grid">
      <Header pipelineStatus={pipelineStatus} jobId={jobId} onStartOver={handleStartOver} />

      {/* Upload overlay when idle */}
      {pipelineStatus === 'idle' && (
        <div className="flex items-center justify-center min-h-[calc(100vh-72px)]">
          <UploadPanel onUpload={handleUpload} />
        </div>
      )}

      {/* Main 3-panel dashboard */}
      {pipelineStatus !== 'idle' && (
        <div className="grid grid-cols-12 gap-4 p-4 pt-2 h-[calc(100vh-72px)]">
          {/* LEFT PANEL — Workflow Timeline */}
          <div className="col-span-3 flex flex-col gap-4 overflow-y-auto pr-1">
            {/* Mini upload for re-runs */}
            <UploadPanel onUpload={handleUpload} mini />

            <WorkflowTimeline updates={updates} pipelineStatus={pipelineStatus} />

            {/* Dataset summary card */}
            {datasetSummary && (
              <div className="glass-card p-4">
                <h3 className="text-sm font-semibold text-brand-400 mb-3 tracking-wide uppercase">Dataset Summary</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-slate-400">Rows</span><span className="font-mono font-semibold">{datasetSummary.row_count?.toLocaleString()}</span></div>
                  <div className="flex justify-between"><span className="text-slate-400">Columns</span><span className="font-mono font-semibold">{datasetSummary.col_count}</span></div>
                  <div className="flex justify-between"><span className="text-slate-400">Missing</span><span className="font-mono font-semibold">{datasetSummary.missing_pct}%</span></div>
                  <div className="flex justify-between"><span className="text-slate-400">Target</span><span className="font-mono font-semibold text-accent-400">{datasetSummary.suggested_target}</span></div>
                  {detectedTask && <div className="flex justify-between"><span className="text-slate-400">Task</span><span className="font-mono font-semibold text-brand-400 capitalize">{detectedTask}</span></div>}
                  {bestModel && <div className="flex justify-between"><span className="text-slate-400">Best Model</span><span className="font-mono font-semibold text-accent-400">{bestModel}</span></div>}
                </div>
              </div>
            )}
          </div>

          {/* CENTER PANEL — Charts & Metrics */}
          <div className="col-span-5 flex flex-col gap-4 overflow-y-auto">
            {/* Metrics row */}
            {results && (
              <div className="grid grid-cols-3 gap-3">
                <MetricsCard title="Task Type" value={detectedTask || '—'} icon="🎯" accent="brand" />
                <MetricsCard title="Best Model" value={bestModel || '—'} icon="🏆" accent="accent" />
                <MetricsCard title="Models Tested" value={Object.keys(benchmarking).length.toString()} icon="⚡" accent="brand" />
              </div>
            )}

            {/* Tab switcher */}
            <div className="glass-card p-1 flex gap-1">
              {(['benchmark', 'shap', 'optimization'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`flex-1 py-2 px-4 rounded-xl text-sm font-medium transition-all duration-300 ${
                    activeTab === tab
                      ? 'bg-brand-600/30 text-brand-400 shadow-lg shadow-brand-600/10'
                      : 'text-slate-400 hover:text-slate-300 hover:bg-white/5'
                  }`}
                >
                  {tab === 'benchmark' ? '📊 Benchmarking' : tab === 'shap' ? '🔬 SHAP Analysis' : '⚙️ Optimization'}
                </button>
              ))}
            </div>

            {/* Active chart */}
            <div className="glass-card p-5 flex-1 min-h-[350px]">
              {activeTab === 'benchmark' && <BenchmarkChart data={benchmarking} taskType={detectedTask} />}
              {activeTab === 'shap' && <ShapChart data={shapValues} />}
              {activeTab === 'optimization' && <OptimizationGraph data={optimizationResults} />}
            </div>

            {/* Deep Dive Metrics */}
            {activeTab === 'benchmark' && benchmarking && bestModel && (
              <DetailedMetrics benchmarking={benchmarking} bestModel={bestModel} taskType={detectedTask} />
            )}

            {/* Model download */}
            {pipelineStatus === 'completed' && jobId && (
              <a
                href={`${API_URL}/api/download/${jobId}`}
                className="glass-card p-4 flex items-center justify-center gap-3 text-accent-400 hover:text-accent-500 transition-colors group cursor-pointer"
              >
                <svg className="w-5 h-5 group-hover:translate-y-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                <span className="font-semibold">Download Best Model (.pkl)</span>
              </a>
            )}
          </div>

          {/* RIGHT PANEL — AI Copilot + Logs */}
          <div className="col-span-4 flex flex-col gap-4 overflow-y-auto pl-1">
            <AICopilotChat report={aiReport} evalNarrative={results?.eval_narrative} explainNarrative={results?.explain_narrative} />
            <ExecutionLog updates={updates} />
          </div>
        </div>
      )}
    </div>
  )
}
