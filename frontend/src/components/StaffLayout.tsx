import { NavLink, Outlet } from 'react-router-dom'

import { cn } from '../lib/cn'

const tabs = [
  { to: '/staff/books', label: 'Libros' },
  { to: '/staff/authors', label: 'Autores' },
  { to: '/staff/publishers', label: 'Editoriales' },
  { to: '/staff/branches', label: 'Sucursales' },
  { to: '/staff/copies', label: 'Copias' },
  { to: '/staff/members', label: 'Socios' },
  { to: '/staff/loans', label: 'Préstamos' },
  { to: '/staff/fines', label: 'Multas' },
]

export function StaffLayout() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Panel de staff</h1>
        <p className="mt-1 text-sm text-slate-500">
          Gestión del catálogo, ejemplares, socios y circulación.
        </p>
      </div>

      <nav className="flex flex-wrap gap-1 rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
        {tabs.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to}
            className={({ isActive }) =>
              cn(
                'rounded-lg px-3 py-2 text-sm font-medium transition',
                isActive
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-600 hover:bg-slate-100',
              )
            }
          >
            {tab.label}
          </NavLink>
        ))}
      </nav>

      <Outlet />
    </div>
  )
}
