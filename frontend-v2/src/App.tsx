import React from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation } from
'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Sidebar } from './components/Sidebar';
import { MobileNav } from './components/MobileNav';
import { useAuth } from './hooks/useAuth';
// Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { CreateVideoPage } from './pages/CreateVideoPage';
import { GenerationProgressPage } from './pages/GenerationProgressPage';
import { LibraryPage } from './pages/LibraryPage';
import { VideoPlayerPage } from './pages/VideoPlayerPage';
function AnimatedRoutes() {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{
          opacity: 0,
          y: 10
        }}
        animate={{
          opacity: 1,
          y: 0
        }}
        exit={{
          opacity: 0,
          y: -10
        }}
        transition={{
          duration: 0.3
        }}
        className="w-full">

        <Routes location={location}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/create" element={<CreateVideoPage />} />
          <Route path="/progress/:id" element={<GenerationProgressPage />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/video/:id" element={<VideoPlayerPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </motion.div>
    </AnimatePresence>);

}
function Layout({ children }: {children: React.ReactNode;}) {
  const { user, logout } = useAuth();
  const location = useLocation();
  // Pages without sidebar
  const fullscreenPages = ['/', '/login', '/video', '/progress'];
  const isFullscreen = fullscreenPages.some(
    (page) =>
    location.pathname === page ||
    location.pathname.startsWith('/video/') ||
    location.pathname.startsWith('/progress/')
  );
  return (
    <div className="min-h-screen relative">
      {/* Background */}
      <div className="bg-mesh-green" />

      {/* Navigation */}
      {!isFullscreen &&
      <>
          <Sidebar user={user} onLogout={logout} />
          <MobileNav />
        </>
      }

      {/* Main Content */}
      <main
        className={`relative z-10 ${!isFullscreen ? 'md:ml-72 pb-24 md:pb-0' : ''} min-h-screen`}>

        {children}
      </main>
    </div>);

}
export function App() {
  return (
    <BrowserRouter>
      <Layout>
        <AnimatedRoutes />
      </Layout>
    </BrowserRouter>);

}