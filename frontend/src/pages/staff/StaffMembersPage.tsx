import { useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { membersApi } from '../../api/endpoints'
import type { Member, MemberPayload, MemberRole, MemberUpdatePayload } from '../../api/types'
import { useAuth } from '../../auth/useAuth'
import { Alert } from '../../components/Alert'
import { Button, Field, Select, TextInput } from '../../components/Controls'
import { EmptyState, FullPageSpinner } from '../../components/Feedback'
import { Pagination } from '../../components/Pagination'
import { StaffPageHeader } from '../../components/StaffPageHeader'
import { StatusBadge } from '../../components/StatusBadge'
import { errorMessage } from '../../lib/errors'

export function StaffMembersPage() {
  const queryClient = useQueryClient()
  const { member: currentMember } = useAuth()
  const isAdmin = currentMember?.role === 'admin'
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [activeFilter, setActiveFilter] = useState('')
  const [page, setPage] = useState(1)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Member | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['members', { query, activeFilter, page }],
    queryFn: () =>
      membersApi.list({
        q: query || undefined,
        is_active: activeFilter === '' ? undefined : activeFilter === 'yes',
        page,
        size: 10,
      }),
  })

  const deactivate = useMutation({
    mutationFn: (id: number) => membersApi.deactivate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['members'] }),
    onError: (caught) => setActionError(errorMessage(caught)),
  })

  const closeForm = () => {
    setShowForm(false)
    setEditing(null)
  }

  return (
    <div className="space-y-5">
      <StaffPageHeader
        title="Socios"
        description="Cuentas de socios, bibliotecarios y administradores."
        action={
          <Button
            onClick={() => {
              setEditing(null)
              setShowForm(true)
            }}
          >
            Nuevo socio
          </Button>
        }
      />

      {showForm || editing ? (
        <MemberForm
          key={editing?.id ?? 'new'}
          initial={editing ?? undefined}
          isAdmin={isAdmin}
          onDone={() => {
            queryClient.invalidateQueries({ queryKey: ['members'] })
            closeForm()
          }}
          onCancel={closeForm}
        />
      ) : null}

      {actionError ? <Alert kind="error">{actionError}</Alert> : null}

      <div className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <form
          className="flex min-w-[220px] flex-1 items-end gap-2"
          onSubmit={(event) => {
            event.preventDefault()
            setPage(1)
            setQuery(search.trim())
          }}
        >
          <div className="flex-1">
            <label htmlFor="member-search" className="mb-1 block text-sm font-medium text-slate-700">
              Buscar
            </label>
            <TextInput
              id="member-search"
              placeholder="Nombre o correo"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
          <Button type="submit" variant="secondary">
            Buscar
          </Button>
        </form>

        <div className="min-w-[160px]">
          <label htmlFor="member-active" className="mb-1 block text-sm font-medium text-slate-700">
            Estado
          </label>
          <Select
            id="member-active"
            value={activeFilter}
            onChange={(event) => {
              setActiveFilter(event.target.value)
              setPage(1)
            }}
          >
            <option value="">Todos</option>
            <option value="yes">Activos</option>
            <option value="no">Inactivos</option>
          </Select>
        </div>
      </div>

      {isLoading ? <FullPageSpinner /> : null}
      {isError ? <Alert kind="error">{errorMessage(error)}</Alert> : null}

      {data && data.items.length === 0 ? <EmptyState title="No hay socios" /> : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
            <table className="min-w-full divide-y divide-slate-100 text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Nombre</th>
                  <th className="px-4 py-3">Correo</th>
                  <th className="px-4 py-3">Rol</th>
                  <th className="px-4 py-3">Estado</th>
                  <th className="px-4 py-3 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.items.map((member) => {
                  const manageable = isAdmin || member.role !== 'admin'
                  return (
                    <tr key={member.id}>
                      <td className="px-4 py-3 font-medium text-slate-900">{member.full_name}</td>
                      <td className="px-4 py-3 text-slate-600">{member.email}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={member.role} />
                      </td>
                      <td className="px-4 py-3 text-slate-600">
                        {member.is_active ? 'Activo' : 'Inactivo'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="secondary"
                            disabled={!manageable}
                            onClick={() => {
                              setEditing(member)
                              setShowForm(true)
                            }}
                          >
                            Editar
                          </Button>
                          <Button
                            variant="danger"
                            disabled={!manageable || !member.is_active || deactivate.isPending}
                            onClick={() => {
                              if (window.confirm(`¿Desactivar a ${member.full_name}?`)) {
                                deactivate.mutate(member.id)
                              }
                            }}
                          >
                            Desactivar
                          </Button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          <Pagination page={data.page} pages={data.pages} onChange={setPage} />
        </>
      ) : null}
    </div>
  )
}

