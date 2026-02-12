import React, { useEffect, useState, Component } from 'react';
import { motion } from 'framer-motion';
interface GlitchTextProps {
  text: string;
  as?: 'h1' | 'h2' | 'h3' | 'p' | 'span';
  className?: string;
  color?: 'cyan' | 'pink' | 'lime' | 'white';
}
export function GlitchText({
  text,
  as: Component = 'h1',
  className = '',
  color = 'cyan'
}: GlitchTextProps) {
  const [isGlitching, setIsGlitching] = useState(false);
  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.85) {
        setIsGlitching(true);
        setTimeout(() => setIsGlitching(false), 200);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);
  const colorMap = {
    cyan: 'text-cyber-cyan shadow-[0_0_10px_rgba(0,255,255,0.5)]',
    pink: 'text-cyber-pink shadow-[0_0_10px_rgba(255,0,128,0.5)]',
    lime: 'text-cyber-lime shadow-[0_0_10px_rgba(57,255,20,0.5)]',
    white: 'text-white shadow-[0_0_10px_rgba(255,255,255,0.5)]'
  };
  return (
    <div className="relative inline-block">
      <Component
        className={`relative z-10 font-display font-bold uppercase tracking-widest ${colorMap[color]} ${className}`}>

        {text}
      </Component>

      {isGlitching &&
      <>
          <motion.span
          className={`absolute top-0 left-0 -z-10 opacity-70 text-cyber-pink overflow-hidden w-full h-full font-display font-bold uppercase tracking-widest ${className}`}
          initial={{
            x: 0
          }}
          animate={{
            x: [-2, 2, -1, 0]
          }}
          transition={{
            duration: 0.2
          }}
          style={{
            clipPath: 'polygon(0 0, 100% 0, 100% 45%, 0 45%)',
            transform: 'translate(-2px)'
          }}>

            {text}
          </motion.span>
          <motion.span
          className={`absolute top-0 left-0 -z-10 opacity-70 text-cyber-cyan overflow-hidden w-full h-full font-display font-bold uppercase tracking-widest ${className}`}
          initial={{
            x: 0
          }}
          animate={{
            x: [2, -2, 1, 0]
          }}
          transition={{
            duration: 0.2
          }}
          style={{
            clipPath: 'polygon(0 80%, 100% 20%, 100% 100%, 0 100%)',
            transform: 'translate(2px)'
          }}>

            {text}
          </motion.span>
        </>
      }
    </div>);

}