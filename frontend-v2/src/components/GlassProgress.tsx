import React from 'react';
import { motion } from 'framer-motion';
interface GlassProgressProps {
  progress: number;
  label?: string;
  showPercentage?: boolean;
}
export function GlassProgress({
  progress,
  label,
  showPercentage = true
}: GlassProgressProps) {
  return (
    <div className="space-y-3">
      {(label || showPercentage) &&
      <div className="flex justify-between items-center text-sm">
          {label && <span className="text-white/60">{label}</span>}
          {showPercentage &&
        <span className="text-accent-cyan font-display font-semibold">
              {Math.round(progress)}%
            </span>
        }
        </div>
      }

      <div className="relative h-2 bg-white/5 rounded-full overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 bg-gradient-to-r from-accent-cyan/10 via-accent-violet/10 to-accent-magenta/10" />

        {/* Progress fill */}
        <motion.div
          className="absolute inset-y-0 left-0 bg-gradient-to-r from-accent-cyan via-accent-violet to-accent-magenta rounded-full"
          initial={{
            width: 0
          }}
          animate={{
            width: `${progress}%`
          }}
          transition={{
            type: 'spring',
            stiffness: 50,
            damping: 20
          }} />


        {/* Glow effect at the end */}
        <motion.div
          className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-accent-cyan rounded-full blur-md"
          animate={{
            left: `${progress}%`
          }}
          transition={{
            type: 'spring',
            stiffness: 50,
            damping: 20
          }}
          style={{
            marginLeft: '-8px'
          }} />

      </div>
    </div>);

}