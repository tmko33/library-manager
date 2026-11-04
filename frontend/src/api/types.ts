export type MemberRole = 'admin' | 'librarian' | 'member'

export interface Member {
  id: number
  email: string
  full_name: string
  phone?: string | null
  address?: string | null
  role: MemberRole
  is_active: boolean
  membership_expires_at?: string | null
  created_at: string
}

export interface AuthorBrief {
  id: number
  name: string
}

export interface PublisherBrief {
  id: number
  name: string
}

export interface BookBrief {
  id: number
  isbn: string
  title: string
}

export interface MemberBrief {
  id: number
  full_name: string
  email: string
}

export interface Book {
  id: number
  isbn: string
  title: string
  publication_year?: number | null
  summary?: string | null
  language: string
  pages?: number | null
  cover_url?: string | null
  publisher_id?: number | null
  authors: AuthorBrief[]
  publisher?: PublisherBrief | null
  total_copies: number
  available_copies: number
}

export type LoanStatus = 'active' | 'returned' | 'overdue'

export interface Loan {
  id: number
  copy_id: number
  member_id: number
  loaned_by_id?: number | null
  book?: BookBrief | null
  member?: MemberBrief | null
  loan_date: string
  due_date: string
  returned_at?: string | null
  status: LoanStatus
  renewals: number
  created_at: string
}

export type ReservationStatus = 'pending' | 'fulfilled' | 'cancelled' | 'expired'

export interface Reservation {
  id: number
  book_id: number
  member_id: number
  book?: BookBrief | null
  member?: MemberBrief | null
  status: ReservationStatus
  expires_at?: string | null
  created_at: string
}

export type FineStatus = 'pending' | 'paid' | 'waived'

export interface Fine {
  id: number
  loan_id: number
  amount: string
  reason: string
  status: FineStatus
  paid_at?: string | null
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
  expires_in: number
}

export interface Page<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ApiProblem {
  type?: string
  title?: string
  status?: number
  detail?: string
  instance?: string
  code?: string
  errors?: Array<{ field: string; message: string; type: string }>
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  phone?: string
  address?: string
}
