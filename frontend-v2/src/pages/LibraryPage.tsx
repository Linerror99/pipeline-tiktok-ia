import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, Film, Play, AlertCircle, Loader2 } from 'lucide-react';
import { TiltCard } from '../components/TiltCard';
import { apiService } from '../services/api';

interface Video {
  video_id: string;
  theme: string;
  status: string;
  created_at: string;
  duration?: number;
  progress?: number;
  current_step?: string;
}

export function LibraryPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiService.listVideos();
      setVideos(data.videos || []);
    } catch (err: any) {
      console.error('Error loading videos:', err);
      setError('Failed to load videos');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredVideos = videos.filter(video =>
    video.theme?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return 'Unknown';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      case 'processing':
        return 'bg-lime-500/20 text-lime-400 border-lime-500/30 animate-pulse';
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-white/10 text-white/50 border-white/20';
    }
  };

  return (
    <div className="p-6 md:p-10 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}>
          <div className="flex items-center space-x-3 mb-2">
            <Film className="w-6 h-6 text-lime-400" />
            <h1 className="font-display text-3xl font-bold text-white">
              Your Library
            </h1>
          </div>
          <p className="text-white/50">
            {isLoading ? 'Loading...' : `${filteredVideos.length} video${filteredVideos.length !== 1 ? 's' : ''}`}
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center space-x-4 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search videos..."
              className="w-full bg-emerald-500/5 border border-emerald-500/20 rounded-xl py-2.5 pl-10 pr-4 text-white placeholder-white/30 text-sm focus:border-emerald-500/50 transition-all"
            />
          </div>
          <button 
            onClick={loadVideos}
            className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400 hover:bg-emerald-500/20 transition-all"
            title="Refresh">
            <Filter size={18} />
          </button>
        </motion.div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-emerald-400 animate-spin" />
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 p-6 bg-red-500/10 border border-red-500/20 rounded-xl">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <div>
            <p className="text-red-400 font-medium">Error loading videos</p>
            <p className="text-white/70 text-sm">{error}</p>
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {!isLoading && !error && filteredVideos.length === 0 && (
        <div className="text-center py-20">
          <Film className="w-16 h-16 text-white/20 mx-auto mb-4" />
          <p className="text-white/50">
            {searchQuery ? 'No videos match your search' : 'No videos yet. Create your first one!'}
          </p>
        </div>
      )}

      {/* Video Grid */}
      {!isLoading && !error && filteredVideos.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredVideos.map((video, idx) => (
            <motion.div
              key={video.video_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}>
              <TiltCard>
                <div className="aspect-[9/16] relative overflow-hidden group cursor-pointer"
                     onClick={() => {
                       if (video.status === 'completed') {
                         navigate(`/video/${video.video_id}`);
                       } else if (video.status === 'processing') {
                         navigate(`/progress/${video.video_id}`);
                       }
                     }}>
                  {/* Placeholder background */}
                  <div className="w-full h-full bg-gradient-to-br from-emerald-500/20 to-lime-500/20 flex items-center justify-center">
                    <Film className="w-16 h-16 text-white/30" />
                  </div>

                  <div className="absolute inset-0 bg-gradient-to-t from-dark-900 via-transparent to-transparent" />

                  <div className="absolute top-3 right-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(video.status)}`}>
                      {video.status}
                    </span>
                  </div>

                  {video.status === 'completed' && (
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                        className="w-14 h-14 rounded-full bg-gradient-to-r from-emerald-500 to-lime-500 flex items-center justify-center shadow-glow">
                        <Play className="w-6 h-6 text-dark-900 ml-0.5" fill="currentColor" />
                      </motion.button>
                    </div>
                  )}

                  {video.status === 'processing' && video.progress !== undefined && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/10">
                      <div 
                        className="h-full bg-gradient-to-r from-emerald-500 to-lime-500"
                        style={{ width: `${video.progress}%` }}
                      />
                    </div>
                  )}

                  <div className="absolute bottom-0 left-0 right-0 p-4">
                    <h3 className="text-white font-semibold mb-1 line-clamp-2">
                      {video.theme}
                    </h3>
                    <div className="flex items-center justify-between text-xs text-white/50">
                      <span>{formatDuration(video.duration)}</span>
                      <span>{formatDate(video.created_at)}</span>
                    </div>
                    {video.current_step && video.status === 'processing' && (
                      <p className="text-xs text-lime-400 mt-1">{video.current_step}</p>
                    )}
                  </div>
                </div>
              </TiltCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}