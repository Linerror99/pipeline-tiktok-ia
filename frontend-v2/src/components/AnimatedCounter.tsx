import React, { useEffect, useState } from 'react';
import { motion, useSpring, useTransform } from 'framer-motion';
interface AnimatedCounterProps {
  value: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
}
export function AnimatedCounter({
  value,
  duration = 2,
  prefix = '',
  suffix = '',
  className = ''
}: AnimatedCounterProps) {
  const spring = useSpring(0, {
    duration: duration * 1000
  });
  const display = useTransform(spring, (current) => Math.floor(current));
  const [displayValue, setDisplayValue] = useState(0);
  useEffect(() => {
    spring.set(value);
  }, [spring, value]);
  useEffect(() => {
    return display.on('change', (latest) => {
      setDisplayValue(latest);
    });
  }, [display]);
  return (
    <motion.span
      className={`font-display font-bold tabular-nums ${className}`}
      initial={{
        opacity: 0,
        scale: 0.5
      }}
      animate={{
        opacity: 1,
        scale: 1
      }}
      transition={{
        duration: 0.5
      }}>

      {prefix}
      {displayValue.toLocaleString()}
      {suffix}
    </motion.span>);

}