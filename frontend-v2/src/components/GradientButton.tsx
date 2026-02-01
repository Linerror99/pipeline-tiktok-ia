import React from 'react';
import { motion } from 'framer-motion';
interface GradientButtonProps {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  fullWidth?: boolean;
}
export function GradientButton({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  size = 'md',
  className = '',
  fullWidth = false
}: GradientButtonProps) {
  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  };
  const variants = {
    primary: `
      bg-gradient-to-r from-accent-cyan via-accent-violet to-accent-magenta
      text-white font-semibold
      hover:shadow-glow-cyan
    `,
    secondary: `
      bg-white/5 border border-white/10
      text-white
      hover:bg-white/10 hover:border-white/20
    `,
    ghost: `
      bg-transparent
      text-white/70
      hover:text-white hover:bg-white/5
    `
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
        ${sizes[size]}
        ${variants[variant]}
        ${fullWidth ? 'w-full' : ''}
        rounded-xl font-display tracking-wide
        transition-all duration-300
        disabled:opacity-50 disabled:cursor-not-allowed
        relative overflow-hidden
        ${className}
      `}>

      {/* Shine effect */}
      {variant === 'primary' &&
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full"
        animate={{
          translateX: ['100%', '-100%']
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          repeatDelay: 3
        }} />

      }
      <span className="relative z-10">{children}</span>
    </motion.button>);

}