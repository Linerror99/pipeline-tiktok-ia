import React, { Component } from 'react';
import { motion } from 'framer-motion';
interface CinematicTextProps {
  text: string;
  as?: 'h1' | 'h2' | 'h3' | 'p' | 'span';
  className?: string;
  variant?: 'gold' | 'cream' | 'red';
}
export function CinematicText({
  text,
  as: Component = 'h1',
  className = '',
  variant = 'gold'
}: CinematicTextProps) {
  const colors = {
    gold: 'text-cinema-gold',
    cream: 'text-cinema-cream',
    red: 'text-cinema-red'
  };
  return (
    <Component
      className={`font-display tracking-widest uppercase ${colors[variant]} ${className}`}>

      {text.split('').map((char, index) =>
      <motion.span
        key={index}
        initial={{
          opacity: 0,
          filter: 'blur(10px)'
        }}
        animate={{
          opacity: 1,
          filter: 'blur(0px)'
        }}
        transition={{
          duration: 0.8,
          delay: index * 0.05,
          ease: 'easeOut'
        }}
        className="inline-block">

          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      )}
    </Component>);

}