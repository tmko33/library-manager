import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { loansApi } from '../api/endpoints'
import type { Loan } from '../api/types'
import { Alert } from '../components/Alert'
import { Button } from '../components/Controls'
import { EmptyState, FullPageSpinner } from '../components/Feedback'
import { Pagination } from '../components/Pagination'
import { StatusBadge } from '../components/StatusBadge'
import { dueLabel, formatDate } from '../lib/format'
import { errorMessage } from '../lib/errors'

interface Feedback {
  kind: 'success' | 'error'
  text: string
}

export function MyLoansPage() {
  const [page, setPage] = useState(1)
  const [feedback, setFeedback] = useState<Feedback | null>(null)
  const queryClient = useQueryClient()

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['loans', { page }],
    queryFn: () => loansApi.list({ page, size: 10 }),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['loans'] })
    queryClient.invalidateQueries({ queryKey: ['books'] })
    queryClient.invalidateQueries({ queryKey: ['book'] })
    queryClient.invalidateQueries({ queryKey: ['fines'] })
  }

  const renew = useMutation({
    mutationFn: (loanId: number) => loansApi.renew(loanId),
    onSuccess: (loan) => {
      invalidate()
      setFeedback({
        kind: 'success',
        text: `Préstamo #${loan.id} renovado hasta el ${formatDate(loan.due_date)}.`,
      })
    },
    onError: (caught) => setFeedback({ kind: 'error', text: errorMessage(caught) }),
  })

  const returnLoan = useMutation({
    mutationFn: (loanId: number) => loansApi.return(loanId),
    onSuccess: (loan) => {
      invalidate()
      setFeedback({ kind: 'success', text: `Préstamo #${loan.id} devuelto.` })
    },
    onError: (caught) => setFeedback({ kind: 'error', text: errorMessage(caught) }),
  })

  const busy = renew.isPending || returnLoan.isPending

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Mis préstamos</h1>
        <p className="mt-1 text-sm text-slate-500">
          Renueva o devuelve tus libros. Los préstamos vencidos generan multas.
        </p>
      </header>

      {feedback ? (
        <Alert kind={feedback.kind === 'success' ? 'success' : 'error'}>{feedback.text}</Alert>
      ) : null}

      {isLoading ? <FullPageSpinner /> : null}
      {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

      {data && data.items.length === 0 ? (
        <EmptyState title="Todavía no tienes préstamos">
          Explora el <Link to="/" className="font-medium text-indigo-600">catálogo</Link> y pide tu
          primer libro.
        </EmptyState>
      ) : null}

      {data && data.items.length > 0 ? (
        <>
          <ul className="space-y-3">
            {data.items.map((loan) => (
              <LoanRow
                key={loan.id}
                loan={loan}
                busy={busy}
                onRenew={() => renew.mutate(loan.id)}
                onReturn={() => returnLoan.mutate(loan.id)}
              />
            ))}
          </ul>
          <Pagination page={data.page} pages={data.pages} onChange={setPage} />
        </>
      ) : null}
    </div>
  )
}

function LoanRow({
  loan,
  busy,
  onRenew,
  onReturn,
}: {
  loan: Loan
  busy: boolean
  onRenew: () => void
  onReturn: () => void
}) {
  const active = loan.status !== 'returned'

  return (
    <li className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-semibold text-slate-900">
              {loan.book ? (
                <Link to={`/books/${loan.book.id}`} className="hover:text-indigo-700">
                  {loan.book.title}
                </Link>
              ) : (
                `Préstamo #${loan.id}`
              )}
            </h2>
            <StatusBadge status={loan.status} />
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Prestado el {formatDate(loan.loan_date)} · devolución {formatDate(loan.due_date)} (
            {dueLabel(loan.due_date)})
          </p>
          <p className="mt-1 text-xs text-slate-400">
            Renovaciones: {loan.renewals}
            {loan.returned_at ? ` · devuelto el ${formatDate(loan.returned_at)}` : ''}
          </p>
        </div>

        {active ? (
          <div className="flex gap-2">
            <Button
              variant="secondary"
              disabled={busy || loan.status === 'overdue'}
              onClick={onRenew}
            >
              Renovar
            </Button>
            <Button variant="danger" disabled={busy} onClick={onReturn}>
              Devolver
            </Button>
          </div>
        ) : null}
      </div>
    </li>
  )
}
