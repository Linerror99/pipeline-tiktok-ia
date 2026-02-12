import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Film, Clock, Zap, Plus, Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { TiltCard } from '../components/TiltCard';
import { PulseButton } from '../components/PulseButton';
import { AnimatedCounter } from '../components/AnimatedCounter';
import { apiService } from '../services/api';

export function DashboardPage() {
  const navigate = useNavigate();
  const [videos, setVideos] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiService.listVideos();
      setVideos(response.videos || []);
    } catch (err: any) {
      console.error('Error loading videos:', err);
      setError('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  // Calcul des stats depuis les vraies données
  const completedVideos = videos.filter(v => v.status === 'completed');
  const processingVideos = videos.filter(v => v.status === 'processing');
  const totalDuration = completedVideos.reduce((sum, v) => sum + (v.duration || 0), 0);
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const stats = [
    {
      label: 'Total Videos',
      value: completedVideos.length,
      icon: Film,
      color: 'emerald'
    },
    {
      label: 'Total Duration',
      value: formatDuration(totalDuration),
      icon: Clock,
      color: 'lime'
    },
    {
      label: 'Processing',
      value: processingVideos.length,
      icon: Zap,
      color: 'teal'
    }
  ];

  // 3 vidéos les plus récentes
  const recentVideos = videos
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 3)
    .map(v => ({
      id: v.video_id || v.id,
      title: v.theme,
      duration: v.duration ? `${Math.floor(v.duration / 60)}:${(v.duration % 60).toString().padStart(2, '0')}` : '0:00',
      date: new Date(v.created_at).toLocaleDateString('fr-FR', { 
        day: 'numeric', 
        month: 'short' 
      }),
      status: v.status,
      thumbnailUrl: null
    }));

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-10">
      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-12 h-12 text-emerald-400 animate-spin" />
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-center py-20">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
            <p className="text-red-400 font-medium mb-2">Failed to load dashboard</p>
            <p className="text-white/70 mb-6">{error}</p>
            <PulseButton onClick={loadVideos}>Try Again</PulseButton>
          </div>
        </motion.div>
      )}

      {/* Main Content */}
      {!isLoading && !error && (
        <>
          {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <motion.div
          initial={{
            opacity: 0,
            x: -20
          }}
          animate={{
            opacity: 1,
            x: 0
          }}>

          <p className="text-emerald-400/60 mb-1">Welcome back</p>
          <h1 className="font-display text-4xl font-bold text-white">
            Dashboard
          </h1>
        </motion.div>

        <motion.div
          initial={{
            opacity: 0,
            x: 20
          }}
          animate={{
            opacity: 1,
            x: 0
          }}
          transition={{
            delay: 0.1
          }}>

          <PulseButton onClick={() => navigate('/create')} size="lg">
            <Plus className="w-5 h-5" />
            Create Video
          </PulseButton>
        </motion.div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat, index) =>
        <motion.div
          key={index}
          initial={{
            opacity: 0,
            y: 20
          }}
          animate={{
            opacity: 1,
            y: 0
          }}
          transition={{
            delay: index * 0.1
          }}>

            <TiltCard>
              <div className="p-6 flex items-start justify-between">
                <div>
                  <p className="text-sm text-white/50 mb-1">{stat.label}</p>
                  <h3 className="text-3xl font-display font-bold text-white">
                    {typeof stat.value === 'number' ?
                  <AnimatedCounter value={stat.value} /> :

                  stat.value
                  }
                  </h3>
                </div>
                <div className="p-3 rounded-xl bg-emerald-500/10">
                  <stat.icon className="w-6 h-6 text-emerald-400" />
                </div>
              </div>
            </TiltCard>
          </motion.div>
        )}
      </div>

      {/* Recent Videos */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Sparkles className="w-5 h-5 text-lime-400" />
            <h2 className="font-display text-2xl font-semibold text-white">
              Recent Creations
            </h2>
          </div>
          <button
            onClick={() => navigate('/library')}
            className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors">

            View All →
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {recentVideos.map((video, idx) =>
          <motion.div
            key={video.id}
            initial={{
              opacity: 0,
              y: 20
            }}
            animate={{
              opacity: 1,
              y: 0
            }}
            transition={{
              delay: idx * 0.1
            }}>

              <TiltCard>
                <div className="aspect-[9/16] relative overflow-hidden cursor-pointer"
                     onClick={() => video.status === 'completed' 
                       ? navigate(`/video/${video.id}`) 
                       : navigate(`/progress/${video.id}`)}>
                  {/* Placeholder si pas de thumbnail */}
                  <div className="w-full h-full bg-gradient-to-br from-emerald-500/20 to-lime-500/20 flex items-center justify-center">
                    <Film className="w-16 h-16 text-white/30" />
                  </div>

                  <div className="absolute inset-0 bg-gradient-to-t from-dark-900 via-transparent to-transparent" />
                  <div className="absolute top-3 right-3">
                    <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${video.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-lime-500/20 text-lime-400 border border-lime-500/30 animate-pulse'}`}>

                      {video.status}
                    </span>
                  </div>
                  <div className="absolute bottom-0 left-0 right-0 p-4">
                    <h3 className="font-display font-semibold text-white truncate">
                      {video.title}
                    </h3>
                    <div className="flex justify-between text-sm text-white/40 mt-1">
                      <span>{video.duration}</span>
                      <span>{video.date}</span>
                    </div>
                  </div>
                </div>
              </TiltCard>
            </motion.div>
          )}
        </div>
      </section>
        </>
      )}
    </div>
  );
}