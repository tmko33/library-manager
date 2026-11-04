import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-10 text-center shadow-sm">
      <p className="text-5xl font-semibold text-indigo-600">404</p>
      <h1 className="mt-3 text-xl font-semibold text-slate-900">Página no encontrada</h1>
      <p className="mt-2 text-sm text-slate-500">La ruta que buscas no existe.</p>
      <Link
        to="/"
        className="mt-6 inline-flex rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
      >
        Volver al catálogo
      </Link>
    </div>
  )
}
