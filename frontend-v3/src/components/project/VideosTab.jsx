import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Film, Play, Download, ExternalLink, Loader2, AlertCircle,
  CheckCircle2, Clock, Zap, RefreshCw, MessageSquare, Trash2,
} from 'lucide-react'
import { GoldButton, SecondaryButton } from '../ui/Buttons'
import { videoService } from '../../services/videos'
import { scenarioService } from '../../services/scenarios'
import { VIDEO_STATUS } from '../../config/api'

// ── Hook WS avec reconnexion automatique ───────────────────────────────────
function useVideoWs(videoId, onUpdate) {
  const wsRef = useRef(null)
  const reconnectRef = useRef(null)
  const stoppedRef = useRef(false)

  const connect = useCallback(() => {
    if (stoppedRef.current || !videoId) return
    const ws = videoService.connectWs(videoId, onUpdate)
    wsRef.current = ws

    ws.onclose = () => {
      if (!stoppedRef.current) {
        reconnectRef.current = setTimeout(connect, 4000)
      }
    }
  }, [videoId, onUpdate])

  useEffect(() => {
    stoppedRef.current = false
    connect()
    return () => {
      stoppedRef.current = true
      clearTimeout(reconnectRef.current)
      wsRef.current?.close()
    }
  }, [connect])
}

// ── Barre de progression ────────────────────────────────────────────────────
function ProgressBar({ progress }) {
  if (!progress) return null
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        className="overflow-hidden"
      >
        <div className="card-hover-glow rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-reetik-gold/10 border border-reetik-gold/20 flex items-center justify-center">
              <Loader2 className="w-4 h-4 text-reetik-gold animate-spin" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-white">{progress.current_step || 'Génération en cours...'}</p>
              {progress.extensions_planned > 0 && (
                <p className="text-xs text-reetik-gray-400 mt-0.5">
                  Extension {progress.extensions_completed}/{progress.extensions_planned}
                </p>
              )}
            </div>
            <span className="text-sm font-mono text-reetik-gold">{Math.round(progress.progress || 0)}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-reetik-dark overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-reetik-gold to-amber-400"
              initial={{ width: 0 }}
              animate={{ width: `${progress.progress || 0}%` }}
              transition={{ duration: 0.6 }}
            />
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}

