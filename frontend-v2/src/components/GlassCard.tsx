import React from 'react';
import { motion } from 'framer-motion';
interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  glow?: 'cyan' | 'violet' | 'magenta' | 'none';
  animate?: boolean;
}
export function GlassCard({
  children,
  className = '',
  hover = true,
  glow = 'none',
  animate = true
}: GlassCardProps) {
  const glowStyles = {
    cyan: 'hover:shadow-glow-cyan',
    violet: 'hover:shadow-glow-violet',
    magenta: 'hover:shadow-glow-magenta',
    none: ''
  };
  const content =
  <div
    className={`
        glass rounded-2xl overflow-hidden
        ${hover ? 'transition-all duration-500 hover:bg-glass-hover hover:border-white/10 hover:-translate-y-1' : ''}
        ${glowStyles[glow]}
        ${className}
      `}>

      {children}
    </div>;

  if (!animate) return content;
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 20
      }}
      animate={{
        opacity: 1,
        y: 0
      }}
      transition={{
        duration: 0.5
      }}>

      {content}
    </motion.div>);

}