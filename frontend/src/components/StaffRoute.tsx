import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'
import { FullPageSpinner } from './Feedback'

export function StaffRoute() {
  const { member, loading } = useAuth()

  if (loading) return <FullPageSpinner />
  if (!member) return <Navigate to="/login" replace />
  if (member.role === 'member') return <Navigate to="/" replace />
  return <Outlet />
}
