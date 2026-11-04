import { api, buildQuery } from './client'
import type {
  Book,
  Fine,
  Loan,
  LoanStatus,
  Member,
  Page,
  RegisterPayload,
  Reservation,
  ReservationStatus,
  Token,
} from './types'

export interface BookListParams {
  page?: number
  size?: number
  q?: string
  available?: boolean
  author_id?: number
  publisher_id?: number
  year?: number
  sort?: 'title' | 'publication_year' | 'created_at'
  order?: 'asc' | 'desc'
}

export interface LoanListParams {
  page?: number
  size?: number
  status_filter?: LoanStatus
  overdue?: boolean
}

export interface ReservationListParams {
  page?: number
  size?: number
  status_filter?: ReservationStatus
}

export interface FineListParams {
  page?: number
  size?: number
}

export const authApi = {
  login: (email: string, password: string) =>
    api<Token>('/api/v1/auth/login', { method: 'POST', form: { username: email, password } }),
  register: (payload: RegisterPayload) =>
    api<Member>('/api/v1/auth/register', { method: 'POST', json: payload }),
  me: () => api<Member>('/api/v1/auth/me'),
}

export const booksApi = {
  list: (params: BookListParams = {}) =>
    api<Page<Book>>(`/api/v1/books${buildQuery({ ...params })}`),
  get: (id: number) => api<Book>(`/api/v1/books/${id}`),
}

export const loansApi = {
  list: (params: LoanListParams = {}) =>
    api<Page<Loan>>(`/api/v1/loans${buildQuery({ ...params })}`),
  borrow: (bookId: number) =>
    api<Loan>('/api/v1/loans', { method: 'POST', json: { book_id: bookId } }),
  renew: (id: number) => api<Loan>(`/api/v1/loans/${id}/renew`, { method: 'POST' }),
  return: (id: number) => api<Loan>(`/api/v1/loans/${id}/return`, { method: 'POST' }),
}

export const reservationsApi = {
  list: (params: ReservationListParams = {}) =>
    api<Page<Reservation>>(`/api/v1/reservations${buildQuery({ ...params })}`),
  create: (bookId: number) =>
    api<Reservation>('/api/v1/reservations', { method: 'POST', json: { book_id: bookId } }),
  cancel: (id: number) =>
    api<Reservation>(`/api/v1/reservations/${id}`, { method: 'DELETE' }),
}

export const finesApi = {
  list: (params: FineListParams = {}) =>
    api<Page<Fine>>(`/api/v1/fines${buildQuery({ ...params })}`),
}
