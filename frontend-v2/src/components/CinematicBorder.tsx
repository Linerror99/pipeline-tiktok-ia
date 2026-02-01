import React from 'react';
import { motion } from 'framer-motion';
interface CinematicBorderProps {
  children: ReactNode;
  className?: string;
  animate?: boolean;
}
export function CinematicBorder({
  children,
  className = '',
  animate = true
}: CinematicBorderProps) {
  return (
    <div className={`relative p-[1px] group ${className}`}>
      {/* Golden Border Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-cinema-gold/40 via-transparent to-cinema-gold/40 opacity-50 group-hover:opacity-100 transition-opacity duration-700" />

      {/* Corner Accents */}
      <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cinema-gold" />
      <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-cinema-gold" />
      <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-cinema-gold" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cinema-gold" />

      {/* Animated Glow Line */}
      {animate &&
      <motion.div
        className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cinema-gold to-transparent opacity-50"
        animate={{
          x: ['-100%', '100%'],
          opacity: [0, 0.5, 0]
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'easeInOut',
          repeatDelay: 2
        }} />

      }

      {/* Content Container */}
      <div className="relative h-full w-full bg-cinema-dark/90 backdrop-blur-sm border border-white/5">
        {children}
      </div>
    </div>);

}