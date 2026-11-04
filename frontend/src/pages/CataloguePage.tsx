import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import { booksApi } from '../api/endpoints'
import { Alert } from '../components/Alert'
import { BookCard } from '../components/BookCard'
import { Button, Select, TextInput } from '../components/Controls'
import { EmptyState, FullPageSpinner } from '../components/Feedback'
import { Pagination } from '../components/Pagination'
import { errorMessage } from '../lib/errors'

type Availability = 'all' | 'yes' | 'no'

export function CataloguePage() {
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [availability, setAvailability] = useState<Availability>('all')
  const [page, setPage] = useState(1)

  const { data, isLoading, isError, error, isFetching } = useQuery({
    queryKey: ['books', { query, availability, page }],
    queryFn: () =>
      booksApi.list({
        page,
        size: 9,
        q: query || undefined,
        available: availability === 'all' ? undefined : availability === 'yes',
      }),
  })

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Catálogo</h1>
          <p className="mt-1 text-sm text-slate-500">
            Busca por título o ISBN y consulta la disponibilidad.
          </p>
        </div>
        {data ? (
          <p className="text-sm text-slate-500">
            {data.total} {data.total === 1 ? 'título' : 'títulos'}
            {isFetching ? ' · actualizando…' : ''}
          </p>
        ) : null}
      </header>

      <form
        className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
        onSubmit={(event) => {
          event.preventDefault()
          setPage(1)
          setQuery(search.trim())
        }}
      >
        <div className="min-w-[220px] flex-1">
          <label htmlFor="search" className="mb-1 block text-sm font-medium text-slate-700">
            Buscar
          </label>
          <TextInput
            id="search"
            placeholder="Cien años de soledad, 9780307474728…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <div>
          <label htmlFor="availability" className="mb-1 block text-sm font-medium text-slate-700">
            Disponibilidad
          </label>
          <Select
            id="availability"
            value={availability}
            onChange={(event) => {
              setAvailability(event.target.value as Availability)
              setPage(1)
            }}
          >
            <option value="all">Todos</option>
            <option value="yes">Con copias disponibles</option>
            <option value="no">Sin copias disponibles</option>
          </Select>
        </div>

        <Button type="submit">Buscar</Button>
      </form>

      {isLoading ? <FullPageSpinner /> : null}

      {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

      {data && data.items.length === 0 ? (
        <EmptyState title="No hay resultados">
          Prueba con otro término o quita los filtros.
        </EmptyState>
      ) : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
          <Pagination page={data.page} pages={data.pages} onChange={setPage} />
        </>
      ) : null}
    </div>
  )
}
