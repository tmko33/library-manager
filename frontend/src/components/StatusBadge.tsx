import { cn } from '../lib/cn'

const labels: Record<string, { text: string; className: string }> = {
  active: { text: 'Activo', className: 'bg-sky-100 text-sky-800' },
  returned: { text: 'Devuelto', className: 'bg-slate-100 text-slate-700' },
  overdue: { text: 'Vencido', className: 'bg-rose-100 text-rose-800' },
  pending: { text: 'Pendiente', className: 'bg-amber-100 text-amber-800' },
  fulfilled: { text: 'Cumplida', className: 'bg-emerald-100 text-emerald-800' },
  cancelled: { text: 'Cancelada', className: 'bg-slate-100 text-slate-700' },
  expired: { text: 'Expirada', className: 'bg-slate-100 text-slate-500' },
  paid: { text: 'Pagada', className: 'bg-emerald-100 text-emerald-800' },
  waived: { text: 'Condonada', className: 'bg-indigo-100 text-indigo-800' },
  member: { text: 'Socio', className: 'bg-slate-100 text-slate-700' },
  librarian: { text: 'Bibliotecario', className: 'bg-indigo-100 text-indigo-800' },
  admin: { text: 'Admin', className: 'bg-purple-100 text-purple-800' },
}

export function StatusBadge({ status }: { status: string }) {
  const entry = labels[status] ?? { text: status, className: 'bg-slate-100 text-slate-700' }
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        entry.className,
      )}
    >
      {entry.text}
    </span>
  )
}

export function AvailabilityBadge({ available, total }: { available: number; total: number }) {
  const has = available > 0
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        has ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800',
      )}
    >
      {has ? `${available} de ${total} disponibles` : 'Sin copias disponibles'}
    </span>
  )
}
