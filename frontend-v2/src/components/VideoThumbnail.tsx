import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { PlayIcon, DownloadIcon, Share2Icon } from 'lucide-react';
interface VideoThumbnailProps {
  id: string;
  title: string;
  duration: string;
  thumbnailUrl: string;
  status: 'ready' | 'processing' | 'failed';
  delay: number;
}
export function VideoThumbnail({
  title,
  duration,
  thumbnailUrl,
  status,
  delay
}: VideoThumbnailProps) {
  const [isHovered, setIsHovered] = useState(false);
  return (
    <motion.div
      initial={{
        opacity: 0,
        scale: 0.9,
        y: 20
      }}
      animate={{
        opacity: 1,
        scale: 1,
        y: 0
      }}
      transition={{
        delay,
        duration: 0.4
      }}
      className="relative group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}>

      {/* Card Container */}
      <div className="relative bg-cyber-dark border border-cyber-gray overflow-hidden aspect-video transition-all duration-300 group-hover:border-cyber-pink group-hover:shadow-[0_0_15px_rgba(255,0,128,0.3)]">
        {/* Image / Placeholder */}
        <div className="absolute inset-0 bg-cyber-black">
          {status === 'processing' ?
          <div className="w-full h-full flex flex-col items-center justify-center space-y-2">
              <div className="w-8 h-8 border-2 border-cyber-cyan border-t-transparent rounded-full animate-spin" />
              <span className="text-xs text-cyber-cyan font-mono animate-pulse">
                RENDERING...
              </span>
            </div> :

          <img
            src={thumbnailUrl}
            alt={title}
            className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity duration-300" />

          }
        </div>

        {/* Overlay UI */}
        <div className="absolute inset-0 bg-gradient-to-t from-cyber-black/90 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
          <div className="transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300">
            <h3 className="text-white font-display text-sm tracking-wide mb-1 truncate">
              {title}
            </h3>
            <div className="flex items-center justify-between">
              <span className="text-cyber-cyan font-mono text-xs">
                {duration}
              </span>
              <div className="flex space-x-2">
                <button className="p-1.5 hover:bg-cyber-cyan hover:text-cyber-black rounded-sm transition-colors text-white">
                  <PlayIcon size={14} />
                </button>
                <button className="p-1.5 hover:bg-cyber-pink hover:text-cyber-black rounded-sm transition-colors text-white">
                  <DownloadIcon size={14} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Corner Decorations */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-cyber-cyan opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-cyber-pink opacity-0 group-hover:opacity-100 transition-opacity" />

        {/* Scanline on hover */}
        {isHovered && status === 'ready' &&
        <motion.div
          className="absolute inset-0 bg-white/5 pointer-events-none"
          initial={{
            top: '-100%'
          }}
          animate={{
            top: '100%'
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            ease: 'linear'
          }}
          style={{
            height: '20%'
          }} />

        }
      </div>
    </motion.div>);

}