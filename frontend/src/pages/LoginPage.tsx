import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'
import { Alert } from '../components/Alert'
import { Button, Field, TextInput } from '../components/Controls'
import { errorMessage } from '../lib/errors'

const demoAccounts = [
  { label: 'Socio', email: 'member@library.dev' },
  { label: 'Bibliotecario', email: 'librarian@library.dev' },
  { label: 'Admin', email: 'admin@library.dev' },
]

export function LoginPage() {
  const { login, member } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('member@library.dev')
  const [password, setPassword] = useState('library12345')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (member) return <Navigate to="/" replace />

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await login(email, password)
      const from = (location.state as { from?: string } | null)?.from
      navigate(from ?? '/', { replace: true })
    } catch (caught) {
      setError(errorMessage(caught))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto grid max-w-4xl gap-6 md:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-slate-900">Ingresar</h1>
        <p className="mt-1 text-sm text-slate-500">
          Usa una cuenta demo o la que hayas registrado.
        </p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          {error ? <Alert kind="error">{error}</Alert> : null}

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
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </Field>

          <Button type="submit" loading={submitting} className="w-full">
            Entrar
          </Button>
        </form>

        <p className="mt-4 text-sm text-slate-500">
          ¿No tienes cuenta?{' '}
          <Link to="/register" className="font-medium text-indigo-600 hover:text-indigo-700">
            Regístrate
          </Link>
        </p>
      </div>

      <aside className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Cuentas demo
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          Contraseña: <code className="rounded bg-slate-100 px-1 py-0.5">library12345</code>
        </p>
        <ul className="mt-4 space-y-2">
          {demoAccounts.map((account) => (
            <li key={account.email}>
              <button
                type="button"
                onClick={() => {
                  setEmail(account.email)
                  setPassword('library12345')
                }}
                className="w-full rounded-lg border border-slate-200 px-3 py-2 text-left text-sm transition hover:border-indigo-300 hover:bg-indigo-50"
              >
                <span className="block font-medium text-slate-800">{account.label}</span>
                <span className="text-xs text-slate-500">{account.email}</span>
              </button>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  )
}
