import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Auth from './pages/Auth';
import CreateVideo from './pages/CreateVideo';
import MyVideos from './pages/MyVideos';
import Dashboard from './pages/Dashboard';
import Logs from './pages/Logs';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Route publique */}
          <Route path="/auth" element={<Auth />} />
          
          {/* Routes protégées */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout>
                <CreateVideo />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/create" element={
            <ProtectedRoute>
              <Layout>
                <CreateVideo />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/my-videos" element={
            <ProtectedRoute>
              <Layout>
                <MyVideos />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } />
          <Route path="/logs" element={
            <ProtectedRoute>
              <Layout>
                <Logs />
              </Layout>
            </ProtectedRoute>
          } />

          {/* Redirect any unknown route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
