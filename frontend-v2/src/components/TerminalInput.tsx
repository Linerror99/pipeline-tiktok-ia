import React, { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { SendIcon } from 'lucide-react';
interface TerminalInputProps {
  onSubmit: (value: string) => void;
  isGenerating: boolean;
}
export function TerminalInput({ onSubmit, isGenerating }: TerminalInputProps) {
  const [value, setValue] = useState('');
  const [placeholder, setPlaceholder] = useState('');
  const fullPlaceholder = 'Describe your vision sequence...';
  const inputRef = useRef<HTMLInputElement>(null);
  // Typing effect for placeholder
  useEffect(() => {
    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex <= fullPlaceholder.length) {
        setPlaceholder(fullPlaceholder.slice(0, currentIndex));
        currentIndex++;
      } else {
        clearInterval(interval);
      }
    }, 50);
    return () => clearInterval(interval);
  }, []);
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim() && !isGenerating) {
      onSubmit(value);
      setValue('');
    }
  };
  return (
    <form onSubmit={handleSubmit} className="relative w-full group">
      <div className="flex items-center bg-cyber-black border border-cyber-gray focus-within:border-cyber-cyan transition-colors duration-300 p-4">
        <span className="text-cyber-lime font-mono mr-3 select-none flex items-center">
          PROMPT://<span className="animate-pulse ml-1">_</span>
        </span>

        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder}
          disabled={isGenerating}
          className="flex-1 bg-transparent border-none outline-none text-cyber-cyan font-mono placeholder-cyber-gray/50 focus:ring-0"
          autoComplete="off" />


        <button
          type="submit"
          disabled={!value.trim() || isGenerating}
          className="ml-2 p-2 text-cyber-gray hover:text-cyber-cyan disabled:opacity-50 disabled:hover:text-cyber-gray transition-colors">

          <SendIcon className="w-5 h-5" />
        </button>
      </div>

      {/* Decorative bottom lines */}
      <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyber-cyan to-transparent opacity-0 group-focus-within:opacity-50 transition-opacity" />
    </form>);

}