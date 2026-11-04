import type { ApiProblem } from './types'

const API_BASE = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')
const TOKEN_KEY = 'library-manager.token'

export class ApiError extends Error {
  readonly status: number
  readonly code?: string
  readonly errors?: ApiProblem['errors']

  constructor(status: number, message: string, code?: string, errors?: ApiProblem['errors']) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.errors = errors
  }
}

type UnauthorizedHandler = () => void
let unauthorizedHandler: UnauthorizedHandler | null = null

export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
  unauthorizedHandler = handler
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  json?: unknown
  form?: Record<string, string>
  signal?: AbortSignal
}

export async function api<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', json, form, signal } = options
  const headers = new Headers()
  const token = getToken()

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let body: BodyInit | undefined
  if (json !== undefined) {
    headers.set('Content-Type', 'application/json')
    body = JSON.stringify(json)
  } else if (form) {
    body = new URLSearchParams(form)
  }

  const response = await fetch(`${API_BASE}${path}`, { method, headers, body, signal })

  if (response.status === 401 && token) {
    clearToken()
    unauthorizedHandler?.()
  }

  if (!response.ok) {
    let problem: ApiProblem | null = null
    try {
      problem = (await response.json()) as ApiProblem
    } catch {
      problem = null
    }
    throw new ApiError(
      response.status,
      problem?.detail ?? problem?.title ?? response.statusText,
      problem?.code,
      problem?.errors,
    )
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export function buildQuery(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value))
    }
  }
  const query = search.toString()
  return query ? `?${query}` : ''
}
