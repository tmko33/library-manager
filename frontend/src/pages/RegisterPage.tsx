import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'
import { Alert } from '../components/Alert'
import { Button, Field, TextInput } from '../components/Controls'
import { errorMessage } from '../lib/errors'

export function RegisterPage() {
  const { register, member } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [phone, setPhone] = useState('')
  const [address, setAddress] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (member) return <Navigate to="/" replace />

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await register({
        email,
        password,
        full_name: fullName,
        phone: phone || undefined,
        address: address || undefined,
      })
      navigate('/', { replace: true })
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-lg rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="text-2xl font-semibold text-slate-900">Crear cuenta</h1>
      <p className="mt-1 text-sm text-slate-500">
        Las cuentas creadas aquí son de tipo socio.
      </p>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        {error ? <Alert kind="error">{error}</Alert> : null}

        <Field label="Nombre completo" htmlFor="full_name">
          <TextInput
            id="full_name"
            required
            minLength={2}
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
          />
        </Field>

        <Field label="Correo electrónico" htmlFor="email">
          <TextInput
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </Field>

        <Field label="Contraseña" htmlFor="password">
          <TextInput
            id="password"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Teléfono (opcional)" htmlFor="phone">
            <TextInput
              id="phone"
              value={phone}
              onChange={(event) => setPhone(event.target.value)}
            />
          </Field>
          <Field label="Dirección (opcional)" htmlFor="address">
            <TextInput
              id="address"
              value={address}
              onChange={(event) => setAddress(event.target.value)}
            />
          </Field>
        </div>

        <Button type="submit" loading={submitting} className="w-full">
          Crear cuenta y entrar
        </Button>
      </form>

      <p className="mt-4 text-sm text-slate-500">
        ¿Ya tienes cuenta?{' '}
        <Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-700">
          Inicia sesión
        </Link>
      </p>
    </div>
  )
}
