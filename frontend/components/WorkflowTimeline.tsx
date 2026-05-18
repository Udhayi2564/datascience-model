'use client'

import { motion, AnimatePresence } from 'framer-motion'

interface AgentUpdate {
  agent: string
  status: string
  message: string
  timestamp: string
}

interface WorkflowTimelineProps {
  updates: AgentUpdate[]
  pipelineStatus: string
}

// Define the expected pipeline steps
const PIPELINE_STEPS = [
  { agent: 'System', label: 'Dataset Loading', icon: '📁' },
  { agent: 'DataAgent', label: 'Data Profiling', icon: '🔍' },
  { agent: 'TaskAgent', label: 'Task Detection', icon: '🎯' },
  { agent: 'WorkflowAgent', label: 'Workflow Planning', icon: '📋' },
  { agent: 'ModelStrategistAgent', label: 'Model Selection', icon: '🧠' },
  { agent: 'MLEngine', label: 'Training & Preprocessing', icon: '⚙️' },
  { agent: 'OptimizationAgent', label: 'Hyperparameter Tuning', icon: '🔧' },
  { agent: 'EvaluationAgent', label: 'Benchmarking', icon: '📊' },
  { agent: 'ExplainabilityAgent', label: 'SHAP Explainability', icon: '🔬' },
  { agent: 'ReportAgent', label: 'AI Report Generation', icon: '📝' },
]

export default function WorkflowTimeline({ updates, pipelineStatus }: WorkflowTimelineProps) {
  const getStepStatus = (agentName: string) => {
    const agentUpdates = updates.filter(u => u.agent === agentName)
    if (agentUpdates.some(u => u.status === 'completed')) return 'completed'
    if (agentUpdates.some(u => u.status === 'running')) return 'running'
    if (agentUpdates.some(u => u.status === 'failed')) return 'failed'
    return 'pending'
  }

  return (
    <div className="glass-card p-4">
      <h3 className="text-sm font-semibold text-brand-400 mb-4 tracking-wide uppercase flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
        Pipeline Progress
      </h3>

      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-[15px] top-0 bottom-0 w-[2px] bg-gradient-to-b from-brand-500/30 via-brand-500/15 to-transparent" />

        <AnimatePresence>
          {PIPELINE_STEPS.map((step, idx) => {
            const status = getStepStatus(step.agent)
            const latestMessage = updates.filter(u => u.agent === step.agent).pop()?.message || ''

            return (
              <motion.div
                key={step.agent}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05, duration: 0.3 }}
                className="relative flex items-start gap-3 mb-3 last:mb-0"
              >
                {/* Status dot */}
                <div className="relative z-10 flex-shrink-0">
                  {status === 'completed' ? (
                    <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                      <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                    </div>
                  ) : status === 'running' ? (
                    <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center border border-amber-500/30">
                      <div className="w-3 h-3 rounded-full border-2 border-amber-400 border-t-transparent animate-spin" />
                    </div>
                  ) : status === 'failed' ? (
                    <div className="w-8 h-8 rounded-full bg-red-500/20 flex items-center justify-center border border-red-500/30">
                      <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" /></svg>
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-slate-500/10 flex items-center justify-center border border-slate-500/20">
                      <div className="w-2 h-2 rounded-full bg-slate-600" />
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 pt-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm">{step.icon}</span>
                    <span className={`text-sm font-medium ${
                      status === 'completed' ? 'text-emerald-400' :
                      status === 'running' ? 'text-amber-400' :
                      status === 'failed' ? 'text-red-400' :
                      'text-slate-500'
                    }`}>
                      {step.label}
                    </span>
                  </div>
                  {latestMessage && status !== 'pending' && (
                    <p className="text-xs text-slate-500 mt-0.5 truncate">{latestMessage}</p>
                  )}
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </div>
  )
}
