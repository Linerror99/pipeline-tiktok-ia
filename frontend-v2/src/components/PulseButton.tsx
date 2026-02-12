import React from 'react';
import { motion } from 'framer-motion';
interface PulseButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'secondary';
  className?: string;
  disabled?: boolean;
}
export function PulseButton({
  children,
  onClick,
  size = 'md',
  variant = 'primary',
  className = '',
  disabled = false
}: PulseButtonProps) {
  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  };
  return (
    <motion.button
      onClick={onClick}
      disabled={disabled}
      whileHover={{
        scale: disabled ? 1 : 1.02
      }}
      whileTap={{
        scale: disabled ? 1 : 0.98
      }}
      className={`
        relative overflow-hidden rounded-xl font-display font-semibold
        ${sizes[size]}
        ${variant === 'primary' ? 'bg-gradient-to-r from-emerald-500 via-emerald-400 to-lime-500 text-dark-900' : 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'}
        disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}>

      {/* Pulse rings */}
      {variant === 'primary' && !disabled &&
      <>
          <motion.span
          className="absolute inset-0 rounded-xl bg-emerald-400"
          animate={{
            scale: [1, 1.5],
            opacity: [0.3, 0]
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeOut'
          }} />

          <motion.span
          className="absolute inset-0 rounded-xl bg-emerald-400"
          animate={{
            scale: [1, 1.5],
            opacity: [0.3, 0]
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeOut',
            delay: 0.5
          }} />

        </>
      }

      {/* Shine effect */}
      <motion.span
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full"
        animate={{
          translateX: ['100%', '-100%']
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          repeatDelay: 3
        }} />


      <span className="relative z-10 flex items-center justify-center gap-2">
        {children}
      </span>
    </motion.button>);

}