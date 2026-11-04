import { useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { authorsApi, countriesApi } from '../../api/endpoints'
import type { Author, AuthorPayload } from '../../api/types'
import { Alert } from '../../components/Alert'
import { Button, Field, Select, TextInput, inputClass } from '../../components/Controls'
import { EmptyState, FullPageSpinner } from '../../components/Feedback'
import { Pagination } from '../../components/Pagination'
import { StaffPageHeader } from '../../components/StaffPageHeader'
import { errorMessage } from '../../lib/errors'

export function StaffAuthorsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Author | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['authors', { q: query, page }],
    queryFn: () => authorsApi.list({ q: query || undefined, page, size: 10 }),
  })

  const remove = useMutation({
    mutationFn: (id: number) => authorsApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['authors'] }),
    onError: (caught) => setActionError(errorMessage(caught)),
  })

  const closeForm = () => {
    setShowForm(false)
    setEditing(null)
  }

  return (
    <div className="space-y-5">
      <StaffPageHeader
        title="Autores"
        description="Personas que firman los títulos del catálogo."
        action={
          <Button
            onClick={() => {
              setEditing(null)
              setShowForm(true)
            }}
          >
            Nuevo autor
          </Button>
        }
      />

      {showForm || editing ? (
        <AuthorForm
          key={editing?.id ?? 'new'}
          initial={editing ?? undefined}
          onDone={() => {
            queryClient.invalidateQueries({ queryKey: ['authors'] })
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
          <label htmlFor="author-search" className="mb-1 block text-sm font-medium text-slate-700">
            Buscar
          </label>
          <TextInput
            id="author-search"
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

      {data && data.items.length === 0 ? <EmptyState title="No hay autores" /> : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-100 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Nombre</th>
                  <th className="px-4 py-3">País</th>
                  <th className="px-4 py-3">Nacimiento</th>
                  <th className="px-4 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map((author) => (
                  <tr key={author.id}>
                    <td className="px-4 py-3 font-medium text-slate-900">{author.name}</td>
                    <td className="px-4 py-3 text-slate-600">{author.country?.name ?? '—'}</td>
                    <td className="px-4 py-3 text-slate-600">{author.birth_year ?? '—'}</td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          onClick={() => {
                            setEditing(author)
                            setShowForm(true)
                          }}
                        >
                          Editar
                        </Button>
                        <Button
                          variant="danger"
                          disabled={remove.isPending}
                          onClick={() => {
                            if (window.confirm(`¿Eliminar a ${author.name}?`)) {
                              remove.mutate(author.id)
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

function AuthorForm({
  initial,
  onDone,
  onCancel,
}: {
  initial?: Author
  onDone: () => void
  onCancel: () => void
}) {
  const { data: countriesPage } = useQuery({
    queryKey: ['countries', 'options'],
    queryFn: () => countriesApi.list({ size: 100 }),
  })

  const [name, setName] = useState(initial?.name ?? '')
  const [birthYear, setBirthYear] = useState(initial?.birth_year?.toString() ?? '')
  const [bio, setBio] = useState(initial?.bio ?? '')
  const [countryId, setCountryId] = useState(initial?.country_id?.toString() ?? '')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (payload: AuthorPayload) =>
      initial ? authorsApi.update(initial.id, payload) : authorsApi.create(payload),
    onSuccess: onDone,
    onError: (caught) => setError(errorMessage(caught)),
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    mutation.mutate({
      name: name.trim(),
      birth_year: birthYear ? Number(birthYear) : null,
      bio: bio.trim() || null,
      country_id: countryId ? Number(countryId) : null,
    })
  }

  return (
    <form
      className="space-y-4 rounded-xl border border-indigo-200 bg-indigo-50/40 p-5"
      onSubmit={handleSubmit}
    >
      <h3 className="text-base font-semibold text-slate-900">
        {initial ? `Editar ${initial.name}` : 'Nuevo autor'}
      </h3>
      {error ? <Alert kind="error">{error}</Alert> : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Nombre" htmlFor="author-name">
          <TextInput
            id="author-name"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </Field>
        <Field label="Año de nacimiento" htmlFor="author-year">
          <TextInput
            id="author-year"
            type="number"
            value={birthYear}
            onChange={(event) => setBirthYear(event.target.value)}
          />
        </Field>
      </div>

      <Field label="País" htmlFor="author-country">
        <Select
          id="author-country"
          value={countryId}
          onChange={(event) => setCountryId(event.target.value)}
        >
          <option value="">Sin país</option>
          {countriesPage?.items.map((country) => (
            <option key={country.id} value={country.id}>
              {country.name}
            </option>
          ))}
        </Select>
      </Field>

      <Field label="Biografía" htmlFor="author-bio">
        <textarea
          id="author-bio"
          rows={3}
          className={inputClass}
          value={bio}
          onChange={(event) => setBio(event.target.value)}
        />
      </Field>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" loading={mutation.isPending}>
          {initial ? 'Guardar cambios' : 'Crear autor'}
        </Button>
      </div>
    </form>
  )
}
