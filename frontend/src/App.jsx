import { Routes, Route, Navigate } from 'react-router-dom'
import React, { Suspense, lazy } from 'react'

import { useAuth } from './contexts/AuthContext'

import Layout from './components/Layout.jsx'
const Dashboard = lazy(() => import('./pages/Dashboard.jsx'))
const Career = lazy(() => import('./pages/Career.jsx'))
const Habits = lazy(() => import('./pages/Habits.jsx'))
const Finance = lazy(() => import('./pages/Finance.jsx'))
// Mood is now consolidated into Journal; keep route for backward-compat
const Mood = lazy(() => import('./pages/Mood.jsx'))
const Journal = lazy(() => import('./pages/Journal.jsx'))
const Motivation = lazy(() => import('./pages/Motivation.jsx'))
const Profile = lazy(() => import('./pages/Profile.jsx'))
const AssistantBuilder = lazy(() => import('./pages/AssistantBuilder.jsx'))
const RealityCheck = lazy(() => import('./pages/RealityCheck.jsx'))
const Onboarding = lazy(() => import('./pages/Onboarding.jsx'))
const Assistant = lazy(() => import('./pages/Assistant.jsx'))

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
        <Route path="dashboard" element={<Suspense fallback={<div className="p-6">Loading…</div>}><Dashboard /></Suspense>} />
        <Route path="career" element={<Suspense fallback={<div className="p-6">Loading…</div>}><Career /></Suspense>} />
        <Route path="habits" element={<Suspense fallback={<div className="p-6">Loading…</div>}><Habits /></Suspense>} />
        <Route path="finance" element={<Suspense fallback={<div className="p-6">Loading…</div>}><Finance /></Suspense>} />
  <Route path="mood" element={<Navigate to="/journal" replace />} />
  <Route path="journal" element={<Suspense fallback={<div className="p-6">Loading…</div>}><Journal /></Suspense>} />
        <Route path="motivation" element={<Suspense fallback={<div className="p-6">Loading…</div>}><Motivation /></Suspense>} />
        <Route path="profile" element={<Suspense fallback={<div className="p-6">Loading…</div>}><Profile /></Suspense>} />
        <Route path="assistant-builder" element={<Suspense fallback={<div className="p-6">Loading…</div>}><AssistantBuilder /></Suspense>} />
        <Route path="reality-check" element={<Suspense fallback={<div className="p-6">Loading…</div>}><RealityCheck /></Suspense>} />
  <Route path="assistant" element={<Suspense fallback={<div className="p-6">Loading…</div>}><Assistant /></Suspense>} />
  <Route path="onboarding" element={<Suspense fallback={<div className="p-6">Loading…</div>}><Onboarding /></Suspense>} />
  {/** Animation Demo route removed */}
      </Route>

      {/* Fallback - always go to dashboard for prototype */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
