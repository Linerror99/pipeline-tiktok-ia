import React from 'react';
import { motion } from 'framer-motion';
import { GlassCard } from './GlassCard';
import { BoxIcon } from 'lucide-react';
interface StatsCardProps {
  label: string;
  value: string;
  icon: BoxIcon;
  trend?: string;
  color?: 'cyan' | 'violet' | 'magenta';
  delay?: number;
}
export function StatsCard({
  label,
  value,
  icon: Icon,
  trend,
  color = 'cyan',
  delay = 0
}: StatsCardProps) {
  const colors = {
    cyan: 'from-accent-cyan/20 to-accent-cyan/5 text-accent-cyan',
    violet: 'from-accent-violet/20 to-accent-violet/5 text-accent-violet',
    magenta: 'from-accent-magenta/20 to-accent-magenta/5 text-accent-magenta'
  };
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
      }}>

      <GlassCard glow={color} className="p-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-white/50 mb-1">{label}</p>
            <h3 className="text-3xl font-display font-bold text-white">
              {value}
            </h3>
            {trend &&
            <p className={`text-xs mt-2 ${colors[color].split(' ')[1]}`}>
                {trend}
              </p>
            }
          </div>
          <div className={`p-3 rounded-xl bg-gradient-to-br ${colors[color]}`}>
            <Icon size={24} />
          </div>
        </div>
      </GlassCard>
    </motion.div>);

}