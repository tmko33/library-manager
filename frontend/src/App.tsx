import { Navigate, Route, Routes } from 'react-router-dom'

import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { StaffLayout } from './components/StaffLayout'
import { StaffRoute } from './components/StaffRoute'
import { AccountPage } from './pages/AccountPage'
import { BookDetailPage } from './pages/BookDetailPage'
import { CataloguePage } from './pages/CataloguePage'
import { LoginPage } from './pages/LoginPage'
import { MyLoansPage } from './pages/MyLoansPage'
import { MyReservationsPage } from './pages/MyReservationsPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { RegisterPage } from './pages/RegisterPage'
import { StaffAuthorsPage } from './pages/staff/StaffAuthorsPage'
import { StaffBooksPage } from './pages/staff/StaffBooksPage'
import { StaffBranchesPage } from './pages/staff/StaffBranchesPage'
import { StaffCopiesPage } from './pages/staff/StaffCopiesPage'
import { StaffFinesPage } from './pages/staff/StaffFinesPage'
import { StaffLoansPage } from './pages/staff/StaffLoansPage'
import { StaffMembersPage } from './pages/staff/StaffMembersPage'
import { StaffPublishersPage } from './pages/staff/StaffPublishersPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<CataloguePage />} />
        <Route path="books/:id" element={<BookDetailPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="loans" element={<MyLoansPage />} />
          <Route path="reservations" element={<MyReservationsPage />} />
          <Route path="account" element={<AccountPage />} />
        </Route>
        <Route element={<StaffRoute />}>
          <Route path="staff" element={<StaffLayout />}>
            <Route index element={<Navigate to="/staff/books" replace />} />
            <Route path="books" element={<StaffBooksPage />} />
            <Route path="authors" element={<StaffAuthorsPage />} />
            <Route path="publishers" element={<StaffPublishersPage />} />
            <Route path="branches" element={<StaffBranchesPage />} />
            <Route path="copies" element={<StaffCopiesPage />} />
            <Route path="members" element={<StaffMembersPage />} />
            <Route path="loans" element={<StaffLoansPage />} />
            <Route path="fines" element={<StaffFinesPage />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}
