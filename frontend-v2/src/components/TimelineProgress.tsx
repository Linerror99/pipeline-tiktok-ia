import React from 'react';
import { motion } from 'framer-motion';
interface TimelineProgressProps {
  progress: number;
  label?: string;
}
export function TimelineProgress({ progress, label }: TimelineProgressProps) {
  return (
    <div className="w-full space-y-2">
      {label &&
      <div className="flex justify-between text-xs font-display tracking-widest text-cinema-gold/80">
          <span>{label}</span>
          <span>{Math.round(progress)}%</span>
        </div>
      }

      <div className="relative h-8 bg-cinema-black border-y border-cinema-gray flex items-center overflow-hidden">
        {/* Film Perforations Top */}
        <div className="absolute top-0 left-0 w-full h-[4px] flex justify-between px-1">
          {Array.from({
            length: 20
          }).map((_, i) =>
          <div
            key={`top-${i}`}
            className="w-[3px] h-[3px] bg-cinema-gray/50 rounded-full" />

          )}
        </div>

        {/* Progress Fill */}
        <motion.div
          className="h-2 bg-gradient-to-r from-cinema-amber to-cinema-gold w-full absolute top-1/2 -translate-y-1/2"
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


        {/* Playhead */}
        <motion.div
          className="absolute top-0 bottom-0 w-[2px] bg-cinema-red shadow-[0_0_10px_rgba(139,0,0,0.8)] z-10"
          animate={{
            left: `${progress}%`
          }}
          transition={{
            type: 'spring',
            stiffness: 50,
            damping: 20
          }} />


        {/* Film Perforations Bottom */}
        <div className="absolute bottom-0 left-0 w-full h-[4px] flex justify-between px-1">
          {Array.from({
            length: 20
          }).map((_, i) =>
          <div
            key={`bottom-${i}`}
            className="w-[3px] h-[3px] bg-cinema-gray/50 rounded-full" />

          )}
        </div>
      </div>
    </div>);

}