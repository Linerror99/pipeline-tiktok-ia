import React from 'react';
import { motion } from 'framer-motion';
interface NeonBorderProps {
  children: ReactNode;
  color?: 'cyan' | 'pink' | 'lime';
  className?: string;
}
export function NeonBorder({
  children,
  color = 'cyan',
  className = ''
}: NeonBorderProps) {
  const colors = {
    cyan: '#00ffff',
    pink: '#ff0080',
    lime: '#39ff14'
  };
  const glowColors = {
    cyan: 'shadow-[0_0_20px_rgba(0,255,255,0.15)]',
    pink: 'shadow-[0_0_20px_rgba(255,0,128,0.15)]',
    lime: 'shadow-[0_0_20px_rgba(57,255,20,0.15)]'
  };
  return (
    <div className={`relative p-[2px] overflow-hidden group ${className}`}>
      {/* Background glow */}
      <div
        className={`absolute inset-0 opacity-20 ${glowColors[color]} transition-opacity duration-500 group-hover:opacity-40`} />


      {/* Animated Border SVG */}
      <div className="absolute inset-0 pointer-events-none">
        <svg className="w-full h-full" width="100%" height="100%">
          <defs>
            <linearGradient
              id={`grad-${color}`}
              x1="0%"
              y1="0%"
              x2="100%"
              y2="0%">

              <stop offset="0%" stopColor="transparent" />
              <stop offset="50%" stopColor={colors[color]} />
              <stop offset="100%" stopColor="transparent" />
            </linearGradient>
          </defs>
          <motion.rect
            width="100%"
            height="100%"
            fill="none"
            stroke={`url(#grad-${color})`}
            strokeWidth="2"
            strokeDasharray="200 400"
            initial={{
              strokeDashoffset: 0
            }}
            animate={{
              strokeDashoffset: -1200
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: 'linear'
            }} />

        </svg>
      </div>

      {/* Corner Accents */}
      <div
        className={`absolute top-0 left-0 w-2 h-2 border-t-2 border-l-2 border-${color === 'cyan' ? 'cyber-cyan' : color === 'pink' ? 'cyber-pink' : 'cyber-lime'}`} />

      <div
        className={`absolute top-0 right-0 w-2 h-2 border-t-2 border-r-2 border-${color === 'cyan' ? 'cyber-cyan' : color === 'pink' ? 'cyber-pink' : 'cyber-lime'}`} />

      <div
        className={`absolute bottom-0 left-0 w-2 h-2 border-b-2 border-l-2 border-${color === 'cyan' ? 'cyber-cyan' : color === 'pink' ? 'cyber-pink' : 'cyber-lime'}`} />

      <div
        className={`absolute bottom-0 right-0 w-2 h-2 border-b-2 border-r-2 border-${color === 'cyan' ? 'cyber-cyan' : color === 'pink' ? 'cyber-pink' : 'cyber-lime'}`} />


      {/* Content */}
      <div className="relative z-10 bg-cyber-dark/90 backdrop-blur-sm h-full w-full">
        {children}
      </div>
    </div>);

}