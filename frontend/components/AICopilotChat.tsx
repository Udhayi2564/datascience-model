'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { motion, AnimatePresence } from 'framer-motion'

interface AICopilotChatProps {
  report: string
  evalNarrative?: any
  explainNarrative?: any
}

export default function AICopilotChat({ report, evalNarrative, explainNarrative }: AICopilotChatProps) {
  const [activeView, setActiveView] = useState<'report' | 'reasoning'>('report')

  return (
    <div className="glass-card flex-[2] flex flex-col overflow-hidden shadow-2xl shadow-brand-900/20 border-brand-500/20">
      {/* Header Tabs */}
      <div className="flex border-b border-white/5 bg-brand-900/20">
        <button
          onClick={() => setActiveView('report')}
          className={`flex-1 p-3 text-sm font-semibold transition-colors flex items-center justify-center gap-2 ${activeView === 'report' ? 'text-brand-400 border-b-2 border-brand-500 bg-brand-500/5' : 'text-slate-400 hover:bg-white/5 hover:text-slate-300'
            }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
          Executive AI Report
        </button>
        <button
          onClick={() => setActiveView('reasoning')}
          className={`flex-1 p-3 text-sm font-semibold transition-colors flex items-center justify-center gap-2 ${activeView === 'reasoning' ? 'text-accent-400 border-b-2 border-accent-500 bg-accent-500/5' : 'text-slate-400 hover:bg-white/5 hover:text-slate-300'
            }`}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          Agent Reasoning
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-5 custom-scrollbar">
        <AnimatePresence mode="wait">
          {activeView === 'report' ? (
            <motion.div
              key="report"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {report ? (
                <div className="markdown-body text-sm">
                  <ReactMarkdown>{report}</ReactMarkdown>
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 mt-20">
                  <div className="w-12 h-12 rounded-full border-4 border-brand-500/30 border-t-brand-500 animate-spin mb-4" />
                  <p>AI Copilot is analyzing data and generating report...</p>
                </div>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="reasoning"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              {/* Eval Narrative */}
              <div>
                <h4 className="text-accent-400 font-semibold mb-3 flex items-center gap-2">
                  <span>Evaluation Agent</span>
                  <span className="h-[1px] flex-1 bg-white/5"></span>
                </h4>
                {evalNarrative ? (
                  <div className="bg-black/20 p-4 rounded-xl border border-white/5 text-sm space-y-3">
                    {evalNarrative.winner && (
                      <p><strong className="text-slate-300">Winner:</strong> <span className="text-accent-400">{evalNarrative.winner}</span></p>
                    )}
                    {evalNarrative.winner_reason && (
                      <p><strong className="text-slate-300">Why:</strong> <span className="text-slate-400">{evalNarrative.winner_reason}</span></p>
                    )}
                    {evalNarrative.business_impact && (
                      <p><strong className="text-slate-300">Business Impact:</strong> <span className="text-slate-400">{evalNarrative.business_impact}</span></p>
                    )}
                    {evalNarrative.warnings && (
                      <p className="text-amber-400/80 mt-2 border-l-2 border-amber-500/50 pl-3 italic">
                        Warning: {evalNarrative.warnings}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="text-slate-500 text-sm italic">Waiting for evaluation reasoning...</p>
                )}
              </div>

              {/* Explainability Narrative */}
              <div>
                <h4 className="text-brand-400 font-semibold mb-3 flex items-center gap-2">
                  <span>Explainability Agent</span>
                  <span className="h-[1px] flex-1 bg-white/5"></span>
                </h4>
                {explainNarrative ? (
                  <div className="bg-black/20 p-4 rounded-xl border border-white/5 text-sm space-y-3">
                    {explainNarrative.top_driver && (
                      <p><strong className="text-slate-300">Top Driver:</strong> <span className="text-brand-400">{typeof explainNarrative.top_driver === 'object' ? JSON.stringify(explainNarrative.top_driver) : explainNarrative.top_driver}</span></p>
                    )}
                    {explainNarrative.model_behavior && (
                      <p><strong className="text-slate-300">Behavior:</strong> <span className="text-slate-400">{explainNarrative.model_behavior}</span></p>
                    )}
                    {explainNarrative.actionable_insights && (
                      <div>
                        <strong className="text-slate-300">Actionable Insights:</strong>
                        <ul className="list-disc pl-5 mt-2 space-y-1 text-slate-400">
                          {Array.isArray(explainNarrative.actionable_insights)
                            ? explainNarrative.actionable_insights.map((insight: string, i: number) => <li key={i}>{insight}</li>)
                            : <li>{explainNarrative.actionable_insights}</li>}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-slate-500 text-sm italic">Waiting for explainability reasoning...</p>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
