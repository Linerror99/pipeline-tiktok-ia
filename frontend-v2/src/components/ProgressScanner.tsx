import React from 'react';
import { motion } from 'framer-motion';
interface ProgressScannerProps {
  progress: number;
  status: string;
}
export function ProgressScanner({ progress, status }: ProgressScannerProps) {
  return (
    <div className="w-full space-y-2 font-mono">
      <div className="flex justify-between text-xs uppercase tracking-wider text-cyber-cyan/80">
        <span>Status: {status}</span>
        <span>{Math.round(progress)}%</span>
      </div>

      <div className="relative h-6 bg-cyber-black border border-cyber-gray overflow-hidden">
        {/* Grid background inside bar */}
        <div className="absolute inset-0 opacity-20 bg-[linear-gradient(90deg,transparent_50%,rgba(0,255,255,0.1)_50%)] bg-[length:4px_100%]" />

        {/* Fill */}
        <motion.div
          className="h-full bg-cyber-cyan/20"
          initial={{
            width: 0
          }}
          animate={{
            width: `${progress}%`
          }}
          transition={{
            type: 'spring',
            stiffness: 50
          }} />


        {/* Scanning Line */}
        <motion.div
          className="absolute top-0 bottom-0 w-[2px] bg-cyber-cyan shadow-[0_0_10px_#00ffff]"
          animate={{
            left: ['0%', '100%']
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'linear'
          }} />


        {/* Random data noise */}
        <div className="absolute top-1 right-2 text-[10px] text-cyber-lime opacity-50">
          {progress < 100 ?
          `HEX:${Math.random().toString(16).slice(2, 8).toUpperCase()}` :
          'COMPLETE'}
        </div>
      </div>
    </div>);

}