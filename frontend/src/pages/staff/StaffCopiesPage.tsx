import { useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { booksApi, branchesApi, copiesApi } from '../../api/endpoints'
import type { CopyPayload, CopyStatus } from '../../api/types'
import { Alert } from '../../components/Alert'
import { Button, Field, Select, TextInput, inputClass } from '../../components/Controls'
import { EmptyState, FullPageSpinner } from '../../components/Feedback'
import { Pagination } from '../../components/Pagination'
import { StaffPageHeader } from '../../components/StaffPageHeader'
import { errorMessage } from '../../lib/errors'

const copyStatuses: Array<{ value: CopyStatus; label: string }> = [
  { value: 'available', label: 'Disponible' },
  { value: 'on_loan', label: 'Prestada' },
  { value: 'reserved', label: 'Reservada' },
  { value: 'maintenance', label: 'Mantenimiento' },
  { value: 'lost', label: 'Perdida' },
]

export function StaffCopiesPage() {
  const queryClient = useQueryClient()
  const [bookFilter, setBookFilter] = useState('')
  const [branchFilter, setBranchFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  const { data: booksPage } = useQuery({
    queryKey: ['books', 'options'],
    queryFn: () => booksApi.list({ size: 100 }),
  })
  const { data: branchesPage } = useQuery({
    queryKey: ['branches', 'options'],
    queryFn: () => branchesApi.list({ size: 100 }),
  })

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['copies', { bookFilter, branchFilter, statusFilter, page }],
    queryFn: () =>
      copiesApi.list({
        book_id: bookFilter ? Number(bookFilter) : undefined,
        branch_id: branchFilter ? Number(branchFilter) : undefined,
        status_filter: (statusFilter as CopyStatus) || undefined,
        page,
        size: 10,
      }),
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['copies'] })
    queryClient.invalidateQueries({ queryKey: ['books'] })
  }

  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: number; status: CopyStatus }) =>
      copiesApi.update(id, { status }),
    onSuccess: invalidate,
    onError: (caught) => setActionError(errorMessage(caught)),
  })

  const remove = useMutation({
    mutationFn: (id: number) => copiesApi.remove(id),
    onSuccess: invalidate,
    onError: (caught) => setActionError(errorMessage(caught)),
  })

  return (
    <div className="space-y-5">
      <StaffPageHeader
        title="Copias"
        description="Ejemplares físicos de cada título y su estado."
        action={<Button onClick={() => setShowForm(true)}>Nueva copia</Button>}
      />

      {showForm ? (
        <CopyForm
          books={booksPage?.items ?? []}
          branches={branchesPage?.items ?? []}
          onDone={() => {
            invalidate()
            setShowForm(false)
          }}
          onCancel={() => setShowForm(false)}
        />
      ) : null}

      {actionError ? <Alert kind="error">{actionError}</Alert> : null}

      <div className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="min-w-[180px] flex-1">
          <label htmlFor="copy-book" className="mb-1 block text-sm font-medium text-slate-700">
            Libro
          </label>
          <Select
            id="copy-book"
            value={bookFilter}
            onChange={(event) => {
              setBookFilter(event.target.value)
              setPage(1)
            }}
          >
            <option value="">Todos</option>
            {booksPage?.items.map((book) => (
              <option key={book.id} value={book.id}>
                {book.title}
              </option>
            ))}
          </Select>
        </div>
        <div className="min-w-[180px]">
          <label htmlFor="copy-branch" className="mb-1 block text-sm font-medium text-slate-700">
            Sucursal
          </label>
          <Select
            id="copy-branch"
            value={branchFilter}
            onChange={(event) => {
              setBranchFilter(event.target.value)
              setPage(1)
            }}
          >
            <option value="">Todas</option>
            {branchesPage?.items.map((branch) => (
              <option key={branch.id} value={branch.id}>
                {branch.name}
              </option>
            ))}
          </Select>
        </div>
        <div className="min-w-[160px]">
          <label htmlFor="copy-status" className="mb-1 block text-sm font-medium text-slate-700">
            Estado
          </label>
          <Select
            id="copy-status"
            value={statusFilter}
            onChange={(event) => {
              setStatusFilter(event.target.value)
              setPage(1)
            }}
          >
            <option value="">Todos</option>
            {copyStatuses.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </Select>
        </div>
      </div>

      {isLoading ? <FullPageSpinner /> : null}
      {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

      {data && data.items.length === 0 ? <EmptyState title="No hay copias" /> : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-100 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Código</th>
                  <th className="px-4 py-3">Libro</th>
                  <th className="px-4 py-3">Sucursal</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map((copy) => (
                  <tr key={copy.id}>
                    <td className="px-4 py-3 font-mono text-xs text-slate-700">
                      {copy.inventory_code}
                    </td>
                    <td className="px-4 py-3 text-slate-700">{copy.book?.title ?? copy.book_id}</td>
                    <td className="px-4 py-3 text-slate-600">
                      {copy.branch?.name ?? copy.branch_id}
                    </td>
                    <td className="px-4 py-3">
                      <Select
                        className="min-w-[140px]"
                        value={copy.status}
                        onChange={(event) =>
                          updateStatus.mutate({
                            id: copy.id,
                            status: event.target.value as CopyStatus,
                          })
                        }
                      >
                        {copyStatuses.map((status) => (
                          <option key={status.value} value={status.value}>
                            {status.label}
                          </option>
                        ))}
                      </Select>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end">
                        <Button
                          variant="danger"
                          disabled={remove.isPending}
                          onClick={() => {
                            if (window.confirm(`¿Eliminar la copia ${copy.inventory_code}?`)) {
                              remove.mutate(copy.id)
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

function CopyForm({
  books,
  branches,
  onDone,
  onCancel,
}: {
  books: Array<{ id: number; title: string }>
  branches: Array<{ id: number; name: string }>
  onDone: () => void
  onCancel: () => void
}) {
  const [bookId, setBookId] = useState('')
  const [branchId, setBranchId] = useState('')
  const [inventoryCode, setInventoryCode] = useState('')
  const [acquiredAt, setAcquiredAt] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)

  // Options load asynchronously; fall back to the first one until the user picks.
  const selectedBookId = bookId || (books[0] ? String(books[0].id) : '')
  const selectedBranchId = branchId || (branches[0] ? String(branches[0].id) : '')

  const mutation = useMutation({
    mutationFn: (payload: CopyPayload) => copiesApi.create(payload),
    onSuccess: onDone,
    onError: (caught) => setError(errorMessage(caught)),
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    mutation.mutate({
      book_id: Number(selectedBookId),
      branch_id: Number(selectedBranchId),
      inventory_code: inventoryCode.trim(),
      acquired_at: acquiredAt || null,
      notes: notes.trim() || null,
    })
  }

  return (
    <form
      className="space-y-4 rounded-xl border border-indigo-200 bg-indigo-50/40 p-5"
      onSubmit={handleSubmit}
    >
      <h3 className="text-base font-semibold text-slate-900">Nueva copia</h3>
      {error ? <Alert kind="error">{error}</Alert> : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Libro" htmlFor="copy-form-book">
          <Select
            id="copy-form-book"
            required
            value={selectedBookId}
            onChange={(event) => setBookId(event.target.value)}
          >
            {books.map((book) => (
              <option key={book.id} value={book.id}>
                {book.title}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Sucursal" htmlFor="copy-form-branch">
          <Select
            id="copy-form-branch"
            required
            value={selectedBranchId}
            onChange={(event) => setBranchId(event.target.value)}
          >
            {branches.map((branch) => (
              <option key={branch.id} value={branch.id}>
                {branch.name}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Código de inventario" htmlFor="copy-code">
          <TextInput
            id="copy-code"
            required
            placeholder="BC-0100"
            value={inventoryCode}
            onChange={(event) => setInventoryCode(event.target.value)}
          />
        </Field>
        <Field label="Fecha de adquisición" htmlFor="copy-date">
          <TextInput
            id="copy-date"
            type="date"
            value={acquiredAt}
            onChange={(event) => setAcquiredAt(event.target.value)}
          />
        </Field>
      </div>

      <Field label="Notas" htmlFor="copy-notes">
        <textarea
          id="copy-notes"
          rows={2}
          className={inputClass}
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
        />
      </Field>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" loading={mutation.isPending} disabled={!books.length || !branches.length}>
          Crear copia
        </Button>
      </div>
    </form>
  )
}
