import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Hash, User, Type, Loader2, AlertCircle,
  Copy, CheckCircle2, Sparkles, Film,
} from 'lucide-react'
import { GoldButton } from '../ui/Buttons'
import { tiktokService } from '../../services/tiktok'
import { videoService } from '../../services/videos'

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = async () => {
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button onClick={handleCopy} className="p-1 hover:bg-reetik-border/30 rounded transition-colors">
      {copied
        ? <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        : <Copy className="w-3.5 h-3.5 text-reetik-gray-500 hover:text-reetik-gray-300" />}
    </button>
  )
}

// ── Bio globale ──────────────────────────────────────────────────────────
function BioSection({ projectId }) {
  const [bio, setBio] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetch = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await tiktokService.suggestProfile({ project_id: projectId })
      const raw = res.data || res
      setBio(raw.profile || raw.bio || raw.suggestion || JSON.stringify(raw))
    } catch {
      setError('Erreur génération bio')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card-hover-glow rounded-2xl p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-reetik-gold/10 border border-reetik-gold/20 flex items-center justify-center">
            <User className="w-5 h-5 text-reetik-gold" />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-white">Bio de profil</h4>
            <p className="text-xs text-reetik-gray-500">Biographie TikTok optimisée pour votre projet</p>
          </div>
        </div>
        <GoldButton size="sm" onClick={fetch} loading={loading}>
          <Sparkles className="w-3.5 h-3.5" />
          {bio ? 'Régénérer' : 'Générer'}
        </GoldButton>
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
      <AnimatePresence mode="wait">
        {bio && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
            <div className="bg-reetik-dark rounded-xl p-4 border border-reetik-border/30">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm text-reetik-gray-200 leading-relaxed whitespace-pre-wrap">{bio}</p>
                <CopyButton text={bio} />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// ── TikTok par vidéo ──────────────────────────────────────────────────────
function VideoTikTok({ projectId, video }) {
  const [titleList, setTitleList] = useState(null)
  const [hashtags, setHashtags] = useState(null)
  const [loadingTitle, setLoadingTitle] = useState(false)
  const [loadingHashtags, setLoadingHashtags] = useState(false)
  const [error, setError] = useState(null)

  const fetchTitle = async () => {
    setLoadingTitle(true); setError(null)
    try {
      const res = await tiktokService.suggestTitle({ project_id: projectId, video_id: video.id })
      const raw = res.data || res
      const titles = raw.titles || raw.suggestions || (typeof raw === 'string' ? [raw] : [JSON.stringify(raw)])
      setTitleList(Array.isArray(titles) ? titles : [titles])
    } catch { setError('Erreur titre') } finally { setLoadingTitle(false) }
  }

  const fetchHashtags = async () => {
    setLoadingHashtags(true); setError(null)
    try {
      const res = await tiktokService.suggestHashtags({ project_id: projectId, video_id: video.id })
      const raw = res.data || res
      setHashtags(raw.hashtags || raw.suggestions || (Array.isArray(raw) ? raw : []))
    } catch { setError('Erreur hashtags') } finally { setLoadingHashtags(false) }
  }

  const videoDate = video.created_at
    ? new Date(video.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
    : null

  return (
    <div className="card-hover-glow rounded-2xl p-5 space-y-5">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-reetik-border/20 flex items-center justify-center flex-shrink-0">
          <Film className="w-5 h-5 text-reetik-gray-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-white truncate">{video.title || `Vidéo ${video.id?.slice(0, 8)}`}</p>
          <p className="text-xs text-reetik-gray-500">{video.actual_duration || video.target_duration}s{videoDate ? ` · ${videoDate}` : ''}</p>
        </div>
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}

      {/* Titres */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Type className="w-4 h-4 text-reetik-gold" />
            <span className="text-xs font-medium text-white">Titres</span>
          </div>
          <GoldButton size="sm" onClick={fetchTitle} loading={loadingTitle}>
            <Sparkles className="w-3 h-3" />
            {titleList ? 'Régénérer' : 'Suggérer'}
          </GoldButton>
        </div>
        <AnimatePresence mode="wait">
          {titleList && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} className="space-y-2">
              {titleList.map((t, i) => (
                <div key={i} className="bg-reetik-dark rounded-lg p-3 border border-reetik-border/30 flex items-start justify-between gap-2">
                  <p className="text-sm text-reetik-gray-200">{typeof t === 'string' ? t : t.title || ''}</p>
                  <CopyButton text={typeof t === 'string' ? t : t.title || ''} />
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Hashtags */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Hash className="w-4 h-4 text-reetik-gold" />
            <span className="text-xs font-medium text-white">Hashtags</span>
          </div>
          <GoldButton size="sm" onClick={fetchHashtags} loading={loadingHashtags}>
            <Sparkles className="w-3 h-3" />
            {hashtags ? 'Régénérer' : 'Suggérer'}
          </GoldButton>
        </div>
        <AnimatePresence mode="wait">
          {hashtags && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
              <div className="flex flex-wrap gap-2">
                {hashtags.map((tag, i) => {
                  const tagStr = typeof tag === 'string' ? tag : tag.hashtag || tag.name || ''
                  return (
                    <motion.span key={i} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.04 }}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm bg-reetik-gold/5 border border-reetik-gold/15 text-reetik-gold hover:bg-reetik-gold/10 transition-colors cursor-pointer group"
                      onClick={() => navigator.clipboard.writeText(tagStr)} title="Cliquer pour copier">
                      <Hash className="w-3 h-3 opacity-50" />
                      {tagStr.replace(/^#/, '')}
                      <Copy className="w-3 h-3 opacity-0 group-hover:opacity-50 transition-opacity" />
                    </motion.span>
                  )
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

// ── Export principal ──────────────────────────────────────────────────────
export default function TikTokTab({ projectId }) {
  const [completedVideos, setCompletedVideos] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const loadVideos = useCallback(async () => {
    try {
      setLoading(true)
      const res = await videoService.list(projectId)
      setCompletedVideos((res.videos || []).filter((v) => v.status === 'completed'))
    } catch {
      setError('Erreur lors du chargement des vidéos')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => { loadVideos() }, [loadVideos])

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Hash className="w-5 h-5 text-reetik-gold" />
          TikTok
        </h3>
        <p className="text-sm text-reetik-gray-400 mt-1">Optimisez votre contenu TikTok avec des suggestions IA.</p>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/5 border border-red-400/20 rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />{error}
        </div>
      )}

      <BioSection projectId={projectId} />

      <div className="space-y-4">
        <h4 className="text-sm font-semibold text-white border-b border-reetik-border/20 pb-2">Par vidéo</h4>
        {loading ? (
          <div className="flex justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-reetik-gold/60" /></div>
        ) : completedVideos.length === 0 ? (
          <div className="text-center py-10 text-reetik-gray-600">
            <Film className="w-10 h-10 mx-auto mb-3 opacity-20" />
            <p className="text-xs">Aucune vidéo terminée pour l'instant</p>
          </div>
        ) : (
          <div className="space-y-4">
            {completedVideos.map((v) => <VideoTikTok key={v.id} projectId={projectId} video={v} />)}
          </div>
        )}
      </div>
    </div>
  )
}
