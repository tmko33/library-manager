import { useQuery } from '@tanstack/react-query'

import { finesApi } from '../api/endpoints'
import { useAuth } from '../auth/useAuth'
import { Alert } from '../components/Alert'
import { FullPageSpinner } from '../components/Feedback'
import { StatusBadge } from '../components/StatusBadge'
import { errorMessage } from '../lib/errors'
import { formatDate } from '../lib/format'

export function AccountPage() {
  const { member } = useAuth()
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['fines', { page: 1 }],
    queryFn: () => finesApi.list({ page: 1, size: 20 }),
  })

  if (!member) return null

  const pending = data?.items.filter((fine) => fine.status === 'pending') ?? []
  const pendingTotal = pending.reduce((total, fine) => total + Number(fine.amount), 0)

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Mi cuenta</h1>
        <p className="mt-1 text-sm text-slate-500">Datos del socio y estado de multas.</p>
      </header>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">{member.full_name}</h2>
            <p className="text-sm text-slate-500">{member.email}</p>
          </div>
          <StatusBadge status={member.role} />
        </div>

        <dl className="mt-6 grid gap-4 border-t border-slate-100 pt-5 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-slate-500">Teléfono</dt>
            <dd className="font-medium text-slate-800">{member.phone ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Dirección</dt>
            <dd className="font-medium text-slate-800">{member.address ?? '—'}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Miembro desde</dt>
            <dd className="font-medium text-slate-800">
              {formatDate(member.created_at.slice(0, 10))}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">Membresía hasta</dt>
            <dd className="font-medium text-slate-800">
              {member.membership_expires_at ? formatDate(member.membership_expires_at) : 'Sin límite'}
            </dd>
          </div>
        </dl>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-900">Multas</h2>
          <p className="text-sm text-slate-500">
            Pendiente: <span className="font-semibold text-slate-800">{pendingTotal.toFixed(2)} €</span>
          </p>
        </div>

        {isLoading ? <FullPageSpinner /> : null}
        {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

        {data && data.items.length === 0 ? (
          <p className="mt-4 text-sm text-slate-500">No tienes multas registradas.</p>
        ) : null}

        {data && data.items.length > 0 ? (
          <ul className="mt-4 divide-y divide-slate-100">
            {data.items.map((fine) => (
              <li key={fine.id} className="flex flex-wrap items-center justify-between gap-2 py-3">
                <div>
                  <p className="text-sm font-medium text-slate-800">
                    {Number(fine.amount).toFixed(2)} € · {fine.reason}
                  </p>
                  <p className="text-xs text-slate-500">
                    Préstamo #{fine.loan_id} · {formatDate(fine.created_at.slice(0, 10))}
                  </p>
                </div>
                <StatusBadge status={fine.status} />
              </li>
            ))}
          </ul>
        ) : null}
      </section>
    </div>
  )
}
