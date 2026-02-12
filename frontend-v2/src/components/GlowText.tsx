import React, { Component } from 'react';
import { motion } from 'framer-motion';
interface GlowTextProps {
  text: string;
  className?: string;
  delay?: number;
  as?: 'h1' | 'h2' | 'h3' | 'p' | 'span';
}
export function GlowText({
  text,
  className = '',
  delay = 0,
  as: Component = 'h1'
}: GlowTextProps) {
  const words = text.split(' ');
  return (
    <Component className={`font-display font-bold ${className}`}>
      {words.map((word, wordIndex) =>
      <span key={wordIndex} className="inline-block mr-[0.25em]">
          {word.split('').map((char, charIndex) =>
        <motion.span
          key={charIndex}
          className="inline-block"
          initial={{
            opacity: 0,
            y: 20,
            filter: 'blur(10px)'
          }}
          animate={{
            opacity: 1,
            y: 0,
            filter: 'blur(0px)'
          }}
          transition={{
            duration: 0.5,
            delay: delay + wordIndex * 0.1 + charIndex * 0.03,
            ease: [0.25, 0.46, 0.45, 0.94]
          }}>

              <motion.span
            className="inline-block"
            animate={{
              textShadow: [
              '0 0 10px rgba(16, 185, 129, 0.5)',
              '0 0 20px rgba(16, 185, 129, 0.8)',
              '0 0 10px rgba(16, 185, 129, 0.5)']

            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: charIndex * 0.1
            }}>

                {char}
              </motion.span>
            </motion.span>
        )}
        </span>
      )}
    </Component>);

}