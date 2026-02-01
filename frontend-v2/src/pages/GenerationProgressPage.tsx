import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';
import confetti from 'canvas-confetti';
import { Check, FileText, Film, Layers, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { TiltCard } from '../components/TiltCard';
import { PulseButton } from '../components/PulseButton';
import { RotatingRings } from '../components/RotatingRings';
import { useVideoProgress } from '../hooks/useVideoProgress';

export function GenerationProgressPage() {
  const navigate = useNavigate();
  const { videoId } = useParams<{ videoId: string }>();
  const { status, error, isConnected } = useVideoProgress(videoId || '');

  useEffect(() => {
    if (status?.status === 'completed') {
      // Confetti animation on completion
      const colors = ['#10b981', '#84cc16', '#14b8a6'];
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
        colors
      });
      setTimeout(() => {
        confetti({ particleCount: 50, angle: 60, spread: 55, origin: { x: 0 }, colors });
        confetti({ particleCount: 50, angle: 120, spread: 55, origin: { x: 1 }, colors });
      }, 200);
    }
  }, [status?.status]);

  if (!videoId) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-white/70">Invalid video ID</p>
        </div>
      </div>
    );
  }

  const isComplete = status?.status === 'completed';
  const isFailed = status?.status === 'failed';
  const progress = status?.progress || 0;

  // Map status to steps
  const getSteps = () => {
    const steps = [
      { id: 'script', label: 'Writing Script', icon: FileText, done: false },
      { id: 'video', label: 'Generating Scenes', icon: Film, done: false },
      { id: 'assembly', label: 'Assembling Video', icon: Layers, done: false },
      { id: 'complete', label: 'Final Touches', icon: Sparkles, done: false },
    ];

    const statusValue = status?.status || '';
    
    if (statusValue === 'completed') {
      steps.forEach(s => s.done = true);
    } else if (statusValue === 'processing' && status?.current_step) {
      const step = status.current_step.toLowerCase();
      if (step.includes('script')) {
        steps[0].done = true;
      } else if (step.includes('génération') || step.includes('video')) {
        steps[0].done = true;
        steps[1].done = false;
      } else if (step.includes('assemblage') || step.includes('assembl')) {
        steps[0].done = true;
        steps[1].done = true;
      }
    }

    return steps;
  };

  const steps = getSteps();
  const currentStepIndex = steps.findIndex(s => !s.done);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 max-w-2xl mx-auto relative">
      {/* Background */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-20 pointer-events-none">
        <RotatingRings size="xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full space-y-10 relative z-10">

        {/* Header */}
        <div className="text-center">
          <motion.div
            animate={{ rotate: isComplete ? 0 : 360 }}
            transition={{
              duration: 2,
              repeat: isComplete ? 0 : Infinity,
              ease: 'linear'
            }}
            className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-6">
            {isFailed ? (
              <AlertCircle className="w-10 h-10 text-red-400" />
            ) : isComplete ? (
              <Check className="w-10 h-10 text-emerald-400" />
            ) : (
              <Loader2 className="w-10 h-10 text-emerald-400" />
            )}
          </motion.div>

          <h1 className="font-display text-3xl font-bold text-white mb-2">
            {isFailed ? 'Generation Failed' : isComplete ? 'Video Ready!' : 'Creating Your Video'}
          </h1>
          <p className="text-white/50">
            {isFailed 
              ? 'Something went wrong' 
              : isComplete 
              ? 'Your masterpiece is complete' 
              : status?.current_step || 'This usually takes 2-3 minutes'}
          </p>
          
          {/* Connection Status */}
          <div className="mt-4">
            <span className={`text-xs px-3 py-1 rounded-full ${
              isConnected 
                ? 'bg-emerald-500/10 text-emerald-400' 
                : 'bg-yellow-500/10 text-yellow-400'
            }`}>
              {isConnected ? '● Live Updates' : '○ Polling...'}
            </span>
          </div>
        </div>

        {/* Error Message */}
        {(error || (isFailed && status?.error_message)) && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-red-400 font-medium mb-1">Error</p>
                <p className="text-white/70 text-sm">
                  {error || status?.error_message || 'An unknown error occurred'}
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Progress Card */}
        <TiltCard glowOnHover={false}>
          <div className="p-8">
            {/* Overall Progress */}
            <div className="mb-8">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-white/50">Overall Progress</span>
                <span className="text-emerald-400 font-display font-semibold">
                  {Math.round(progress)}%
                </span>
              </div>
              <div className="h-2 bg-emerald-500/10 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-emerald-500 via-lime-500 to-emerald-500 rounded-full"
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>

            {/* Blocks Progress (if available) */}
            {status?.blocks_completed !== undefined && status?.total_blocks && (
              <div className="mb-8 p-4 bg-emerald-500/5 rounded-xl">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-white/50">Video Blocks</span>
                  <span className="text-lime-400 font-display font-semibold">
                    {status.blocks_completed} / {status.total_blocks}
                  </span>
                </div>
              </div>
            )}

            {/* Steps */}
            <div className="space-y-4">
              {steps.map((step, index) => {
                const isActive = index === currentStepIndex && !isComplete && !isFailed;
                const isCompleted = step.done;
                const Icon = step.icon;

                return (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`flex items-center space-x-4 p-4 rounded-xl transition-all ${
                      isActive ? 'bg-emerald-500/10' : ''
                    }`}>
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                        isCompleted
                          ? 'bg-gradient-to-br from-emerald-400 to-lime-400 text-dark-900'
                          : isActive
                          ? 'bg-emerald-500/20 text-emerald-400 animate-pulse'
                          : 'bg-emerald-500/5 text-white/30'
                      }`}>
                      {isCompleted ? <Check size={18} /> : <Icon size={18} />}
                    </div>

                    <div className="flex-1">
                      <p className={`font-medium ${isActive || isCompleted ? 'text-white' : 'text-white/40'}`}>
                        {step.label}
                      </p>
                    </div>

                    {isCompleted && (
                      <span className="text-xs text-emerald-400 font-medium">Done</span>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
        </TiltCard>

        {/* Action Buttons */}
        <AnimatePresence>
          {isComplete && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center gap-4">
              <PulseButton size="lg" onClick={() => navigate(`/video/${videoId}`)}>
                View Your Video
              </PulseButton>
            </motion.div>
          )}
          
          {isFailed && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-center gap-4">
              <PulseButton size="lg" onClick={() => navigate('/create')} variant="secondary">
                Try Again
              </PulseButton>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}