import React from 'react';
import { motion } from 'framer-motion';
interface GradientBorderCardProps {
  children: ReactNode;
  className?: string;
}
export function GradientBorderCard({
  children,
  className = ''
}: GradientBorderCardProps) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        scale: 0.95
      }}
      animate={{
        opacity: 1,
        scale: 1
      }}
      transition={{
        duration: 0.5
      }}
      className={`gradient-border rounded-2xl ${className}`}>

      <div className="relative z-10 h-full w-full rounded-2xl bg-dark-900/80 backdrop-blur-xl">
        {children}
      </div>
    </motion.div>);

}