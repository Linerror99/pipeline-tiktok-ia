import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, Zap, ArrowRight } from 'lucide-react';
import { MatrixParticles } from '../components/MatrixParticles';
import { RotatingRings } from '../components/RotatingRings';
import { PulseButton } from '../components/PulseButton';
import { TiltCard } from '../components/TiltCard';
import { useAuth } from '../hooks/useAuth';
export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email);
    navigate('/dashboard');
  };
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 relative overflow-hidden">
      <MatrixParticles />
      <div className="bg-mesh-green" />

      {/* Background Rings */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-20 pointer-events-none">
        <RotatingRings size="xl" />
      </div>

      <motion.div
        initial={{
          opacity: 0,
          y: 30
        }}
        animate={{
          opacity: 1,
          y: 0
        }}
        transition={{
          duration: 0.8
        }}
        className="relative z-10 w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-10">
          <motion.div
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-lime-500 mb-6"
            animate={{
              rotate: [0, 5, -5, 0]
            }}
            transition={{
              duration: 4,
              repeat: Infinity
            }}>

            <Zap className="w-8 h-8 text-dark-900" />
          </motion.div>
          <h1 className="font-display text-4xl font-bold text-white mb-2">
            Welcome Back
          </h1>
          <p className="text-white/50">
            Sign in to continue creating amazing videos
          </p>
        </div>

        <TiltCard glowOnHover={false}>
          <div className="rotating-border rounded-2xl">
            <div className="relative z-10 bg-dark-800/90 rounded-2xl p-8">
              {/* Tabs */}
              <div className="flex mb-8 p-1 bg-emerald-500/10 rounded-xl">
                <button
                  onClick={() => setIsLogin(true)}
                  className={`flex-1 py-3 rounded-lg text-sm font-medium transition-all ${isLogin ? 'bg-emerald-500/20 text-emerald-400' : 'text-white/50 hover:text-white'}`}>

                  Sign In
                </button>
                <button
                  onClick={() => setIsLogin(false)}
                  className={`flex-1 py-3 rounded-lg text-sm font-medium transition-all ${!isLogin ? 'bg-emerald-500/20 text-emerald-400' : 'text-white/50 hover:text-white'}`}>

                  Sign Up
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm text-white/60">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      className="w-full bg-emerald-500/5 border border-emerald-500/20 rounded-xl py-4 pl-12 pr-4 text-white placeholder-white/30 focus:border-emerald-500/50 focus:shadow-glow-sm transition-all" />

                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm text-white/60">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30" />
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full bg-emerald-500/5 border border-emerald-500/20 rounded-xl py-4 pl-12 pr-4 text-white placeholder-white/30 focus:border-emerald-500/50 focus:shadow-glow-sm transition-all" />

                  </div>
                </div>

                <PulseButton
                  fullWidth
                  size="lg"
                  disabled={loading}
                  className="mt-8">

                  {loading ?
                  <span className="flex items-center justify-center">
                      <motion.div
                      animate={{
                        rotate: 360
                      }}
                      transition={{
                        duration: 1,
                        repeat: Infinity,
                        ease: 'linear'
                      }}
                      className="w-5 h-5 border-2 border-dark-900/30 border-t-dark-900 rounded-full mr-2" />

                      Signing in...
                    </span> :

                  <span className="flex items-center justify-center">
                      {isLogin ? 'Sign In' : 'Create Account'}
                      <ArrowRight className="ml-2 w-5 h-5" />
                    </span>
                  }
                </PulseButton>
              </form>

              <div className="mt-6 text-center">
                <a
                  href="#"
                  className="text-sm text-white/40 hover:text-emerald-400 transition-colors">

                  Forgot your password?
                </a>
              </div>
            </div>
          </div>
        </TiltCard>
      </motion.div>
    </div>);

}