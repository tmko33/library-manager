import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'

import { reservationsApi } from '../api/endpoints'
import { Alert } from '../components/Alert'
import { Button } from '../components/Controls'
import { EmptyState, FullPageSpinner } from '../components/Feedback'
import { Pagination } from '../components/Pagination'
import { StatusBadge } from '../components/StatusBadge'
import { errorMessage } from '../lib/errors'
import { formatDate } from '../lib/format'

export function MyReservationsPage() {
  const [page, setPage] = useState(1)
  const [feedback, setFeedback] = useState<{ kind: 'success' | 'error'; text: string } | null>(
    null,
  )
  const queryClient = useQueryClient()

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['reservations', { page }],
    queryFn: () => reservationsApi.list({ page, size: 10 }),
  })

  const cancel = useMutation({
    mutationFn: (id: number) => reservationsApi.cancel(id),
    onSuccess: (reservation) => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] })
      queryClient.invalidateQueries({ queryKey: ['book'] })
      queryClient.invalidateQueries({ queryKey: ['books'] })
      setFeedback({ kind: 'success', text: `Reserva #${reservation.id} cancelada.` })
    },
    onError: (caught) => setFeedback({ kind: 'error', text: errorMessage(caught) }),
  })

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Mis reservas</h1>
        <p className="mt-1 text-sm text-slate-500">
          Cola de espera por título. El primer socio de la cola tiene prioridad.
        </p>
      </header>

      {feedback ? (
        <Alert kind={feedback.kind === 'success' ? 'success' : 'error'}>{feedback.text}</Alert>
      ) : null}

      {isLoading ? <FullPageSpinner /> : null}
      {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

      {data && data.items.length === 0 ? (
        <EmptyState title="No tienes reservas">
          Cuando un libro no tenga copias disponibles podrás reservarlo desde su ficha.
        </EmptyState>
      ) : null}

      {data && data.items.length > 0 ? (
        <>
          <ul className="space-y-3">
            {data.items.map((reservation) => (
              <li
                key={reservation.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
              >
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <h2 className="text-base font-semibold text-slate-900">
                      {reservation.book ? (
                        <Link
                          to={`/books/${reservation.book.id}`}
                          className="hover:text-indigo-700"
                        >
                          {reservation.book.title}
                        </Link>
                      ) : (
                        `Reserva #${reservation.id}`
                      )}
                    </h2>
                    <StatusBadge status={reservation.status} />
                  </div>
                  <p className="mt-1 text-sm text-slate-500">
                    Creada el {formatDate(reservation.created_at.slice(0, 10))}
                    {reservation.expires_at
                      ? ` · retención hasta ${formatDate(reservation.expires_at)}`
                      : ''}
                  </p>
                </div>

                {reservation.status === 'pending' ? (
                  <Button
                    variant="secondary"
                    loading={cancel.isPending}
                    onClick={() => cancel.mutate(reservation.id)}
                  >
                    Cancelar
                  </Button>
                ) : null}
              </li>
            ))}
          </ul>
          <Pagination page={data.page} pages={data.pages} onChange={setPage} />
        </>
      ) : null}
    </div>
  )
}
