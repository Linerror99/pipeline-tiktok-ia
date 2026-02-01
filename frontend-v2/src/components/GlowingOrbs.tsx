import React from 'react';
import { motion } from 'framer-motion';
export function GlowingOrbs() {
  const orbs = [
  {
    size: 300,
    x: '10%',
    y: '20%',
    color: 'rgba(139, 92, 246, 0.4)',
    delay: 0
  },
  {
    size: 400,
    x: '80%',
    y: '60%',
    color: 'rgba(0, 212, 255, 0.3)',
    delay: 2
  },
  {
    size: 250,
    x: '50%',
    y: '80%',
    color: 'rgba(217, 70, 239, 0.35)',
    delay: 4
  },
  {
    size: 200,
    x: '70%',
    y: '10%',
    color: 'rgba(59, 130, 246, 0.3)',
    delay: 1
  },
  {
    size: 350,
    x: '20%',
    y: '70%',
    color: 'rgba(0, 212, 255, 0.25)',
    delay: 3
  }];

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {orbs.map((orb, index) =>
      <motion.div
        key={index}
        className="absolute rounded-full blur-3xl"
        style={{
          width: orb.size,
          height: orb.size,
          left: orb.x,
          top: orb.y,
          background: `radial-gradient(circle, ${orb.color} 0%, transparent 70%)`,
          transform: 'translate(-50%, -50%)'
        }}
        animate={{
          x: [0, 30, -20, 0],
          y: [0, -40, 20, 0],
          scale: [1, 1.1, 0.95, 1]
        }}
        transition={{
          duration: 15 + index * 2,
          repeat: Infinity,
          ease: 'easeInOut',
          delay: orb.delay
        }} />

      )}
    </div>);

}