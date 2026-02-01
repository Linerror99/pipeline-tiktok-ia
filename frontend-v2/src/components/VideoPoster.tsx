import React from 'react';
import { motion } from 'framer-motion';
import { Play, Download, Trash2 } from 'lucide-react';
interface VideoPosterProps {
  id: string;
  title: string;
  duration: string;
  date: string;
  thumbnailUrl: string;
  status: 'completed' | 'processing' | 'failed';
  onPlay?: () => void;
}
export function VideoPoster({
  title,
  duration,
  date,
  thumbnailUrl,
  status,
  onPlay
}: VideoPosterProps) {
  return (
    <motion.div
      className="group relative aspect-[9/16] bg-cinema-dark cursor-pointer overflow-hidden border border-cinema-gray hover:border-cinema-gold transition-colors duration-500"
      whileHover={{
        scale: 1.02
      }}
      transition={{
        duration: 0.4
      }}>

      {/* Image */}
      <img
        src={thumbnailUrl}
        alt={title}
        className="w-full h-full object-cover opacity-70 group-hover:opacity-100 transition-opacity duration-500 grayscale group-hover:grayscale-0" />


      {/* Vignette Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-cinema-black via-transparent to-transparent opacity-90" />

      {/* Status Badge */}
      <div className="absolute top-2 right-2">
        <span
          className={`text-[10px] font-display tracking-widest px-2 py-1 border ${status === 'completed' ? 'border-cinema-gold text-cinema-gold' : status === 'processing' ? 'border-cinema-amber text-cinema-amber animate-pulse' : 'border-cinema-red text-cinema-red'}`}>

          {status === 'processing' ? 'IN PRODUCTION' : status.toUpperCase()}
        </span>
      </div>

      {/* Content */}
      <div className="absolute bottom-0 left-0 w-full p-4 transform translate-y-2 group-hover:translate-y-0 transition-transform duration-500">
        <h3 className="font-display text-xl text-cinema-cream mb-1 truncate">
          {title}
        </h3>
        <div className="flex justify-between items-center text-xs text-gray-400 font-mono mb-4">
          <span>{duration}</span>
          <span>{date}</span>
        </div>

        {/* Actions */}
        <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-500 delay-100">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onPlay?.();
            }}
            className="flex-1 bg-cinema-gold text-cinema-black py-2 font-display tracking-wider hover:bg-white transition-colors flex items-center justify-center">

            <Play size={14} className="mr-1" /> PLAY
          </button>
          <button className="p-2 border border-cinema-gray hover:border-cinema-cream text-cinema-cream transition-colors">
            <Download size={14} />
          </button>
        </div>
      </div>
    </motion.div>);

}