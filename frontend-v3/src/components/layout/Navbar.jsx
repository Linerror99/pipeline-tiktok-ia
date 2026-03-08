import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X } from 'lucide-react'
import Logo from '../ui/Logo'
import { useAuth } from '../../contexts/AuthContext'

const NAV_LINKS = [
  { label: 'Fonctionnalités', href: '/#features' },
  { label: 'Comment ça marche', href: '/#how-it-works' },
  { label: 'Tarifs', href: '/#pricing' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const { isAuthenticated, logout, user } = useAuth()
  const location = useLocation()
  const isLanding = location.pathname === '/'

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <>
      <motion.nav
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
          scrolled
            ? 'bg-reetik-black/80 backdrop-blur-xl border-b border-reetik-border/50'
            : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-20">
            {/* Logo */}
            <Link to={isAuthenticated ? '/dashboard' : '/'} className="text-white hover:text-reetik-gold transition-colors">
              <Logo className="h-7" />
            </Link>

            {/* Desktop Nav Links */}
            {isLanding && (
              <div className="hidden md:flex items-center gap-8">
                {NAV_LINKS.map((link) => (
                  <a
                    key={link.label}
                    href={link.href}
                    className="text-sm text-reetik-gray-300 hover:text-white transition-colors duration-300"
                  >
                    {link.label}
                  </a>
                ))}
              </div>
            )}

            {/* Right side */}
            <div className="hidden md:flex items-center gap-4">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/dashboard"
                    className="text-sm text-reetik-gray-300 hover:text-white transition-colors"
                  >
                    Dashboard
                  </Link>
                  <div className="flex items-center gap-3">
                    {user?.picture && (
                      <img src={user.picture} alt="" className="w-8 h-8 rounded-full border border-reetik-border" />
                    )}
                    <button
                      onClick={logout}
                      className="text-sm text-reetik-gray-400 hover:text-white transition-colors"
                    >
                      Déconnexion
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="px-5 py-2 text-sm text-reetik-gray-200 rounded-full border border-reetik-border
                               hover:border-white/40 hover:bg-white/5 transition-all duration-300"
                  >
                    Se connecter
                  </Link>
                  <Link
                    to="/login"
                    className="group px-5 py-2 text-sm rounded-full border border-reetik-gold text-reetik-gold
                               hover:bg-reetik-gold hover:text-reetik-black transition-all duration-300
                               flex items-center gap-2"
                  >
                    Commencer
                    <span className="transition-transform duration-300 group-hover:translate-x-1">›</span>
                  </Link>
                </>
              )}
            </div>

            {/* Mobile hamburger */}
            <button
              className="md:hidden text-white p-2"
              onClick={() => setMobileOpen(!mobileOpen)}
            >
              {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </motion.nav>

      {/* Mobile menu overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-0 z-40 bg-reetik-black/95 backdrop-blur-xl pt-20 px-6 md:hidden"
          >
            <div className="flex flex-col gap-6">
              {isLanding &&
                NAV_LINKS.map((link) => (
                  <a
                    key={link.label}
                    href={link.href}
                    onClick={() => setMobileOpen(false)}
                    className="text-lg text-reetik-gray-200 hover:text-reetik-gold transition-colors"
                  >
                    {link.label}
                  </a>
                ))}
              <div className="pt-4 border-t border-reetik-border">
                {isAuthenticated ? (
                  <>
                    <Link to="/dashboard" onClick={() => setMobileOpen(false)} className="block py-3 text-white">
                      Dashboard
                    </Link>
                    <button onClick={() => { logout(); setMobileOpen(false) }} className="text-reetik-gray-400">
                      Déconnexion
                    </button>
                  </>
                ) : (
                  <Link
                    to="/login"
                    onClick={() => setMobileOpen(false)}
                    className="inline-block px-6 py-3 rounded-full border border-reetik-gold text-reetik-gold"
                  >
                    Commencer
                  </Link>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
