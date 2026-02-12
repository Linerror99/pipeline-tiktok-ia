import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
interface TiltCardProps {
  children: React.ReactNode;
  className?: string;
  glowOnHover?: boolean;
}
export function TiltCard({
  children,
  className = '',
  glowOnHover = true
}: TiltCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const mouseX = e.clientX - centerX;
    const mouseY = e.clientY - centerY;
    const rotateXValue = mouseY / (rect.height / 2) * -10;
    const rotateYValue = mouseX / (rect.width / 2) * 10;
    setRotateX(rotateXValue);
    setRotateY(rotateYValue);
  };
  const handleMouseLeave = () => {
    setRotateX(0);
    setRotateY(0);
    setIsHovered(false);
  };
  return (
    <div className="perspective-1000">
      <motion.div
        ref={cardRef}
        className={`preserve-3d relative ${className}`}
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={handleMouseLeave}
        animate={{
          rotateX,
          rotateY,
          scale: isHovered ? 1.02 : 1
        }}
        transition={{
          type: 'spring',
          stiffness: 300,
          damping: 20
        }}
        style={{
          transformStyle: 'preserve-3d'
        }}>

        {/* Glow effect */}
        {glowOnHover &&
        <motion.div
          className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-emerald-500/20 via-lime-500/20 to-emerald-500/20 blur-xl"
          animate={{
            opacity: isHovered ? 1 : 0
          }}
          transition={{
            duration: 0.3
          }} />

        }

        {/* Card content */}
        <div className="relative glass-green rounded-2xl overflow-hidden">
          {children}
        </div>
      </motion.div>
    </div>);

}