// ── Carte vidéo individuelle (avec WS interne) ─────────────────────────────
function VideoCard({ video: initialVideo, onRefresh, onDelete }) {
  const [video, setVideo] = useState(initialVideo)
  const [retrying, setRetrying] = useState(false)
  const isActive = !['completed', 'failed'].includes(video.status)

  const handleRetry = async () => {
    setRetrying(true)
    try {
      const updated = await videoService.retry(video.id)
      setVideo(updated)
      onRefresh()
    } catch (err) {
      console.error('Retry failed:', err)
    } finally {
      setRetrying(false)
    }
  }

  // WS actif seulement pour les vidéos en cours de génération
  const handleWsUpdate = useCallback((data) => {
    setVideo((prev) => ({ ...prev, ...data }))
    if (data.status === 'completed' || data.status === 'failed') {
      onRefresh()
    }
  }, [onRefresh])

  // Hook conditionnel — actif seulement si vidéo en cours avec un ID valide
  useVideoWs(
    (isActive && video.id) ? video.id : null,
    handleWsUpdate,
  )

  const statusConfig = {
    [VIDEO_STATUS.PENDING]: { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-400/5 border-yellow-400/20', label: 'En attente' },
    generating: { icon: Loader2, color: 'text-blue-400', bg: 'bg-blue-400/5 border-blue-400/20', label: 'En cours', spin: true },
    [VIDEO_STATUS.COMPLETED]: { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-400/5 border-emerald-400/20', label: 'Terminée' },
    failed: { icon: AlertCircle, color: 'text-red-400', bg: 'bg-red-400/5 border-red-400/20', label: 'Échec' },
  }

  const cfg = statusConfig[video.status] || statusConfig[VIDEO_STATUS.PENDING]
  const StatusIcon = cfg.icon

  return (
    <motion.div layout className="card-hover-glow rounded-2xl overflow-hidden">
      {/* Preview */}
      <div className="aspect-[9/16] max-h-[260px] bg-reetik-dark relative group">
        {video.status === VIDEO_STATUS.COMPLETED && video.video_url ? (
          <video
            src={video.video_url}
            className="w-full h-full object-cover"
            muted playsInline
            onMouseEnter={(e) => e.target.play()}
            onMouseLeave={(e) => { e.target.pause(); e.target.currentTime = 0 }}
          />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center gap-2">
            <StatusIcon className={`w-10 h-10 ${cfg.color} opacity-40 ${cfg.spin ? 'animate-spin' : ''}`} />
            {video.status === 'generating' && (
              <div className="w-24 h-1 rounded-full bg-reetik-border overflow-hidden">
                <motion.div
                  className="h-full bg-reetik-gold/60 rounded-full"
                  animate={{ width: [`${video.progress || 10}%`, `${(video.progress || 10) + 10}%`] }}
                  transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
                />
              </div>
            )}
          </div>
        )}
        {video.status === VIDEO_STATUS.COMPLETED && (
          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <Play className="w-12 h-12 text-white" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3 space-y-2">
        <div className="flex items-center justify-between">
          <span className={`text-xs px-2 py-0.5 rounded-full border flex items-center gap-1 ${cfg.bg}`}>
            <StatusIcon className={`w-3 h-3 ${cfg.color} ${cfg.spin ? 'animate-spin' : ''}`} />
            <span className={cfg.color}>{cfg.label}</span>
          </span>
          {(video.actual_duration || video.target_duration) && (
            <span className="text-xs text-reetik-gray-500">{video.actual_duration || video.target_duration}s</span>
          )}
        </div>

        {/* Progression si en cours */}
        {video.status === 'generating' && (
          <div className="space-y-1">
            <p className="text-xs text-reetik-gray-400">{video.current_step || ''}</p>
            <div className="h-1 rounded-full bg-reetik-dark overflow-hidden">
              <motion.div
                className="h-full rounded-full bg-reetik-gold/60"
                animate={{ width: `${video.progress || 0}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        )}

        {video.error && (
          <p className="text-xs text-red-400 truncate">{video.error}</p>
        )}

        {video.status === 'failed' && (
          <SecondaryButton size="sm" className="w-full text-xs" onClick={handleRetry} disabled={retrying}>
            {retrying
              ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
              : <RefreshCw className="w-3.5 h-3.5" />}
            {retrying ? 'Relance...' : 'Réessayer'}
          </SecondaryButton>
        )}

        {video.status === VIDEO_STATUS.COMPLETED && (
          <div className="flex gap-2">
            <SecondaryButton size="sm" className="flex-1 text-xs"
              onClick={() => window.open(video.video_url, '_blank')}>
              <ExternalLink className="w-3.5 h-3.5" />
              Ouvrir
            </SecondaryButton>
            <GoldButton size="sm" className="flex-1 text-xs"
              onClick={() => window.open(video.video_url, '_blank')}>
              <Download className="w-3.5 h-3.5" />
              Télécharger
            </GoldButton>
          </div>
        )}

        {video.created_at && (
          <p className="text-xs text-reetik-gray-600">
            {new Date(video.created_at).toLocaleDateString('fr-FR', {
              day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
            })}
          </p>
        )}

        {/* Delete */}
        <div className="flex justify-end">
          <button
            onClick={() => onDelete(video.id)}
            className="p-1.5 rounded-lg text-reetik-gray-600
                       hover:text-red-400 hover:bg-red-500/10
                       transition-colors"
            title="Supprimer la vidéo"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}

// ── Bloc scénario + ses vidéos ─────────────────────────────────────────────
function ScenarioSection({ scenario, videos, onGenerate, generating, onRefresh, onDeleteVideo }) {
  return (
    <div className="space-y-4">
      {/* Header scénario */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-reetik-gold" />
          <span className="text-sm font-semibold text-white">
            {scenario.title || `Scénario ${scenario.id?.slice(0, 6)}`}
          </span>
          {scenario.target_duration && (
            <span className="text-xs text-reetik-gray-500 bg-reetik-dark px-2 py-0.5 rounded-full border border-reetik-border/30">
              {scenario.target_duration}s
            </span>
          )}
        </div>
        <GoldButton
          size="sm"
          onClick={() => onGenerate(scenario)}
          disabled={generating === scenario.id}
          loading={generating === scenario.id}
        >
          <Zap className="w-3.5 h-3.5" />
          Générer une vidéo
        </GoldButton>
      </div>

      {/* Vidéos de ce scénario */}
      {videos.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {videos.map((v) => (
            v.id ? <VideoCard key={v.id} video={v} onRefresh={onRefresh} onDelete={onDeleteVideo} /> : null
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-reetik-gray-600 border border-dashed border-reetik-border/20 rounded-2xl">
          <Film className="w-8 h-8 mx-auto mb-2 opacity-20" />
          <p className="text-xs">Aucune vidéo générée pour ce scénario</p>
        </div>
      )}
    </div>
  )
}

// ── Export principal ───────────────────────────────────────────────────────
export default function VideosTab({ projectId }) {
  const [videos, setVideos] = useState([])
  const [validatedScenarios, setValidatedScenarios] = useState([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(null)
  const [error, setError] = useState(null)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      const [videosRes, scenariosRes] = await Promise.all([
        videoService.list(projectId),
        scenarioService.list(projectId),
      ])
      setVideos(videosRes.videos || [])
      setValidatedScenarios(
        (scenariosRes.scenarios || []).filter((s) => s.status === 'validated')
      )
    } catch {
      setError('Erreur lors du chargement')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => { loadData() }, [loadData])

  const handleGenerate = async (scenario) => {
    setGenerating(scenario.id)
    setError(null)
    try {
      await videoService.generate({ scenario_id: scenario.id, project_id: projectId })
      await loadData()
    } catch {
      setError('Erreur lors du lancement de la génération')
    } finally {
      setGenerating(null)
    }
  }

  const handleDeleteVideo = async (videoId) => {
    try {
      await videoService.remove(videoId)
      setVideos((prev) => prev.filter((v) => v.id !== videoId))
    } catch {
      setError('Erreur lors de la suppression')
    }
  }

  // Regrouper les vidéos par scenario_id
  const videosByScenario = (scenarioId) =>
    videos.filter((v) => v.scenario_id === scenarioId)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Film className="w-5 h-5 text-reetik-gold" />
            Vidéos
          </h3>
          <p className="text-sm text-reetik-gray-400 mt-1">
            Génération Veo 3.1 par scénario validé.
          </p>
        </div>
        <SecondaryButton size="sm" onClick={loadData} disabled={loading}>
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </SecondaryButton>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/5 border border-red-400/20 rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-reetik-gold/60" />
        </div>
      ) : validatedScenarios.length === 0 ? (
        <div className="text-center py-16 text-reetik-gray-500">
          <Film className="w-14 h-14 mx-auto mb-4 opacity-20" />
          <p className="text-sm font-medium text-white mb-2">Aucun scénario validé</p>
          <p className="text-xs">Validez un scénario dans l'onglet Scénario pour générer des vidéos.</p>
        </div>
      ) : (
        <div className="space-y-10 divide-y divide-reetik-border/20">
          {validatedScenarios.map((sc, i) => (
            <div key={sc.id} className={i > 0 ? 'pt-10' : ''}>
              <ScenarioSection
                scenario={sc}
                videos={videosByScenario(sc.id)}
                onGenerate={handleGenerate}
                generating={generating}
                onRefresh={loadData}
                onDeleteVideo={handleDeleteVideo}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
