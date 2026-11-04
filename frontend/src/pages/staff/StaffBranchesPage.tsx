import { useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { branchesApi, countriesApi } from '../../api/endpoints'
import type { Branch, BranchPayload } from '../../api/types'
import { Alert } from '../../components/Alert'
import { Button, Field, Select, TextInput } from '../../components/Controls'
import { EmptyState, FullPageSpinner } from '../../components/Feedback'
import { Pagination } from '../../components/Pagination'
import { StaffPageHeader } from '../../components/StaffPageHeader'
import { StatusBadge } from '../../components/StatusBadge'
import { errorMessage } from '../../lib/errors'

export function StaffBranchesPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Branch | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['branches', { page }],
    queryFn: () => branchesApi.list({ page, size: 10 }),
  })

  const remove = useMutation({
    mutationFn: (id: number) => branchesApi.remove(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['branches'] }),
    onError: (caught) => setActionError(errorMessage(caught)),
  })

  const closeForm = () => {
    setShowForm(false)
    setEditing(null)
  }

  return (
    <div className="space-y-5">
      <StaffPageHeader
        title="Sucursales"
        description="Ubicaciones físicas que albergan ejemplares."
        action={
          <Button
            onClick={() => {
              setEditing(null)
              setShowForm(true)
            }}
          >
            Nueva sucursal
          </Button>
        }
      />

      {showForm || editing ? (
        <BranchForm
          key={editing?.id ?? 'new'}
          initial={editing ?? undefined}
          onDone={() => {
            queryClient.invalidateQueries({ queryKey: ['branches'] })
            closeForm()
          }}
          onCancel={closeForm}
        />
      ) : null}

      {actionError ? <Alert kind="error">{actionError}</Alert> : null}
      {isLoading ? <FullPageSpinner /> : null}
      {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

      {data && data.items.length === 0 ? <EmptyState title="No hay sucursales" /> : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-100 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Nombre</th>
                  <th className="px-4 py-3">Dirección</th>
                  <th className="px-4 py-3">Ciudad</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map((branch) => (
                  <tr key={branch.id}>
                    <td className="px-4 py-3 font-medium text-slate-900">{branch.name}</td>
                    <td className="px-4 py-3 text-slate-600">{branch.address}</td>
                    <td className="px-4 py-3 text-slate-600">{branch.city}</td>
                    <td className="px-4 py-3">
                      <span
                        className={
                          branch.is_active
                            ? 'text-xs font-medium text-emerald-700'
                            : 'text-xs font-medium text-slate-500'
                        }
                      >
                        {branch.is_active ? 'Activa' : 'Inactiva'}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="secondary"
                          onClick={() => {
                            setEditing(branch)
                            setShowForm(true)
                          }}
                        >
                          Editar
                        </Button>
                        <Button
                          variant="danger"
                          disabled={remove.isPending}
                          onClick={() => {
                            if (window.confirm(`¿Eliminar ${branch.name}?`)) {
                              remove.mutate(branch.id)
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

function BranchForm({
  initial,
  onDone,
  onCancel,
}: {
  initial?: Branch
  onDone: () => void
  onCancel: () => void
}) {
  const { data: countriesPage } = useQuery({
    queryKey: ['countries', 'options'],
    queryFn: () => countriesApi.list({ size: 100 }),
  })

  const [name, setName] = useState(initial?.name ?? '')
  const [address, setAddress] = useState(initial?.address ?? '')
  const [city, setCity] = useState(initial?.city ?? '')
  const [countryId, setCountryId] = useState(initial?.country_id?.toString() ?? '')
  const [isActive, setIsActive] = useState(initial?.is_active ?? true)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (payload: BranchPayload) =>
      initial ? branchesApi.update(initial.id, payload) : branchesApi.create(payload),
    onSuccess: onDone,
    onError: (caught) => setError(errorMessage(caught)),
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    mutation.mutate({
      name: name.trim(),
      address: address.trim(),
      city: city.trim(),
      country_id: countryId ? Number(countryId) : null,
      is_active: isActive,
    })
  }

  return (
    <form
      className="space-y-4 rounded-xl border border-indigo-200 bg-indigo-50/40 p-5"
      onSubmit={handleSubmit}
    >
      <h3 className="text-base font-semibold text-slate-900">
        {initial ? `Editar ${initial.name}` : 'Nueva sucursal'}
      </h3>
      {error ? <Alert kind="error">{error}</Alert> : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Nombre" htmlFor="branch-name">
          <TextInput
            id="branch-name"
            required
            value={name}
            onChange={(event) => setName(event.target.value)}
          />
        </Field>
        <Field label="Ciudad" htmlFor="branch-city">
          <TextInput
            id="branch-city"
            required
            value={city}
            onChange={(event) => setCity(event.target.value)}
          />
        </Field>
        <Field label="Dirección" htmlFor="branch-address">
          <TextInput
            id="branch-address"
            required
            value={address}
            onChange={(event) => setAddress(event.target.value)}
          />
        </Field>
        <Field label="País" htmlFor="branch-country">
          <Select
            id="branch-country"
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
      </div>

      <label className="flex items-center gap-2 text-sm text-slate-700">
        <input
          type="checkbox"
          checked={isActive}
          onChange={(event) => setIsActive(event.target.checked)}
        />
        Sucursal activa
      </label>

      <div className="flex items-center justify-between">
        <StatusBadge status={isActive ? 'active' : 'cancelled'} />
        <div className="flex gap-2">
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancelar
          </Button>
          <Button type="submit" loading={mutation.isPending}>
            {initial ? 'Guardar cambios' : 'Crear sucursal'}
          </Button>
        </div>
      </div>
    </form>
  )
}
