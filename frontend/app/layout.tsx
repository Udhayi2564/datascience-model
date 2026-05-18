import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AutoML Copilot — Adaptive Multi-Agent Data Science Platform',
  description: 'Enterprise-grade autonomous ML platform. Upload a dataset and receive complete AI-powered analysis automatically.',
  keywords: 'AutoML, Machine Learning, AI, Data Science, Copilot',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-surface-900 text-white">
        {children}
      </body>
    </html>
  )
}
