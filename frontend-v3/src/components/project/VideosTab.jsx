import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Film, Play, Download, ExternalLink, Loader2, AlertCircle,
  CheckCircle2, Clock, Zap, RefreshCw
} from 'lucide-react'
import { GoldButton, SecondaryButton } from '../ui/Buttons'
import { videoService } from '../../services/videos'
import { VIDEO_STATUS } from '../../config/api'

export default function VideosTab({ projectId }) {
  const [videos, setVideos] = useState([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [progress, setProgress] = useState(null)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)

  const loadVideos = useCallback(async () => {
    try {
      setLoading(true)
      const res = await videoService.list(projectId)
      setVideos(res.data?.videos || [])
    } catch {
      setError('Erreur lors du chargement des vidéos')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => { loadVideos() }, [loadVideos])

  useEffect(() => {
    return () => { wsRef.current?.close() }
  }, [])

  const handleGenerate = async () => {
    setGenerating(true)
    setProgress({ step: 'Initialisation...', percent: 0 })
    setError(null)

    try {
      const res = await videoService.generate(projectId)
      const videoId = res.data?.video_id

      if (videoId) {
        const ws = videoService.connectWs(videoId)
        wsRef.current = ws

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.status === 'completed') {
              setProgress(null)
              setGenerating(false)
              loadVideos()
              ws.close()
            } else if (data.status === 'error') {
              setError(data.message || 'Erreur lors de la génération')
              setProgress(null)
              setGenerating(false)
              ws.close()
            } else {
              setProgress({
                step: data.step || data.message || 'En cours...',
                percent: data.progress || 0,
                detail: data.detail,
              })
            }
          } catch { /* ignore parse errors */ }
        }

        ws.onerror = () => {
          setError('Connexion WebSocket perdue')
          setProgress(null)
          setGenerating(false)
        }

        ws.onclose = () => {
          if (generating) {
            setProgress(null)
            setGenerating(false)
            loadVideos()
          }
        }
      }
    } catch {
      setError('Erreur lors du lancement de la génération')
      setProgress(null)
      setGenerating(false)
    }
  }

  const statusConfig = {
    [VIDEO_STATUS.PENDING]: { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-400/5 border-yellow-400/20', label: 'En attente' },
    [VIDEO_STATUS.PROCESSING]: { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-400/5 border-blue-400/20', label: 'En cours', spin: true },
    [VIDEO_STATUS.COMPLETED]: { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-400/5 border-emerald-400/20', label: 'Terminée' },
    [VIDEO_STATUS.ERROR]: { icon: AlertCircle, color: 'text-red-400', bg: 'bg-red-400/5 border-red-400/20', label: 'Erreur' },
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Film className="w-5 h-5 text-reetik-gold" />
            Vidéos
          </h3>
          <p className="text-sm text-reetik-gray-400 mt-1">
            Générez vos vidéos TikTok à partir du scénario validé.
          </p>
        </div>

        <GoldButton onClick={handleGenerate} disabled={generating} loading={generating}>
          <Zap className="w-4 h-4" />
          Générer la vidéo
        </GoldButton>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/5 border border-red-400/20 rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Progress */}
      <AnimatePresence>
        {progress && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="card-hover-glow rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-reetik-gold/10 border border-reetik-gold/20 
                                flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-reetik-gold animate-spin" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-white">{progress.step}</p>
                  {progress.detail && (
                    <p className="text-xs text-reetik-gray-400 mt-0.5">{progress.detail}</p>
                  )}
                </div>
                <span className="text-sm font-mono text-reetik-gold">{Math.round(progress.percent)}%</span>
              </div>

              <div className="h-1.5 rounded-full bg-reetik-dark overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-gradient-to-r from-reetik-gold to-reetik-gold-light"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress.percent}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Video list */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-reetik-gold/60" />
        </div>
      ) : videos.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {videos.map((video) => {
            const cfg = statusConfig[video.status] || statusConfig[VIDEO_STATUS.PENDING]
            const StatusIcon = cfg.icon
            return (
              <motion.div
                key={video.id}
                layout
                className="card-hover-glow rounded-2xl overflow-hidden"
              >
                {/* Video preview */}
                <div className="aspect-[9/16] max-h-[320px] bg-reetik-dark relative group">
                  {video.status === VIDEO_STATUS.COMPLETED && video.stream_url ? (
                    <video
                      src={videoService.getStreamUrl(video.id)}
                      className="w-full h-full object-cover"
                      muted
                      playsInline
                      onMouseEnter={(e) => e.target.play()}
                      onMouseLeave={(e) => { e.target.pause(); e.target.currentTime = 0 }}
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <StatusIcon className={`w-12 h-12 ${cfg.color} opacity-30 ${cfg.spin ? 'animate-spin' : ''}`} />
                    </div>
                  )}

                  {/* Overlay on hover */}
                  {video.status === VIDEO_STATUS.COMPLETED && (
                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 
                                    transition-opacity flex items-center justify-center">
                      <Play className="w-12 h-12 text-white" />
                    </div>
                  )}
                </div>

                {/* Info */}
                <div className="p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className={`text-xs px-2 py-0.5 rounded-full border flex items-center gap-1 ${cfg.bg}`}>
                      <StatusIcon className={`w-3 h-3 ${cfg.color} ${cfg.spin ? 'animate-spin' : ''}`} />
                      <span className={cfg.color}>{cfg.label}</span>
                    </span>
                    {video.duration && (
                      <span className="text-xs text-reetik-gray-500">{video.duration}s</span>
                    )}
                  </div>

                  {video.created_at && (
                    <p className="text-xs text-reetik-gray-500">
                      {new Date(video.created_at).toLocaleDateString('fr-FR', {
                        day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
                      })}
                    </p>
                  )}

                  {/* Actions */}
                  {video.status === VIDEO_STATUS.COMPLETED && (
                    <div className="flex gap-2">
                      <SecondaryButton
                        size="sm"
                        className="flex-1 text-xs"
                        onClick={() => window.open(videoService.getStreamUrl(video.id), '_blank')}
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        Ouvrir
                      </SecondaryButton>
                      <GoldButton
                        size="sm"
                        className="flex-1 text-xs"
                        onClick={() => window.open(videoService.getDownloadUrl(video.id), '_blank')}
                      >
                        <Download className="w-3.5 h-3.5" />
                        Télécharger
                      </GoldButton>
                    </div>
                  )}
                </div>
              </motion.div>
            )
          })}
        </div>
      ) : (
        <div className="text-center py-12 text-reetik-gray-500">
          <Film className="w-12 h-12 mx-auto mb-3 opacity-20" />
          <p className="text-sm">Aucune vidéo pour le moment</p>
          <p className="text-xs mt-1">Validez d'abord votre scénario puis lancez la génération</p>
        </div>
      )}
    </div>
  )
}
