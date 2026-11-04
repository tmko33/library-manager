import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'
import { cn } from '../lib/cn'
import { Button } from './Controls'
import { StatusBadge } from './StatusBadge'

function navClass({ isActive }: { isActive: boolean }) {
  return cn(
    'rounded-lg px-3 py-2 text-sm font-medium transition',
    isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-100',
  )
}

export function Layout() {
  const { member, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-4 px-4 py-3">
          <Link to="/" className="flex items-center gap-2 text-slate-900">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600 text-white">
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 5.5A2.5 2.5 0 016.5 3H20v16.5H6.5A2.5 2.5 0 004 22V5.5z" />
                <path d="M4 19a2.5 2.5 0 012.5-2.5H20" />
              </svg>
            </span>
            <span className="text-lg font-semibold">Biblioteca</span>
          </Link>

          <nav className="flex flex-1 flex-wrap items-center gap-1">
            <NavLink to="/" end className={navClass}>
              Catálogo
            </NavLink>
            {member ? (
              <>
                <NavLink to="/loans" className={navClass}>
                  Mis préstamos
                </NavLink>
                <NavLink to="/reservations" className={navClass}>
                  Mis reservas
                </NavLink>
                <NavLink to="/account" className={navClass}>
                  Mi cuenta
                </NavLink>
              </>
            ) : null}
          </nav>

          {member ? (
            <div className="flex items-center gap-3">
              <div className="hidden text-right sm:block">
                <p className="text-sm font-medium text-slate-800">{member.full_name}</p>
                <div className="mt-0.5 flex justify-end">
                  <StatusBadge status={member.role} />
                </div>
              </div>
              <Button
                variant="secondary"
                onClick={() => {
                  logout()
                  navigate('/')
                }}
              >
                Salir
              </Button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Button variant="ghost" onClick={() => navigate('/login')}>
                Ingresar
              </Button>
              <Button onClick={() => navigate('/register')}>Crear cuenta</Button>
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-4 text-xs text-slate-500">
          <span>Library Manager API · demo de portafolio</span>
          <a
            className="hover:text-indigo-600"
            href="https://github.com/tmko33/library-manager"
            target="_blank"
            rel="noreferrer"
          >
            Código fuente
          </a>
        </div>
      </footer>
    </div>
  )
}
