import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, Info } from 'lucide-react';
export type ToastType = 'success' | 'error' | 'info';
interface ToastProps {
  message: string;
  type: ToastType;
  isVisible: boolean;
  onClose: () => void;
}
export function Toast({ message, type, isVisible, onClose }: ToastProps) {
  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(onClose, 3000);
      return () => clearTimeout(timer);
    }
  }, [isVisible, onClose]);
  const icons = {
    success: <CheckCircle className="text-cinema-gold" size={20} />,
    error: <AlertCircle className="text-cinema-red" size={20} />,
    info: <Info className="text-cinema-cream" size={20} />
  };
  return (
    <AnimatePresence>
      {isVisible &&
      <motion.div
        initial={{
          opacity: 0,
          y: 50
        }}
        animate={{
          opacity: 1,
          y: 0
        }}
        exit={{
          opacity: 0,
          y: 20
        }}
        className="fixed bottom-8 right-8 z-50">

          <div className="bg-cinema-black border border-cinema-gold/30 px-6 py-4 flex items-center space-x-4 shadow-2xl min-w-[300px]">
            {icons[type]}
            <span className="font-display tracking-wide text-cinema-cream">
              {message}
            </span>

            {/* Progress bar */}
            <motion.div
            className="absolute bottom-0 left-0 h-[2px] bg-cinema-gold"
            initial={{
              width: '100%'
            }}
            animate={{
              width: '0%'
            }}
            transition={{
              duration: 3,
              ease: 'linear'
            }} />

          </div>
        </motion.div>
      }
    </AnimatePresence>);

}