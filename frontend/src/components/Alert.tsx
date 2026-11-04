import type { ReactNode } from 'react'

import { cn } from '../lib/cn'

type Kind = 'error' | 'success' | 'info'

const styles: Record<Kind, string> = {
  error: 'border-rose-200 bg-rose-50 text-rose-800',
  success: 'border-emerald-200 bg-emerald-50 text-emerald-800',
  info: 'border-sky-200 bg-sky-50 text-sky-800',
}

export function Alert({
  kind = 'error',
  title,
  children,
}: {
  kind?: Kind
  title?: string
  children: ReactNode
}) {
  return (
    <div role="status" className={cn('rounded-lg border px-4 py-3 text-sm', styles[kind])}>
      {title ? <p className="font-semibold">{title}</p> : null}
      <div className={title ? 'mt-1' : undefined}>{children}</div>
    </div>
  )
}
