import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Clock,
  Palette,
  Languages,
  Wand2,
  Rocket,
  AlertCircle } from
'lucide-react';
import { TiltCard } from '../components/TiltCard';
import { PulseButton } from '../components/PulseButton';
import { RotatingRings } from '../components/RotatingRings';
import { apiService } from '../services/api';

export function CreateVideoPage() {
  const navigate = useNavigate();
  const [theme, setTheme] = useState('');
  const [duration, setDuration] = useState(36);
  const [style, setStyle] = useState('informative');
  const [language, setLanguage] = useState('fr');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!theme.trim()) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const result = await apiService.createVideo({
        theme: theme.trim(),
        target_duration: duration,
        style,
        language
      });

      // Redirect to progress page with video ID
      navigate(`/progress/${result.video_id}`);
    } catch (err: any) {
      console.error('Error creating video:', err);
      setError(err.response?.data?.detail || 'Failed to create video. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  const durations = [
    { value: 15, label: '15s' },
    { value: 29, label: '30s' },
    { value: 50, label: '50s' },
    { value: 64, label: '60s' }
  ];
  
  const styles = [
  {
    value: 'informative',
    label: 'Informative',
    emoji: '📚'
  },
  {
    value: 'humorous',
    label: 'Humorous',
    emoji: '😄'
  },
  {
    value: 'dramatic',
    label: 'Dramatic',
    emoji: '🎭'
  },
  {
    value: 'inspiring',
    label: 'Inspiring',
    emoji: '✨'
  }];

  return (
    <div className="p-6 md:p-10 max-w-4xl mx-auto min-h-screen flex flex-col justify-center relative">
      {/* Background Rings */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-20 pointer-events-none">
        <RotatingRings size="lg" />
      </div>

      <motion.div
        initial={{
          opacity: 0,
          y: 20
        }}
        animate={{
          opacity: 1,
          y: 0
        }}
        className="text-center mb-10 relative z-10">

        <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-6">
          <Sparkles className="w-4 h-4 text-emerald-400" />
          <span className="text-sm text-emerald-400">
            AI-Powered Generation
          </span>
        </div>
        <h1 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">
          Create Your Video
        </h1>
        <p className="text-white/50 max-w-md mx-auto">
          Describe your idea and let AI transform it into a stunning TikTok
          video
        </p>
      </motion.div>

      <TiltCard glowOnHover={false} className="relative z-10">
        <div className="rotating-border rounded-2xl">
          <div className="relative z-10 bg-dark-800/90 rounded-2xl p-8 md:p-10 space-y-8">
            {/* Theme Input */}
            <div className="space-y-3">
              <label className="flex items-center text-sm text-emerald-400">
                <Wand2 className="w-4 h-4 mr-2" />
                What's your video about?
              </label>
              <textarea
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
                placeholder="e.g., The benefits of morning meditation for productivity..."
                rows={3}
                disabled={isLoading}
                className="w-full bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4 text-white placeholder-white/30 resize-none focus:border-emerald-500/50 focus:shadow-glow-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed" />

            </div>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </motion.div>
            )}

            {/* Duration */}
            <div className="space-y-4">
              <label className="flex items-center text-sm text-lime-400">
                <Clock className="w-4 h-4 mr-2" />
                Duration (8-78 seconds)
              </label>
              <div className="flex gap-3">
                {durations.map((d) =>
                <button
                  key={d.value}
                  onClick={() => setDuration(d.value)}
                  disabled={isLoading}
                  className={`flex-1 py-3 rounded-xl font-display font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed ${duration === d.value ? 'bg-gradient-to-r from-emerald-500 to-lime-500 text-dark-900 shadow-glow' : 'bg-emerald-500/10 text-white/50 hover:bg-emerald-500/20 hover:text-white'}`}>

                    {d.label}
                  </button>
                )}
              </div>
            </div>

            {/* Style */}
            <div className="space-y-4">
              <label className="flex items-center text-sm text-emerald-400">
                <Palette className="w-4 h-4 mr-2" />
                Style
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {styles.map((s) =>
                <button
                  key={s.value}
                  onClick={() => setStyle(s.value)}
                  disabled={isLoading}
                  className={`py-4 rounded-xl transition-all flex flex-col items-center space-y-2 disabled:opacity-50 disabled:cursor-not-allowed ${style === s.value ? 'bg-emerald-500/20 border border-emerald-500/50 text-white' : 'bg-emerald-500/5 border border-transparent text-white/50 hover:bg-emerald-500/10 hover:text-white'}`}>

                    <span className="text-2xl">{s.emoji}</span>
                    <span className="text-sm font-medium">{s.label}</span>
                  </button>
                )}
              </div>
            </div>

            {/* Language */}
            <div className="space-y-3">
              <label className="flex items-center text-sm text-lime-400">
                <Languages className="w-4 h-4 mr-2" />
                Language
              </label>
              <select 
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                disabled={isLoading}
                className="w-full bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4 text-white focus:border-emerald-500/50 transition-all appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
                <option value="fr">🇫🇷 Français</option>
                <option value="en">🇬🇧 English</option>
                <option value="es">🇪🇸 Español</option>
              </select>
            </div>

            {/* Generate Button */}
            <div className="pt-4">
              <PulseButton
                fullWidth
                size="lg"
                onClick={handleGenerate}
                disabled={!theme.trim() || isLoading}>

                <Rocket className="w-5 h-5" />
                {isLoading ? 'Creating...' : 'Generate Video'}
              </PulseButton>
            </div>
          </div>
        </div>
      </TiltCard>
    </div>);

}