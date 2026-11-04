import { useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { authorsApi, booksApi, publishersApi } from '../../api/endpoints'
import type { Book, BookPayload } from '../../api/types'
import { Alert } from '../../components/Alert'
import { Button, Field, Select, TextInput, inputClass } from '../../components/Controls'
import { EmptyState, FullPageSpinner } from '../../components/Feedback'
import { Pagination } from '../../components/Pagination'
import { StaffPageHeader } from '../../components/StaffPageHeader'
import { errorMessage } from '../../lib/errors'

export function StaffBooksPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Book | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['books', { staff: true, query, page }],
    queryFn: () => booksApi.list({ q: query || undefined, page, size: 10 }),
  })

  const remove = useMutation({
    mutationFn: (id: number) => booksApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] })
      setActionError(null)
    },
    onError: (caught) => setActionError(errorMessage(caught)),
  })

  const closeForm = () => {
    setShowForm(false)
    setEditing(null)
  }

  return (
    <div className="space-y-5">
      <StaffPageHeader
        title="Libros"
        description="Alta, edición y baja de títulos del catálogo."
        action={
          <Button
            onClick={() => {
              setEditing(null)
              setShowForm(true)
            }}
          >
            Nuevo libro
          </Button>
        }
      />

      {showForm || editing ? (
        <BookForm
          key={editing?.id ?? 'new'}
          initial={editing ?? undefined}
          onDone={() => {
            queryClient.invalidateQueries({ queryKey: ['books'] })
            closeForm()
          }}
          onCancel={closeForm}
        />
      ) : null}

      {actionError ? <Alert kind="error">{actionError}</Alert> : null}

      <form
        className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
        onSubmit={(event) => {
          event.preventDefault()
          setPage(1)
          setQuery(search.trim())
        }}
      >
        <div className="min-w-[220px] flex-1">
          <label htmlFor="book-search" className="mb-1 block text-sm font-medium text-slate-700">
            Buscar
          </label>
          <TextInput
            id="book-search"
            placeholder="Título o ISBN"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <Button type="submit" variant="secondary">
          Buscar
        </Button>
      </form>

      {isLoading ? <FullPageSpinner /> : null}
      {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

      {data && data.items.length === 0 ? (
        <EmptyState title="No hay libros">Crea el primero con el botón “Nuevo libro”.</EmptyState>
      ) : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-100 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Título</th>
                  <th className="px-4 py-3">Autores</th>
                  <th className="px-4 py-3">ISBN</th>
                  <th className="px-4 py-3">Copias</th>
                  <th className="px-4 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map((book) => (
                  <tr key={book.id} className="align-top">
                    <td className="px-4 py-3">
                      <p className="font-medium text-slate-900">{book.title}</p>
                      <p className="text-xs text-slate-500">{book.publication_year ?? 's. f.'}</p>
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {book.authors.map((author) => author.name).join(', ') || '—'}
                    </td>
                    <td className="px-4 py-3 text-slate-600">{book.isbn}</td>
                    <td className="px-4 py-3 text-slate-600">
                      {book.available_copies}/{book.total_copies}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          onClick={() => {
                            setEditing(book)
                            setShowForm(true)
                          }}
                        >
                          Editar
                        </Button>
                        <Button
                          variant="danger"
                          disabled={remove.isPending}
                          onClick={() => {
                            if (window.confirm(`¿Eliminar "${book.title}"?`)) {
                              remove.mutate(book.id)
                            }
                          }}
                        >
                          Eliminar
                        </Button>
                      </div>
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

function BookForm({
  initial,
  onDone,
  onCancel,
}: {
  initial?: Book
  onDone: () => void
  onCancel: () => void
}) {
  const { data: authorsPage } = useQuery({
    queryKey: ['authors', 'options'],
    queryFn: () => authorsApi.list({ size: 100 }),
  })
  const { data: publishersPage } = useQuery({
    queryKey: ['publishers', 'options'],
    queryFn: () => publishersApi.list({ size: 100 }),
  })

  const [isbn, setIsbn] = useState(initial?.isbn ?? '')
  const [title, setTitle] = useState(initial?.title ?? '')
  const [year, setYear] = useState(initial?.publication_year?.toString() ?? '')
  const [language, setLanguage] = useState(initial?.language ?? 'es')
  const [pages, setPages] = useState(initial?.pages?.toString() ?? '')
  const [summary, setSummary] = useState(initial?.summary ?? '')
  const [publisherId, setPublisherId] = useState(initial?.publisher_id?.toString() ?? '')
  const [authorIds, setAuthorIds] = useState<number[]>(
    initial?.authors.map((author) => author.id) ?? [],
  )
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (payload: BookPayload) =>
      initial ? booksApi.update(initial.id, payload) : booksApi.create(payload),
    onSuccess: onDone,
    onError: (caught) => setError(errorMessage(caught)),
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    mutation.mutate({
      isbn: isbn.trim(),
      title: title.trim(),
      publication_year: year ? Number(year) : null,
      language: language.trim() || 'es',
      pages: pages ? Number(pages) : null,
      summary: summary.trim() || null,
      publisher_id: publisherId ? Number(publisherId) : null,
      author_ids: authorIds,
    })
  }

  return (
    <form
      className="space-y-4 rounded-xl border border-indigo-200 bg-indigo-50/40 p-5"
      onSubmit={handleSubmit}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900">
          {initial ? `Editar “${initial.title}”` : 'Nuevo libro'}
        </h3>
      </div>

      {error ? <Alert kind="error">{error}</Alert> : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="ISBN" htmlFor="isbn">
          <TextInput id="isbn" required value={isbn} onChange={(e) => setIsbn(e.target.value)} />
        </Field>
        <Field label="Título" htmlFor="title">
          <TextInput id="title" required value={title} onChange={(e) => setTitle(e.target.value)} />
        </Field>
        <Field label="Año de publicación" htmlFor="year">
          <TextInput id="year" type="number" value={year} onChange={(e) => setYear(e.target.value)} />
        </Field>
        <Field label="Idioma" htmlFor="language">
          <TextInput
            id="language"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          />
        </Field>
        <Field label="Páginas" htmlFor="pages">
          <TextInput id="pages" type="number" value={pages} onChange={(e) => setPages(e.target.value)} />
        </Field>
        <Field label="Editorial" htmlFor="publisher">
          <Select
            id="publisher"
            value={publisherId}
            onChange={(e) => setPublisherId(e.target.value)}
          >
            <option value="">Sin editorial</option>
            {publishersPage?.items.map((publisher) => (
              <option key={publisher.id} value={publisher.id}>
                {publisher.name}
              </option>
            ))}
          </Select>
        </Field>
      </div>

      <Field label="Resumen" htmlFor="summary">
        <textarea
          id="summary"
          rows={3}
          className={inputClass}
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
        />
      </Field>

      <div>
        <p className="mb-2 text-sm font-medium text-slate-700">Autores</p>
        {authorsPage && authorsPage.items.length === 0 ? (
          <p className="text-sm text-slate-500">
            No hay autores todavía. Créalos en la pestaña “Autores”.
          </p>
        ) : null}
        <div className="grid max-h-40 gap-2 overflow-y-auto rounded-lg border border-slate-200 bg-white p-3 sm:grid-cols-2">
          {authorsPage?.items.map((author) => (
            <label key={author.id} className="flex items-center gap-2 text-sm text-slate-700">
              <input
                type="checkbox"
                checked={authorIds.includes(author.id)}
                onChange={(event) =>
                  setAuthorIds((current) =>
                    event.target.checked
                      ? [...current, author.id]
                      : current.filter((id) => id !== author.id),
                  )
                }
              />
              {author.name}
            </label>
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" loading={mutation.isPending}>
          {initial ? 'Guardar cambios' : 'Crear libro'}
        </Button>
      </div>
    </form>
  )
}
