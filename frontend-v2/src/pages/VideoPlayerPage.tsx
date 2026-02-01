import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowLeft,
  Play,
  Pause,
  Volume2,
  VolumeX,
  Maximize2,
  Download,
  Share2,
  Check,
  AlertCircle,
  Loader2 } from
'lucide-react';
import { TiltCard } from '../components/TiltCard';
import { PulseButton } from '../components/PulseButton';
import { RotatingRings } from '../components/RotatingRings';
import { apiService } from '../services/api';

export function VideoPlayerPage() {
  const navigate = useNavigate();
  const { videoId } = useParams<{ videoId: string }>();
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [copied, setCopied] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [videoData, setVideoData] = useState<any>(null);

  useEffect(() => {
    if (!videoId) return;
    
    const loadVideo = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Get video status first
        const status = await apiService.getVideoStatus(videoId);
        setVideoData(status);
        
        if (status.status !== 'completed') {
          setError('Video is not ready yet');
          return;
        }

        // Get signed URL
        const url = await apiService.getVideoUrl(videoId);
        setVideoUrl(url);
      } catch (err: any) {
        console.error('Error loading video:', err);
        setError(err.response?.data?.detail || 'Failed to load video');
      } finally {
        setIsLoading(false);
      }
    };

    loadVideo();
  }, [videoId]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    
    if (isPlaying) {
      videoRef.current.pause();
    } else {
      videoRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleDownload = async () => {
    if (!videoUrl || !videoId) return;
    
    try {
      const response = await fetch(videoUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `video_${videoId}.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download failed:', err);
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-dark-900/80 via-dark-900/90 to-dark-900" />

      {/* Rotating Rings Background */}
      <div className="absolute top-1/2 left-1/4 -translate-x-1/2 -translate-y-1/2 opacity-10 pointer-events-none">
        <RotatingRings size="lg" />
      </div>

      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <div className="p-6 flex items-center justify-between">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center space-x-2 text-white/60 hover:text-emerald-400 transition-colors">
            <ArrowLeft size={20} />
            <span className="hidden md:inline">Back</span>
          </button>
          <h1 className="font-display text-lg text-white/80">
            {videoData?.theme || 'Video Preview'}
          </h1>
          <div className="w-20" />
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex-1 flex items-center justify-center">
            <Loader2 className="w-12 h-12 text-emerald-400 animate-spin" />
          </div>
        )}

        {/* Error State */}
        {error && !isLoading && (
          <div className="flex-1 flex items-center justify-center p-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center">
              <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
              <p className="text-red-400 font-medium mb-2">Failed to load video</p>
              <p className="text-white/70 mb-6">{error}</p>
              <PulseButton onClick={() => navigate('/library')}>
                Back to Library
              </PulseButton>
            </motion.div>
          </div>
        )}

        {/* Main Content */}
        {!isLoading && !error && videoUrl && (
          <div className="flex-1 flex flex-col lg:flex-row items-center justify-center gap-8 p-6">
            {/* Video Player */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="relative aspect-[9/16] w-full max-w-sm bg-black rounded-2xl overflow-hidden shadow-2xl shadow-emerald-500/10">
              
              <video
                ref={videoRef}
                src={videoUrl}
                className="w-full h-full object-cover"
                onClick={togglePlay}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
              />

              {/* Play/Pause Overlay */}
              <div
                className="absolute inset-0 flex items-center justify-center bg-black/20 cursor-pointer opacity-0 hover:opacity-100 transition-opacity"
                onClick={togglePlay}>
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-20 h-20 rounded-full bg-emerald-500/20 backdrop-blur-md flex items-center justify-center border border-emerald-500/30">
                  {isPlaying ? (
                    <Pause className="w-8 h-8 text-emerald-400" fill="currentColor" />
                  ) : (
                    <Play className="w-8 h-8 text-emerald-400 ml-1" fill="currentColor" />
                  )}
                </motion.div>
              </div>

              {/* Video Controls */}
              <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent">
                <div className="flex items-center justify-between text-white">
                  <div className="flex items-center space-x-4">
                    <button onClick={togglePlay} className="hover:text-emerald-400 transition-colors">
                      {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                    </button>
                    <button onClick={toggleMute} className="hover:text-emerald-400 transition-colors">
                      {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
                    </button>
                  </div>
                  <button 
                    onClick={() => videoRef.current?.requestFullscreen()}
                    className="hover:text-emerald-400 transition-colors">
                    <Maximize2 size={20} />
                  </button>
                </div>
              </div>
            </motion.div>

            {/* Info Panel */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="w-full max-w-md space-y-6">

              <TiltCard glowOnHover={false}>
                <div className="p-6">
                  <h2 className="font-display text-2xl font-bold text-white mb-2">
                    {videoData?.theme || 'Video'}
                  </h2>
                  <p className="text-white/50 text-sm mb-6">
                    {videoData?.created_at && `Created on ${new Date(videoData.created_at).toLocaleDateString()}`}
                    {videoData?.duration && ` • ${Math.floor(videoData.duration / 60)}:${(videoData.duration % 60).toString().padStart(2, '0')}`}
                  </p>

                  <div className="grid grid-cols-2 gap-3">
                    <PulseButton
                      onClick={handleDownload}
                      variant="secondary"
                      fullWidth>
                      <Download size={18} />
                      Download
                    </PulseButton>
                    <PulseButton
                      onClick={handleCopyLink}
                      variant="secondary"
                      fullWidth>
                      {copied ? <Check size={18} /> : <Share2 size={18} />}
                      {copied ? 'Copied!' : 'Share'}
                    </PulseButton>
                  </div>
                </div>
              </TiltCard>

              <TiltCard glowOnHover={false}>
                <div className="p-6">
                  <h3 className="font-medium text-white mb-4">Video Details</h3>
                  <div className="space-y-3 text-sm">
                    {videoData?.duration && (
                      <div className="flex justify-between">
                        <span className="text-white/50">Duration</span>
                        <span className="text-emerald-400">
                          {Math.floor(videoData.duration / 60)}:{(videoData.duration % 60).toString().padStart(2, '0')}
                        </span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-white/50">Status</span>
                      <span className="text-emerald-400 capitalize">{videoData?.status || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/50">Resolution</span>
                      <span className="text-emerald-400">1080x1920 (9:16)</span>
                    </div>
                  </div>
                </div>
              </TiltCard>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}