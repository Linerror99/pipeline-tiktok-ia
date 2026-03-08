import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Lock, LogIn, Loader2, AlertCircle } from 'lucide-react'
import Logo from '../components/ui/Logo'
import { useAuth } from '../contexts/AuthContext'

export default function LoginPage() {
  const { codeVerified, verifyCode, login } = useAuth()
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleVerifyCode = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await verifyCode(code)
    } catch {
      setError('Code d\'accès invalide.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    setError('')
    setLoading(true)
    try {
      await login()
      navigate('/dashboard')
    } catch {
      setError('Erreur lors de la connexion Google.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 grid-lines opacity-20" />
      <div className="absolute inset-0 bg-gradient-radial from-reetik-gold/[0.02] via-transparent to-transparent" />

      {/* Decorative arcs */}
      <svg className="absolute bottom-0 left-0 w-[500px] h-[500px] opacity-[0.05]" viewBox="0 0 500 500">
        <circle cx="0" cy="500" r="250" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
        <circle cx="0" cy="500" r="350" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
      </svg>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="relative z-10 w-full max-w-md px-6"
      >
        <div className="text-center mb-10">
          <div className="flex justify-center text-white mb-6">
            <Logo className="h-10" />
          </div>
          <h1 className="font-serif text-3xl text-reetik-cream">
            {codeVerified ? 'Connexion' : 'Accès'}
          </h1>
          <p className="mt-2 text-sm text-reetik-gray-400">
            {codeVerified
              ? 'Connectez-vous avec votre compte Google.'
              : 'Entrez votre code d\'accès pour continuer.'}
          </p>
        </div>

        <div className="card-hover-glow rounded-2xl bg-reetik-card/60 backdrop-blur-sm p-8">
          {/* Error */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
            >
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </motion.div>
          )}

          {!codeVerified ? (
            /* Step 1: Access Code */
            <form onSubmit={handleVerifyCode} className="space-y-6">
              <div>
                <label className="block text-xs uppercase tracking-wider text-reetik-gray-400 mb-2">
                  Code d'accès
                </label>
                <div className="relative">
                  <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-reetik-gray-500" />
                  <input
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="Entrez le code"
                    className="w-full pl-11 pr-4 py-3.5 rounded-xl bg-reetik-dark border border-reetik-border
                               text-white placeholder-reetik-gray-500
                               focus:outline-none focus:border-reetik-gold/50 focus:ring-1 focus:ring-reetik-gold/20
                               transition-all duration-300"
                    required
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={loading || !code}
                className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl
                           bg-reetik-gold text-reetik-black font-medium
                           hover:bg-reetik-gold-light transition-all duration-300
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Vérifier'}
              </button>
            </form>
          ) : (
            /* Step 2: Google Sign-In */
            <div className="space-y-6">
              <button
                onClick={handleGoogleLogin}
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 py-3.5 rounded-xl
                           border border-reetik-border bg-white/[0.03]
                           text-white font-medium
                           hover:border-white/30 hover:bg-white/[0.06] transition-all duration-300
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    {/* Google icon */}
                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                    </svg>
                    Continuer avec Google
                  </>
                )}
              </button>
              <p className="text-xs text-center text-reetik-gray-500">
                En continuant, vous acceptez les conditions d'utilisation.
              </p>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
