import { useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { publishersApi } from '../../api/endpoints'
import type { Publisher, PublisherPayload } from '../../api/types'
import { Alert } from '../../components/Alert'
import { Button, Field, TextInput } from '../../components/Controls'
import { EmptyState, FullPageSpinner } from '../../components/Feedback'
import { Pagination } from '../../components/Pagination'
import { StaffPageHeader } from '../../components/StaffPageHeader'
import { errorMessage } from '../../lib/errors'

export function StaffPublishersPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Publisher | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['publishers', { q: query, page }],
    queryFn: () => publishersApi.list({ q: query || undefined, page, size: 10 }),
  })

  const remove = useMutation({
    mutationFn: (id: number) => publishersApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['publishers'] }),
    onError: (caught) => setActionError(errorMessage(caught)),
  })

  const closeForm = () => {
    setShowForm(false)
    setEditing(null)
  }

  return (
    <div className="space-y-5">
      <StaffPageHeader
        title="Editoriales"
        description="Empresas que publican los títulos."
        action={
          <Button
            onClick={() => {
              setEditing(null)
              setShowForm(true)
            }}
          >
            Nueva editorial
          </Button>
        }
      />

      {showForm || editing ? (
        <PublisherForm
          key={editing?.id ?? 'new'}
          initial={editing ?? undefined}
          onDone={() => {
            queryClient.invalidateQueries({ queryKey: ['publishers'] })
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
          <label
            htmlFor="publisher-search"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Buscar
          </label>
          <TextInput
            id="publisher-search"
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

      {data && data.items.length === 0 ? <EmptyState title="No hay editoriales" /> : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-100 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Nombre</th>
                  <th className="px-4 py-3">Web</th>
                  <th className="px-4 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map((publisher) => (
                  <tr key={publisher.id}>
                    <td className="px-4 py-3 font-medium text-slate-900">{publisher.name}</td>
                    <td className="px-4 py-3 text-slate-600">{publisher.website ?? '—'}</td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          onClick={() => {
                            setEditing(publisher)
                            setShowForm(true)
                          }}
                        >
                          Editar
                        </Button>
                        <Button
                          variant="danger"
                          disabled={remove.isPending}
                          onClick={() => {
                            if (window.confirm(`¿Eliminar ${publisher.name}?`)) {
                              remove.mutate(publisher.id)
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

function PublisherForm({
  initial,
  onDone,
  onCancel,
}: {
  initial?: Publisher
  onDone: () => void
  onCancel: () => void
}) {
  const [name, setName] = useState(initial?.name ?? '')
  const [website, setWebsite] = useState(initial?.website ?? '')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (payload: PublisherPayload) =>
      initial ? publishersApi.update(initial.id, payload) : publishersApi.create(payload),
    onSuccess: onDone,
    onError: (caught) => setError(errorMessage(caught)),
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    mutation.mutate({ name: name.trim(), website: website.trim() || null })
  }

  return (
    <form
      className="space-y-4 rounded-xl border border-indigo-200 bg-indigo-50/40 p-5"
      onSubmit={handleSubmit}
    >
      <h3 className="text-base font-semibold text-slate-900">
        {initial ? `Editar ${initial.name}` : 'Nueva editorial'}
      </h3>
      {error ? <Alert kind="error">{error}</Alert> : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Nombre" htmlFor="publisher-name">
          <TextInput
            id="publisher-name"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </Field>
        <Field label="Sitio web" htmlFor="publisher-website">
          <TextInput
            id="publisher-website"
            value={website}
            onChange={(event) => setWebsite(event.target.value)}
          />
        </Field>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" loading={mutation.isPending}>
          {initial ? 'Guardar cambios' : 'Crear editorial'}
        </Button>
      </div>
    </form>
  )
}
