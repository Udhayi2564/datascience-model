interface MetricsCardProps {
  title: string
  value: string
  icon: string
  accent?: 'brand' | 'accent' | 'warning' | 'danger'
}

export default function MetricsCard({ title, value, icon, accent = 'brand' }: MetricsCardProps) {
  const accentClasses = {
    brand: 'text-brand-400 bg-brand-500/10 border-brand-500/20',
    accent: 'text-accent-400 bg-accent-500/10 border-accent-500/20',
    warning: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    danger: 'text-red-400 bg-red-500/10 border-red-500/20',
  }

  const colorConfig = accentClasses[accent]

  return (
    <div className={`glass-card p-4 border flex items-center gap-4 ${colorConfig.split(' ')[2]}`}>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl ${colorConfig.split(' ')[1]}`}>
        {icon}
      </div>
      <div>
        <p className="text-xs text-slate-400 mb-1">{title}</p>
        <p className={`text-lg font-bold truncate capitalize ${colorConfig.split(' ')[0]}`}>
          {value}
        </p>
      </div>
    </div>
  )
}
