const dateFormatter = new Intl.DateTimeFormat('es', { dateStyle: 'medium' })

export function formatDate(value?: string | null): string {
  if (!value) return '—'
  return dateFormatter.format(new Date(`${value}T00:00:00`))
}

export function daysUntil(value: string): number {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const target = new Date(`${value}T00:00:00`)
  return Math.round((target.getTime() - today.getTime()) / 86_400_000)
}

export function dueLabel(value: string): string {
  const days = daysUntil(value)
  if (days === 0) return 'vence hoy'
  if (days === 1) return 'vence mañana'
  if (days > 1) return `vence en ${days} días`
  if (days === -1) return 'venció ayer'
  return `venció hace ${Math.abs(days)} días`
}
