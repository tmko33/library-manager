import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { booksApi, loansApi, reservationsApi } from '../api/endpoints'
import { useAuth } from '../auth/useAuth'
import { Alert } from '../components/Alert'
import { Button } from '../components/Controls'
import { FullPageSpinner } from '../components/Feedback'
import { AvailabilityBadge } from '../components/StatusBadge'
import { errorMessage } from '../lib/errors'

interface Feedback {
  kind: 'success' | 'error'
  text: string
}

export function BookDetailPage() {
  const { id } = useParams()
  const bookId = Number(id)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { member } = useAuth()
  const [feedback, setFeedback] = useState<Feedback | null>(null)

  const { data: book, isLoading, isError, error } = useQuery({
    queryKey: ['book', bookId],
    queryFn: () => booksApi.get(bookId),
    enabled: Number.isInteger(bookId) && bookId > 0,
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['books'] })
    queryClient.invalidateQueries({ queryKey: ['book', bookId] })
    queryClient.invalidateQueries({ queryKey: ['loans'] })
    queryClient.invalidateQueries({ queryKey: ['reservations'] })
  }

  const borrow = useMutation({
    mutationFn: () => loansApi.borrow(bookId),
    onSuccess: () => {
      invalidate()
      setFeedback({ kind: 'success', text: 'Préstamo creado. Revisa la fecha de devolución en "Mis préstamos".' })
    },
    onError: (caught) => setFeedback({ kind: 'error', text: errorMessage(caught) }),
  })

  const reserve = useMutation({
    mutationFn: () => reservationsApi.create(bookId),
    onSuccess: () => {
      invalidate()
      setFeedback({ kind: 'success', text: 'Reserva creada. Entrarás en la cola de espera del título.' })
    },
    onError: (caught) => setFeedback({ kind: 'error', text: errorMessage(caught) }),
  })

  if (isLoading) return <FullPageSpinner />

  if (isError || !book) {
    return (
      <div className="space-y-4">
        <Alert kind="error" title="No se pudo cargar el libro">
          {errorMessage(error)}
        </Alert>
        <Link to="/" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">
          ← Volver al catálogo
        </Link>
      </div>
    )
  }

  const authors = book.authors.map((author) => author.name).join(', ')

  return (
    <div className="space-y-6">
      <Link to="/" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">
        ← Volver al catálogo
      </Link>

      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <article className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-center gap-3">
            <AvailabilityBadge available={book.available_copies} total={book.total_copies} />
            <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
              {book.publication_year ?? 's. f.'} · {book.language.toUpperCase()}
            </span>
          </div>

          <h1 className="mt-4 text-3xl font-semibold leading-tight text-slate-900">{book.title}</h1>
          <p className="mt-2 text-base text-slate-600">{authors || 'Autor desconocido'}</p>

          {book.summary ? (
            <p className="mt-5 leading-relaxed text-slate-700">{book.summary}</p>
          ) : null}

          <dl className="mt-6 grid gap-4 border-t border-slate-100 pt-5 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-slate-500">ISBN</dt>
              <dd className="font-medium text-slate-800">{book.isbn}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Editorial</dt>
              <dd className="font-medium text-slate-800">{book.publisher?.name ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Páginas</dt>
              <dd className="font-medium text-slate-800">{book.pages ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Copias</dt>
              <dd className="font-medium text-slate-800">
                {book.available_copies} disponibles de {book.total_copies}
              </dd>
            </div>
          </dl>
        </article>

        <aside className="h-fit rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Circulación</h2>
          <p className="mt-1 text-sm text-slate-500">
            {book.available_copies > 0
              ? 'Hay copias disponibles: puedes pedir el préstamo ahora.'
              : 'No hay copias disponibles: puedes reservar y esperar tu turno.'}
          </p>

          <div className="mt-5 space-y-3">
            {feedback ? (
              <Alert kind={feedback.kind === 'success' ? 'success' : 'error'}>
                {feedback.text}
              </Alert>
            ) : null}

            {!member ? (
              <Button
                className="w-full"
                onClick={() => navigate('/login', { state: { from: `/books/${book.id}` } })}
              >
                Ingresar para pedir
              </Button>
            ) : book.available_copies > 0 ? (
              <Button
                className="w-full"
                loading={borrow.isPending}
                onClick={() => borrow.mutate()}
              >
                Pedir préstamo
              </Button>
            ) : (
              <Button
                className="w-full"
                loading={reserve.isPending}
                onClick={() => reserve.mutate()}
              >
                Reservar
              </Button>
            )}
          </div>

          <ul className="mt-6 space-y-2 text-xs text-slate-500">
            <li>· Préstamo inicial de 14 días.</li>
            <li>· Máximo 5 préstamos activos por socio.</li>
            <li>· Las reservas respetan el orden de llegada.</li>
          </ul>
        </aside>
      </div>
    </div>
  )
}
