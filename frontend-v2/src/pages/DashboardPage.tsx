import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Film, Clock, Zap, Plus, Sparkles } from 'lucide-react';
import { TiltCard } from '../components/TiltCard';
import { PulseButton } from '../components/PulseButton';
import { AnimatedCounter } from '../components/AnimatedCounter';
export function DashboardPage() {
  const navigate = useNavigate();
  const stats = [
  {
    label: 'Total Videos',
    value: 24,
    icon: Film,
    color: 'emerald'
  },
  {
    label: 'Total Duration',
    value: '12m 30s',
    icon: Clock,
    color: 'lime'
  },
  {
    label: 'Processing',
    value: 1,
    icon: Zap,
    color: 'teal'
  }];

  const recentVideos = [
  {
    id: '1',
    title: 'Morning Routine Tips',
    duration: '00:45',
    date: 'Today',
    status: 'completed',
    thumbnailUrl:
    'https://images.unsplash.com/photo-1611162616475-46b635cb6868?q=80&w=600&auto=format&fit=crop'
  },
  {
    id: '2',
    title: 'Coffee Culture',
    duration: '00:30',
    date: 'Yesterday',
    status: 'processing',
    thumbnailUrl:
    'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=80&w=600&auto=format&fit=crop'
  },
  {
    id: '3',
    title: 'Travel Hacks 2024',
    duration: '01:00',
    date: '2 days ago',
    status: 'completed',
    thumbnailUrl:
    'https://images.unsplash.com/photo-1488646953014-85cb44e25828?q=80&w=600&auto=format&fit=crop'
  }];

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-10">
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
                <div className="aspect-[9/16] relative overflow-hidden">
                  <img
                  src={video.thumbnailUrl}
                  alt={video.title}
                  className="w-full h-full object-cover" />

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
    </div>);

}