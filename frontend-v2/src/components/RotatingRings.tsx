import React from 'react';
import { motion } from 'framer-motion';
interface RotatingRingsProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}
export function RotatingRings({
  size = 'lg',
  className = ''
}: RotatingRingsProps) {
  const sizes = {
    sm: {
      outer: 200,
      middle: 150,
      inner: 100
    },
    md: {
      outer: 300,
      middle: 220,
      inner: 140
    },
    lg: {
      outer: 500,
      middle: 380,
      inner: 260
    },
    xl: {
      outer: 700,
      middle: 520,
      inner: 340
    }
  };
  const s = sizes[size];
  return (
    <div
      className={`relative ${className}`}
      style={{
        width: s.outer,
        height: s.outer
      }}>

      {/* Outer Ring */}
      <motion.div
        className="absolute inset-0 rounded-full border-2 border-emerald-500/20"
        style={{
          borderStyle: 'dashed',
          borderWidth: '2px'
        }}
        animate={{
          rotate: 360
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: 'linear'
        }}>

        {/* Glowing dot on outer ring */}
        <motion.div
          className="absolute w-3 h-3 bg-emerald-400 rounded-full shadow-glow"
          style={{
            top: -6,
            left: '50%',
            marginLeft: -6
          }}
          animate={{
            scale: [1, 1.5, 1],
            opacity: [0.8, 1, 0.8]
          }}
          transition={{
            duration: 2,
            repeat: Infinity
          }} />

      </motion.div>

      {/* Middle Ring */}
      <motion.div
        className="absolute rounded-full border border-lime-500/30"
        style={{
          width: s.middle,
          height: s.middle,
          top: (s.outer - s.middle) / 2,
          left: (s.outer - s.middle) / 2
        }}
        animate={{
          rotate: -360
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: 'linear'
        }}>

        {/* Gradient arc */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          <defs>
            <linearGradient id="arcGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0" />
              <stop offset="50%" stopColor="#84cc16" stopOpacity="1" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
            </linearGradient>
          </defs>
          <circle
            cx="50"
            cy="50"
            r="48"
            fill="none"
            stroke="url(#arcGradient)"
            strokeWidth="2"
            strokeDasharray="75 225"
            strokeLinecap="round" />

        </svg>
      </motion.div>

      {/* Inner Ring */}
      <motion.div
        className="absolute rounded-full"
        style={{
          width: s.inner,
          height: s.inner,
          top: (s.outer - s.inner) / 2,
          left: (s.outer - s.inner) / 2,
          background:
          'conic-gradient(from 0deg, transparent, rgba(16, 185, 129, 0.3), transparent)'
        }}
        animate={{
          rotate: 360
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: 'linear'
        }} />


      {/* Center Glow */}
      <div
        className="absolute rounded-full bg-emerald-500/20 blur-3xl"
        style={{
          width: s.inner * 0.6,
          height: s.inner * 0.6,
          top: (s.outer - s.inner * 0.6) / 2,
          left: (s.outer - s.inner * 0.6) / 2
        }} />

    </div>);

}