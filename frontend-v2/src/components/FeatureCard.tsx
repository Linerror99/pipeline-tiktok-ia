import React from 'react';
import { motion } from 'framer-motion';
import { TiltCard } from './TiltCard';
import { BoxIcon } from 'lucide-react';
interface FeatureCardProps {
  icon: BoxIcon;
  title: string;
  description: string;
  delay?: number;
}
export function FeatureCard({
  icon: Icon,
  title,
  description,
  delay = 0
}: FeatureCardProps) {
  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 30
      }}
      whileInView={{
        opacity: 1,
        y: 0
      }}
      viewport={{
        once: true
      }}
      transition={{
        duration: 0.6,
        delay
      }}>

      <TiltCard className="h-full">
        <div className="p-8">
          <motion.div
            className="w-14 h-14 rounded-xl bg-gradient-to-br from-emerald-500/20 to-lime-500/20 flex items-center justify-center mb-6 border border-emerald-500/20"
            whileHover={{
              rotate: [0, -10, 10, 0],
              scale: 1.1
            }}
            transition={{
              duration: 0.5
            }}>

            <Icon className="w-7 h-7 text-emerald-400" />
          </motion.div>

          <h3 className="font-display text-xl font-semibold text-white mb-3">
            {title}
          </h3>
          <p className="text-white/60 leading-relaxed">{description}</p>
        </div>
      </TiltCard>
    </motion.div>);

}