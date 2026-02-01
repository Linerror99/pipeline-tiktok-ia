import React from 'react';
import { motion } from 'framer-motion';
import { Play, Download, MoreHorizontal } from 'lucide-react';
interface VideoCardProps {
  id: string;
  title: string;
  duration: string;
  date: string;
  thumbnailUrl: string;
  status: 'completed' | 'processing' | 'failed';
  onPlay?: () => void;
  delay?: number;
}
export function VideoCard({
  title,
  duration,
  date,
  thumbnailUrl,
  status,
  onPlay,
  delay = 0
}: VideoCardProps) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 20
      }}
      animate={{
        opacity: 1,
        y: 0
      }}
      transition={{
        duration: 0.5,
        delay
      }}
      whileHover={{
        y: -4
      }}
      className="group relative">

      <div className="glass rounded-2xl overflow-hidden transition-all duration-500 hover:shadow-glow-violet">
        {/* Thumbnail */}
        <div className="relative aspect-[9/16] overflow-hidden">
          <img
            src={thumbnailUrl}
            alt={title}
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />


          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-dark-900 via-transparent to-transparent opacity-80" />

          {/* Status Badge */}
          <div className="absolute top-3 right-3">
            <span
              className={`
              px-3 py-1 rounded-full text-xs font-medium backdrop-blur-md
              ${status === 'completed' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : status === 'processing' ? 'bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/30 animate-pulse' : 'bg-red-500/20 text-red-400 border border-red-500/30'}
            `}>

              {status === 'processing' ? 'Processing...' : status}
            </span>
          </div>

          {/* Play Button Overlay */}
          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <motion.button
              onClick={onPlay}
              whileHover={{
                scale: 1.1
              }}
              whileTap={{
                scale: 0.95
              }}
              className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/30">

              <Play className="w-6 h-6 text-white ml-1" fill="white" />
            </motion.button>
          </div>
        </div>

        {/* Info */}
        <div className="p-4">
          <h3 className="font-display font-semibold text-white truncate mb-2">
            {title}
          </h3>
          <div className="flex items-center justify-between text-sm text-white/40">
            <span>{duration}</span>
            <span>{date}</span>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-2 mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            <button className="flex-1 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 hover:text-white text-sm font-medium transition-all flex items-center justify-center space-x-2">
              <Download size={14} />
              <span>Download</span>
            </button>
            <button className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-white/70 hover:text-white transition-all">
              <MoreHorizontal size={18} />
            </button>
          </div>
        </div>
      </div>
    </motion.div>);

}