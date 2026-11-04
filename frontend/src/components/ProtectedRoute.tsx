import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'
import { FullPageSpinner } from './Feedback'

export function ProtectedRoute() {
  const { member, loading } = useAuth()
  const location = useLocation()

  if (loading) return <FullPageSpinner />
  if (!member) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}
