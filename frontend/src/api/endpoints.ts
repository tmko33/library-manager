import { api, buildQuery } from './client'
import type {
  Author,
  AuthorPayload,
  Book,
  BookPayload,
  Branch,
  BranchPayload,
  Copy,
  CopyPayload,
  CopyStatus,
  CopyUpdatePayload,
  Country,
  Fine,
  Loan,
  LoanStatus,
  Member,
  MemberPayload,
  MemberUpdatePayload,
  Page,
  Publisher,
  PublisherPayload,
  Reservation,
  ReservationStatus,
  Token,
  RegisterPayload,
} from './types'

export interface PaginatedParams {
  page?: number
  size?: number
  q?: string
}

export interface BookListParams extends PaginatedParams {
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
  member_id?: number
  status_filter?: LoanStatus
  overdue?: boolean
}

export interface ReservationListParams {
  page?: number
  size?: number
  member_id?: number
  status_filter?: ReservationStatus
}

export interface FineListParams {
  page?: number
  size?: number
  member_id?: number
  status_filter?: 'pending' | 'paid' | 'waived'
}

export interface CopyListParams {
  page?: number
  size?: number
  book_id?: number
  branch_id?: number
  status_filter?: CopyStatus
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
  create: (payload: BookPayload) =>
    api<Book>('/api/v1/books', { method: 'POST', json: payload }),
  update: (id: number, payload: Partial<BookPayload>) =>
    api<Book>(`/api/v1/books/${id}`, { method: 'PATCH', json: payload }),
  remove: (id: number) => api<void>(`/api/v1/books/${id}`, { method: 'DELETE' }),
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
  pay: (id: number) => api<Fine>(`/api/v1/fines/${id}/pay`, { method: 'POST' }),
  waive: (id: number) => api<Fine>(`/api/v1/fines/${id}/waive`, { method: 'POST' }),
}

export const authorsApi = {
  list: (params: PaginatedParams = {}) =>
    api<Page<Author>>(`/api/v1/authors${buildQuery({ ...params })}`),
  create: (payload: AuthorPayload) =>
    api<Author>('/api/v1/authors', { method: 'POST', json: payload }),
  update: (id: number, payload: Partial<AuthorPayload>) =>
    api<Author>(`/api/v1/authors/${id}`, { method: 'PATCH', json: payload }),
  remove: (id: number) => api<void>(`/api/v1/authors/${id}`, { method: 'DELETE' }),
}

export const publishersApi = {
  list: (params: PaginatedParams = {}) =>
    api<Page<Publisher>>(`/api/v1/publishers${buildQuery({ ...params })}`),
  create: (payload: PublisherPayload) =>
    api<Publisher>('/api/v1/publishers', { method: 'POST', json: payload }),
  update: (id: number, payload: Partial<PublisherPayload>) =>
    api<Publisher>(`/api/v1/publishers/${id}`, { method: 'PATCH', json: payload }),
  remove: (id: number) =>
    api<void>(`/api/v1/publishers/${id}`, { method: 'DELETE' }),
}

export const branchesApi = {
  list: (params: PaginatedParams & { city?: string; is_active?: boolean } = {}) =>
    api<Page<Branch>>(`/api/v1/branches${buildQuery({ ...params })}`),
  create: (payload: BranchPayload) =>
    api<Branch>('/api/v1/branches', { method: 'POST', json: payload }),
  update: (id: number, payload: Partial<BranchPayload>) =>
    api<Branch>(`/api/v1/branches/${id}`, { method: 'PATCH', json: payload }),
  remove: (id: number) => api<void>(`/api/v1/branches/${id}`, { method: 'DELETE' }),
}

export const countriesApi = {
  list: (params: PaginatedParams = {}) =>
    api<Page<Country>>(`/api/v1/countries${buildQuery({ ...params })}`),
}

export const copiesApi = {
  list: (params: CopyListParams = {}) =>
    api<Page<Copy>>(`/api/v1/copies${buildQuery({ ...params })}`),
  create: (payload: CopyPayload) =>
    api<Copy>('/api/v1/copies', { method: 'POST', json: payload }),
  update: (id: number, payload: CopyUpdatePayload) =>
    api<Copy>(`/api/v1/copies/${id}`, { method: 'PATCH', json: payload }),
  remove: (id: number) => api<void>(`/api/v1/copies/${id}`, { method: 'DELETE' }),
}

export const membersApi = {
  list: (params: PaginatedParams & { is_active?: boolean } = {}) =>
    api<Page<Member>>(`/api/v1/members${buildQuery({ ...params })}`),
  create: (payload: MemberPayload) =>
    api<Member>('/api/v1/members', { method: 'POST', json: payload }),
  update: (id: number, payload: MemberUpdatePayload) =>
    api<Member>(`/api/v1/members/${id}`, { method: 'PATCH', json: payload }),
  deactivate: (id: number) =>
    api<void>(`/api/v1/members/${id}`, { method: 'DELETE' }),
}
