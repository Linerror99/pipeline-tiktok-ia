import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Navbar from './components/layout/Navbar'
import Footer from './components/layout/Footer'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ProjectPage from './pages/ProjectPage'
import { Loader2 } from 'lucide-react'

function ProtectedRoute({ children }) {
  const { user, loading, codeVerified } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-reetik-black">
        <Loader2 className="w-8 h-8 animate-spin text-reetik-gold" />
      </div>
    )
  }

  if (!codeVerified || !user) {
    return <Navigate to="/login" replace />
  }

  return children
}

function AppRoutes() {
  return (
    <div className="min-h-screen flex flex-col bg-reetik-black text-white">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:id"
            element={
              <ProtectedRoute>
                <ProjectPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
