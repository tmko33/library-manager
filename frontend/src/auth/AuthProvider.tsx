import type { ReactNode } from 'react'
import { useEffect, useMemo, useState } from 'react'

import { clearToken, getToken, setToken, setUnauthorizedHandler } from '../api/client'
import { authApi } from '../api/endpoints'
import type { Member } from '../api/types'
import { AuthContext } from './context'
import type { AuthContextValue } from './context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [member, setMember] = useState<Member | null>(null)
  const [loading, setLoading] = useState<boolean>(() => Boolean(getToken()))

  useEffect(() => {
    setUnauthorizedHandler(() => setMember(null))

    if (!getToken()) {
      return () => setUnauthorizedHandler(null)
    }

    let cancelled = false
    authApi
      .me()
      .then((profile) => {
        if (!cancelled) setMember(profile)
      })
      .catch(() => {
        clearToken()
        if (!cancelled) setMember(null)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
      setUnauthorizedHandler(null)
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      member,
      loading,
      login: async (email, password) => {
        const token = await authApi.login(email, password)
        setToken(token.access_token)
        setMember(await authApi.me())
      },
      register: async (payload) => {
        await authApi.register(payload)
        const token = await authApi.login(payload.email, payload.password)
        setToken(token.access_token)
        setMember(await authApi.me())
      },
      logout: () => {
        clearToken()
        setMember(null)
      },
    }),
    [member, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
