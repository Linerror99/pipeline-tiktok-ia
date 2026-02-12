import React from 'react';
import { motion } from 'framer-motion';
import { BoxIcon } from 'lucide-react';
interface GlassInputProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  icon?: BoxIcon;
  type?: 'text' | 'email' | 'password';
}
export function GlassInput({
  label,
  placeholder,
  value,
  onChange,
  icon: Icon,
  type = 'text'
}: GlassInputProps) {
  return (
    <div className="space-y-2">
      {label &&
      <label className="text-sm text-white/60 font-medium tracking-wide">
          {label}
        </label>
      }
      <div className="relative group">
        {Icon &&
        <Icon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/30 group-focus-within:text-accent-cyan transition-colors" />
        }
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className={`
            w-full bg-white/5 border border-white/10 rounded-xl py-4 text-white placeholder-white/30
            transition-all duration-300
            focus:bg-white/8 focus:border-accent-cyan/50
            ${Icon ? 'pl-12 pr-4' : 'px-4'}
          `} />

        {/* Focus glow effect */}
        <div className="absolute inset-0 rounded-xl opacity-0 group-focus-within:opacity-100 transition-opacity duration-300 pointer-events-none">
          <div className="absolute inset-0 rounded-xl bg-accent-cyan/5 blur-xl" />
        </div>
      </div>
    </div>);

}