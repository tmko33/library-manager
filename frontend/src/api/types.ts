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

export interface Country {
  id: number
  name: string
  iso_code?: string | null
}

export interface Author {
  id: number
  name: string
  bio?: string | null
  birth_year?: number | null
  country_id?: number | null
  country?: Country | null
}

export interface Publisher {
  id: number
  name: string
  website?: string | null
}

export interface Branch {
  id: number
  name: string
  address: string
  city: string
  country_id?: number | null
  is_active: boolean
  country?: Country | null
}

export type CopyStatus = 'available' | 'on_loan' | 'reserved' | 'lost' | 'maintenance'

export interface Copy {
  id: number
  inventory_code: string
  book_id: number
  branch_id: number
  status: CopyStatus
  acquired_at?: string | null
  notes?: string | null
  book?: BookBrief
  branch?: Pick<Branch, 'id' | 'name' | 'city'>
}

export interface BookPayload {
  isbn: string
  title: string
  publication_year?: number | null
  summary?: string | null
  language: string
  pages?: number | null
  cover_url?: string | null
  publisher_id?: number | null
  author_ids: number[]
}

export interface AuthorPayload {
  name: string
  bio?: string | null
  birth_year?: number | null
  country_id?: number | null
}

export interface PublisherPayload {
  name: string
  website?: string | null
}

export interface BranchPayload {
  name: string
  address: string
  city: string
  country_id?: number | null
  is_active: boolean
}

export interface CopyPayload {
  book_id: number
  branch_id: number
  inventory_code: string
  acquired_at?: string | null
  notes?: string | null
}

export interface CopyUpdatePayload {
  branch_id?: number
  status?: CopyStatus
  notes?: string | null
}

export interface MemberPayload {
  email: string
  password: string
  full_name: string
  phone?: string | null
  address?: string | null
  role: MemberRole
  membership_expires_at?: string | null
}

export interface MemberUpdatePayload {
  email?: string
  full_name?: string
  phone?: string | null
  address?: string | null
  role?: MemberRole
  is_active?: boolean
  membership_expires_at?: string | null
}

