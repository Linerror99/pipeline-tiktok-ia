import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Hash, User, TrendingUp, Type, Loader2, AlertCircle,
  Copy, CheckCircle2, Sparkles
} from 'lucide-react'
import { GoldButton } from '../ui/Buttons'
import { tiktokService } from '../../services/tiktok'

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

const sections = [
  {
    key: 'profile',
    icon: User,
    title: 'Bio de profil',
    description: 'Suggestion de biographie TikTok optimisée',
    action: 'Générer une bio',
    fetch: (projectId) => tiktokService.suggestProfile(projectId),
    resultKey: 'profile',
  },
  {
    key: 'hashtags',
    icon: Hash,
    title: 'Hashtags',
    description: 'Hashtags tendance liés à votre contenu',
    action: 'Suggérer des hashtags',
    fetch: (projectId) => tiktokService.suggestHashtags(projectId),
    resultKey: 'hashtags',
  },
  {
    key: 'title',
    icon: Type,
    title: 'Titre de vidéo',
    description: 'Titres accrocheurs pour votre TikTok',
    action: 'Suggérer des titres',
    fetch: (projectId) => tiktokService.suggestTitle(projectId),
    resultKey: 'titles',
  },
]

export default function TikTokTab({ projectId }) {
  const [results, setResults] = useState({})
  const [loadingKey, setLoadingKey] = useState(null)
  const [error, setError] = useState(null)

  const handleFetch = async (section) => {
    setLoadingKey(section.key)
    setError(null)
    try {
      const res = await section.fetch(projectId)
      setResults((prev) => ({ ...prev, [section.key]: res.data }))
    } catch {
      setError(`Erreur lors de la génération (${section.title})`)
    } finally {
      setLoadingKey(null)
    }
  }

  const renderResult = (section) => {
    const data = results[section.key]
    if (!data) return null

    if (section.key === 'profile') {
      const bio = data.profile || data.bio || data.suggestion || JSON.stringify(data)
      return (
        <div className="bg-reetik-dark rounded-xl p-4 border border-reetik-border/30 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm text-reetik-gray-200 leading-relaxed whitespace-pre-wrap">{bio}</p>
            <CopyButton text={bio} />
          </div>
        </div>
      )
    }

    if (section.key === 'hashtags') {
      const tags = data.hashtags || data.suggestions || (Array.isArray(data) ? data : [])
      return (
        <div className="bg-reetik-dark rounded-xl p-4 border border-reetik-border/30">
          <div className="flex flex-wrap gap-2">
            {tags.map((tag, i) => {
              const tagStr = typeof tag === 'string' ? tag : tag.hashtag || tag.name || ''
              return (
                <motion.span
                  key={i}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                  className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm
                             bg-reetik-gold/5 border border-reetik-gold/15 text-reetik-gold
                             hover:bg-reetik-gold/10 transition-colors cursor-pointer group"
                  onClick={() => navigator.clipboard.writeText(tagStr)}
                  title="Cliquer pour copier"
                >
                  <Hash className="w-3 h-3 opacity-50" />
                  {tagStr.replace(/^#/, '')}
                  <Copy className="w-3 h-3 opacity-0 group-hover:opacity-50 transition-opacity" />
                </motion.span>
              )
            })}
          </div>
        </div>
      )
    }

    if (section.key === 'title') {
      const titles = data.titles || data.suggestions || (Array.isArray(data) ? data : [])
      return (
        <div className="space-y-2">
          {titles.map((t, i) => {
            const titleStr = typeof t === 'string' ? t : t.title || t.suggestion || ''
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className="flex items-center justify-between gap-3 bg-reetik-dark rounded-xl px-4 py-3 
                           border border-reetik-border/30 hover:border-reetik-gold/20 transition-colors"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="text-xs font-mono text-reetik-gold/50">{String(i + 1).padStart(2, '0')}</span>
                  <p className="text-sm text-reetik-gray-200 truncate">{titleStr}</p>
                </div>
                <CopyButton text={titleStr} />
              </motion.div>
            )
          })}
        </div>
      )
    }

    return null
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-reetik-gold" />
          Assistant TikTok
        </h3>
        <p className="text-sm text-reetik-gray-400 mt-1">
          Optimisez votre présence TikTok avec des suggestions IA.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/5 border border-red-400/20 rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Sections */}
      <div className="space-y-6">
        {sections.map((section) => {
          const Icon = section.icon
          const isLoading = loadingKey === section.key
          const hasResult = !!results[section.key]

          return (
            <motion.div
              key={section.key}
              layout
              className="card-hover-glow rounded-2xl p-5 space-y-4"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-reetik-gold/10 border border-reetik-gold/20 
                                  flex items-center justify-center">
                    <Icon className="w-5 h-5 text-reetik-gold" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white">{section.title}</h4>
                    <p className="text-xs text-reetik-gray-500">{section.description}</p>
                  </div>
                </div>

                <GoldButton
                  size="sm"
                  onClick={() => handleFetch(section)}
                  disabled={isLoading}
                  loading={isLoading}
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  {hasResult ? 'Régénérer' : section.action}
                </GoldButton>
              </div>

              <AnimatePresence mode="wait">
                {hasResult && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {renderResult(section)}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
