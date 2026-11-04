import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { finesApi } from '../../api/endpoints'
import type { FineStatus } from '../../api/types'
import { useAuth } from '../../auth/useAuth'
import { Alert } from '../../components/Alert'
import { Button, Select } from '../../components/Controls'
import { EmptyState, FullPageSpinner } from '../../components/Feedback'
import { Pagination } from '../../components/Pagination'
import { StaffPageHeader } from '../../components/StaffPageHeader'
import { StatusBadge } from '../../components/StatusBadge'
import { errorMessage } from '../../lib/errors'
import { formatDate } from '../../lib/format'

export function StaffFinesPage() {
  const queryClient = useQueryClient()
  const { member } = useAuth()
  const isAdmin = member?.role === 'admin'
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)
  const [feedback, setFeedback] = useState<{ kind: 'success' | 'error'; text: string } | null>(
    null,
  )

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['fines', { statusFilter, page }],
    queryFn: () =>
      finesApi.list({
        status_filter: (statusFilter as FineStatus) || undefined,
        page,
        size: 10,
      }),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['fines'] })
    queryClient.invalidateQueries({ queryKey: ['loans'] })
  }

  const pay = useMutation({
    mutationFn: (id: number) => finesApi.pay(id),
    onSuccess: (fine) => {
      invalidate()
      setFeedback({ kind: 'success', text: `Multa #${fine.id} marcada como pagada.` })
    },
    onError: (caught) => setFeedback({ kind: 'error', text: errorMessage(caught) }),
  })

  const waive = useMutation({
    mutationFn: (id: number) => finesApi.waive(id),
    onSuccess: (fine) => {
      invalidate()
      setFeedback({ kind: 'success', text: `Multa #${fine.id} condonada.` })
    },
    onError: (caught) => setFeedback({ kind: 'error', text: errorMessage(caught) }),
  })

  const busy = pay.isPending || waive.isPending

  return (
    <div className="space-y-5">
      <StaffPageHeader
        title="Multas"
        description="Multas generadas por devoluciones tardías."
      />

      {feedback ? (
        <Alert kind={feedback.kind === 'success' ? 'success' : 'error'}>{feedback.text}</Alert>
      ) : null}

      <div className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="min-w-[180px]">
          <label htmlFor="fine-status" className="mb-1 block text-sm font-medium text-slate-700">
            Estado
          </label>
          <Select
            id="fine-status"
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value)
              setPage(1)
            }}
          >
            <option value="">Todas</option>
            <option value="pending">Pendientes</option>
            <option value="paid">Pagadas</option>
            <option value="waived">Condonadas</option>
          </Select>
        </div>
      </div>

      {isLoading ? <FullPageSpinner /> : null}
      {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

      {data && data.items.length === 0 ? <EmptyState title="No hay multas" /> : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-100 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Importe</th>
                  <th className="px-4 py-3">Motivo</th>
                  <th className="px-4 py-3">Fecha</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map((fine) => (
                  <tr key={fine.id}>
                    <td className="px-4 py-3 font-medium text-slate-900">
                      {Number(fine.amount).toFixed(2)} €
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {fine.reason}
                      <span className="block text-xs text-slate-400">Préstamo #{fine.loan_id}</span>
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {formatDate(fine.created_at.slice(0, 10))}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={fine.status} />
                    </td>
                    <td className="px-4 py-3">
                      {fine.status === 'pending' ? (
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="secondary"
                            disabled={busy}
                            onClick={() => pay.mutate(fine.id)}
                          >
                            Pagar
                          </Button>
                          {isAdmin ? (
                            <Button
                              variant="ghost"
                              disabled={busy}
                              onClick={() => waive.mutate(fine.id)}
                            >
                              Condonar
                            </Button>
                          ) : null}
                        </div>
                      ) : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination page={data.page} pages={data.pages} onChange={setPage} />
        </>
      ) : null}
    </div>
  )
}
