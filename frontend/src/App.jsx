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

  return (
    <Routes>
      {/* Login/register routes removed for prototype - always show dashboard */}

      {/* No auth gating - render Layout and all pages directly for prototype */}
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

      {/* Fallback - always go to dashboard for prototype */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
