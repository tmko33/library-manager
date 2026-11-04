import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { loansApi } from '../../api/endpoints'
import type { LoanStatus } from '../../api/types'
import { Alert } from '../../components/Alert'
import { Button, Select } from '../../components/Controls'
import { EmptyState, FullPageSpinner } from '../../components/Feedback'
import { Pagination } from '../../components/Pagination'
import { StaffPageHeader } from '../../components/StaffPageHeader'
import { StatusBadge } from '../../components/StatusBadge'
import { errorMessage } from '../../lib/errors'
import { dueLabel, formatDate } from '../../lib/format'

export function StaffLoansPage() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)
  const [feedback, setFeedback] = useState<{ kind: 'success' | 'error'; text: string } | null>(
    null,
  )

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['loans', { staff: true, statusFilter, page }],
    queryFn: () =>
      loansApi.list({
        status_filter: (statusFilter as LoanStatus) || undefined,
        page,
        size: 10,
      }),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['loans'] })
    queryClient.invalidateQueries({ queryKey: ['books'] })
  }

  const renew = useMutation({
    mutationFn: (id: number) => loansApi.renew(id),
    onSuccess: (loan) => {
      invalidate()
      setFeedback({ kind: 'success', text: `Préstamo #${loan.id} renovado.` })
    },
    onError: (caught) => setFeedback({ kind: 'error', text: errorMessage(caught) }),
  })

  const returnLoan = useMutation({
    mutationFn: (id: number) => loansApi.return(id),
    onSuccess: (loan) => {
      invalidate()
      setFeedback({ kind: 'success', text: `Préstamo #${loan.id} devuelto.` })
    },
    onError: (caught) => setFeedback({ kind: 'error', text: errorMessage(caught) }),
  })

  const busy = renew.isPending || returnLoan.isPending

  return (
    <div className="space-y-5">
      <StaffPageHeader
        title="Préstamos"
        description="Todos los préstamos del sistema. Puedes renovar o registrar devoluciones."
      />

      {feedback ? (
        <Alert kind={feedback.kind === 'success' ? 'success' : 'error'}>{feedback.text}</Alert>
      ) : null}

      <div className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="min-w-[180px]">
          <label htmlFor="loan-status" className="mb-1 block text-sm font-medium text-slate-700">
            Estado
          </label>
          <Select
            id="loan-status"
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value)
              setPage(1)
            }}
          >
            <option value="">Todos</option>
            <option value="active">Activos</option>
            <option value="overdue">Vencidos</option>
            <option value="returned">Devueltos</option>
          </Select>
        </div>
      </div>

      {isLoading ? <FullPageSpinner /> : null}
      {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

      {data && data.items.length === 0 ? <EmptyState title="No hay préstamos" /> : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-100 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Libro</th>
                  <th className="px-4 py-3">Socio</th>
                  <th className="px-4 py-3">Fechas</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map((loan) => {
                  const active = loan.status !== 'returned'
                  return (
                    <tr key={loan.id}>
                      <td className="px-4 py-3 font-medium text-slate-900">
                        {loan.book?.title ?? `Préstamo #${loan.id}`}
                      </td>
                      <td className="px-4 py-3 text-slate-600">
                        {loan.member?.full_name ?? `Socio #${loan.member_id}`}
                        {loan.member ? (
                          <span className="block text-xs text-slate-400">{loan.member.email}</span>
                        ) : null}
                      </td>
                      <td className="px-4 py-3 text-slate-600">
                        {formatDate(loan.loan_date)} → {formatDate(loan.due_date)}
                        <span className="block text-xs text-slate-400">
                          {dueLabel(loan.due_date)} · {loan.renewals} renovaciones
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={loan.status} />
                      </td>
                      <td className="px-4 py-3">
                        {active ? (
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="secondary"
                              disabled={busy || loan.status === 'overdue'}
                              onClick={() => renew.mutate(loan.id)}
                            >
                              Renovar
                            </Button>
                            <Button
                              variant="danger"
                              disabled={busy}
                              onClick={() => returnLoan.mutate(loan.id)}
                            >
                              Devolver
                            </Button>
                          </div>
                        ) : null}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          <Pagination page={data.page} pages={data.pages} onChange={setPage} />
        </>
      ) : null}
    </div>
  )
}
