import { Link } from 'react-router-dom'

import type { Book } from '../api/types'
import { AvailabilityBadge } from './StatusBadge'

export function BookCard({ book }: { book: Book }) {
  const authors = book.authors.map((author) => author.name).join(', ')

  return (
    <Link
      to={`/books/${book.id}`}
      className="group flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-300 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
          {book.publication_year ?? 's. f.'}
        </span>
        <AvailabilityBadge available={book.available_copies} total={book.total_copies} />
      </div>

      <div>
        <h3 className="text-base font-semibold leading-snug text-slate-900 group-hover:text-indigo-700">
          {book.title}
        </h3>
        <p className="mt-1 text-sm text-slate-600">{authors || 'Autor desconocido'}</p>
      </div>

      {book.summary ? (
        <p className="line-clamp-2 text-sm text-slate-500">{book.summary}</p>
      ) : null}

      <div className="mt-auto flex items-center justify-between text-xs text-slate-400">
        <span>ISBN {book.isbn}</span>
        <span>{book.pages ? `${book.pages} págs.` : ''}</span>
      </div>
    </Link>
  )
}
