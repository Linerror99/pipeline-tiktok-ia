import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NeonBorder } from './NeonBorder';
import { TerminalInput } from './TerminalInput';
import { ProgressScanner } from './ProgressScanner';
import { SparklesIcon, SettingsIcon, CpuIcon } from 'lucide-react';
interface GenerationPanelProps {
  onGenerate: (prompt: string) => void;
  isGenerating: boolean;
  progress: number;
}
export function GenerationPanel({
  onGenerate,
  isGenerating,
  progress
}: GenerationPanelProps) {
  const [activeTab, setActiveTab] = useState<'text' | 'image'>('text');
  return (
    <div className="w-full max-w-3xl mx-auto mb-16">
      <NeonBorder
        color={isGenerating ? 'pink' : 'cyan'}
        className="bg-cyber-dark/80">

        <div className="p-6 md:p-8 space-y-6">
          {/* Header */}
          <div className="flex justify-between items-center border-b border-cyber-gray pb-4">
            <div className="flex space-x-4">
              <button
                onClick={() => setActiveTab('text')}
                className={`flex items-center space-x-2 text-sm font-mono uppercase tracking-wider transition-colors ${activeTab === 'text' ? 'text-cyber-cyan' : 'text-gray-500 hover:text-gray-300'}`}>

                <SparklesIcon size={16} />
                <span>Text-to-Video</span>
              </button>
              <button
                onClick={() => setActiveTab('image')}
                className={`flex items-center space-x-2 text-sm font-mono uppercase tracking-wider transition-colors ${activeTab === 'image' ? 'text-cyber-pink' : 'text-gray-500 hover:text-gray-300'}`}>

                <CpuIcon size={16} />
                <span>Image-to-Video</span>
              </button>
            </div>
            <button className="text-cyber-gray hover:text-cyber-lime transition-colors">
              <SettingsIcon size={18} />
            </button>
          </div>

          {/* Input Area */}
          <div className="space-y-4">
            <TerminalInput onSubmit={onGenerate} isGenerating={isGenerating} />

            {/* Settings Tags */}
            <div className="flex flex-wrap gap-2 text-xs font-mono">
              <span className="px-2 py-1 border border-cyber-gray text-gray-400 rounded-sm">
                Model: V4.2-NEON
              </span>
              <span className="px-2 py-1 border border-cyber-gray text-gray-400 rounded-sm">
                Ratio: 16:9
              </span>
              <span className="px-2 py-1 border border-cyber-gray text-gray-400 rounded-sm">
                Steps: 50
              </span>
            </div>
          </div>

          {/* Progress Area */}
          <AnimatePresence>
            {isGenerating &&
            <motion.div
              initial={{
                opacity: 0,
                height: 0
              }}
              animate={{
                opacity: 1,
                height: 'auto'
              }}
              exit={{
                opacity: 0,
                height: 0
              }}
              className="overflow-hidden">

                <div className="pt-4 border-t border-cyber-gray border-dashed">
                  <ProgressScanner
                  progress={progress}
                  status="INITIALIZING NEURAL NETWORKS..." />

                </div>
              </motion.div>
            }
          </AnimatePresence>
        </div>
      </NeonBorder>
    </div>);

}