function MemberForm({
  initial,
  isAdmin,
  onDone,
  onCancel,
}: {
  initial?: Member
  isAdmin: boolean
  onDone: () => void
  onCancel: () => void
}) {
  const roleOptions: MemberRole[] = isAdmin
    ? ['member', 'librarian', 'admin']
    : ['member', 'librarian']

  const [fullName, setFullName] = useState(initial?.full_name ?? '')
  const [email, setEmail] = useState(initial?.email ?? '')
  const [password, setPassword] = useState('')
  const [phone, setPhone] = useState(initial?.phone ?? '')
  const [address, setAddress] = useState(initial?.address ?? '')
  const [role, setRole] = useState<MemberRole>(initial?.role ?? 'member')
  const [isActive, setIsActive] = useState(initial?.is_active ?? true)
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: (payload: MemberPayload | MemberUpdatePayload) =>
      initial ? membersApi.update(initial.id, payload) : membersApi.create(payload as MemberPayload),
    onSuccess: onDone,
    onError: (caught) => setError(errorMessage(caught)),
  })

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (initial) {
      mutation.mutate({
        full_name: fullName.trim(),
        email: email.trim(),
        phone: phone.trim() || null,
        address: address.trim() || null,
        role,
        is_active: isActive,
      })
    } else {
      mutation.mutate({
        full_name: fullName.trim(),
        email: email.trim(),
        password,
        phone: phone.trim() || null,
        address: address.trim() || null,
        role,
      })
    }
  }

  return (
    <form
      className="space-y-4 rounded-xl border border-indigo-200 bg-indigo-50/40 p-5"
      onSubmit={handleSubmit}
    >
      <h3 className="text-base font-semibold text-slate-900">
        {initial ? `Editar ${initial.full_name}` : 'Nuevo socio'}
      </h3>
      {error ? <Alert kind="error">{error}</Alert> : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <Field label="Nombre completo" htmlFor="member-name">
          <TextInput
            id="member-name"
            required
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
          />
        </Field>
        <Field label="Correo" htmlFor="member-email">
          <TextInput
            id="member-email"
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </Field>
        {!initial ? (
          <Field label="Contraseña" htmlFor="member-password">
            <TextInput
              id="member-password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </Field>
        ) : null}
        <Field label="Rol" htmlFor="member-role">
          <Select
            id="member-role"
            value={role}
            onChange={(event) => setRole(event.target.value as MemberRole)}
          >
            {roleOptions.map((option) => (
              <option key={option} value={option}>
                {option === 'member' ? 'Socio' : option === 'librarian' ? 'Bibliotecario' : 'Admin'}
              </option>
            ))}
          </Select>
        </Field>
        <Field label="Teléfono" htmlFor="member-phone">
          <TextInput
            id="member-phone"
            value={phone ?? ''}
            onChange={(event) => setPhone(event.target.value)}
          />
        </Field>
        <Field label="Dirección" htmlFor="member-address">
          <TextInput
            id="member-address"
            value={address ?? ''}
            onChange={(event) => setAddress(event.target.value)}
          />
        </Field>
      </div>

      {initial ? (
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={isActive}
            onChange={(event) => setIsActive(event.target.checked)}
          />
          Cuenta activa
        </label>
      ) : null}

      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" loading={mutation.isPending}>
          {initial ? 'Guardar cambios' : 'Crear socio'}
        </Button>
      </div>
    </form>
  )
}
