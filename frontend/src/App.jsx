import { Routes, Route, Navigate, Outlet } from 'react-router-dom'

import { useAuth } from './contexts/AuthContext'

import Layout from './components/Layout.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Career from './pages/Career.jsx'
import Habits from './pages/Habits.jsx'
import Finance from './pages/Finance.jsx'
import Mood from './pages/Mood.jsx'
import Motivation from './pages/Motivation.jsx'
import Profile from './pages/Profile.jsx'
import AnimationDemo from './pages/AnimationDemo.jsx'

function App() {
  const { user, loading } = useAuth()

  // Simple loading fallback while auth state initializes
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="spinner w-8 h-8" role="status" aria-label="Loading" />
      </div>
    )
  }

  // RequireAuth renders children via <Outlet /> when user is authenticated
  const RequireAuth = () => {
    const { user: currentUser } = useAuth()
    if (!currentUser) return <Navigate to="/login" replace />
    return <Outlet />
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected routes */}
      <Route element={<RequireAuth />}>
        <Route element={<Layout />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="career" element={<Career />} />
          <Route path="habits" element={<Habits />} />
          <Route path="finance" element={<Finance />} />
          <Route path="mood" element={<Mood />} />
          <Route path="motivation" element={<Motivation />} />
          <Route path="profile" element={<Profile />} />
          <Route path="demo" element={<AnimationDemo />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to={user ? '/dashboard' : '/login'} replace />} />
    </Routes>
  )
}

export default App
