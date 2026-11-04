import { createContext } from 'react'

import type { Member, RegisterPayload } from '../api/types'

export interface AuthContextValue {
  member: Member | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
