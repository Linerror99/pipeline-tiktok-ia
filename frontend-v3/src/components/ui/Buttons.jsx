import { motion } from 'framer-motion'
import { ArrowRight, Loader2 } from 'lucide-react'

export function GoldButton({ children, onClick, loading, className = '', ...props }) {
  return (
    <motion.button
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      disabled={loading}
      className={`group relative inline-flex items-center gap-3 px-7 py-3.5 rounded-full
                  border border-reetik-gold text-reetik-gold font-medium text-sm
                  transition-all duration-300
                  hover:bg-reetik-gold hover:text-reetik-black
                  disabled:opacity-50 disabled:cursor-not-allowed
                  ${className}`}
      {...props}
    >
      {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : children}
      <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
    </motion.button>
  )
}

export function SecondaryButton({ children, onClick, className = '', ...props }) {
  return (
    <motion.button
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`inline-flex items-center gap-2 px-7 py-3.5 rounded-full
                  border border-reetik-border text-white font-medium text-sm
                  transition-all duration-300
                  hover:border-white/40 hover:bg-white/5
                  ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  )
}

export function IconButton({ children, onClick, className = '', ...props }) {
  return (
    <motion.button
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`p-2 rounded-lg text-reetik-gray-300 transition-colors
                  hover:text-white hover:bg-white/10
                  ${className}`}
      {...props}
    >
      {children}
    </motion.button>
  )
}
