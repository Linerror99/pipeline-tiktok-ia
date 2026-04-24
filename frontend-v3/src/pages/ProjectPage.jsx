import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ArrowLeft, Users, MessageSquare, Film, Hash, Loader2 } from 'lucide-react'
import { projectService } from '../services/projects'
import CharactersTab from '../components/project/CharactersTab'
import ScenarioTab from '../components/project/ScenarioTab'
import VideosTab from '../components/project/VideosTab'
import TikTokTab from '../components/project/TikTokTab'

const TABS = [
  { id: 'characters', label: 'Personnages', icon: Users },
  { id: 'scenario', label: 'Scénario', icon: MessageSquare },
  { id: 'videos', label: 'Vidéos', icon: Film },
  { id: 'tiktok', label: 'TikTok', icon: Hash },
]

export default function ProjectPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState(null)
  const [activeTab, setActiveTab] = useState('characters')
  const [loading, setLoading] = useState(true)

  const loadProject = useCallback(async () => {
    try {
      const data = await projectService.get(id)
      setProject(data)
    } catch {
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }, [id, navigate])

  useEffect(() => { loadProject() }, [loadProject])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-reetik-gold animate-spin" />
      </div>
    )
  }

  const TabContent = {
    characters: CharactersTab,
    scenario: ScenarioTab,
    videos: VideosTab,
    tiktok: TikTokTab,
  }[activeTab]

  return (
    <div className="min-h-screen pt-16 flex">
      {/* ── Sidebar gauche ── */}
      <aside className="w-56 flex-shrink-0 sticky top-16 h-[calc(100vh-4rem)] border-r border-reetik-border/30
                         bg-reetik-card/40 backdrop-blur-sm flex flex-col">
        {/* Back + Project name */}
        <div className="p-4 border-b border-reetik-border/30">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-xs text-reetik-gray-400 hover:text-white transition-colors mb-3"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Dashboard
          </button>
          <h2 className="font-semibold text-white text-sm leading-tight truncate">{project?.name}</h2>
          {project?.theme && (
            <p className="text-xs text-reetik-gray-500 mt-0.5 truncate">{project.theme}</p>
          )}
        </div>

        {/* Nav items */}
        <nav className="flex-1 p-3 space-y-1">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
                            transition-all duration-200 text-left relative
                            ${isActive
                              ? 'bg-reetik-gold/10 text-reetik-gold'
                              : 'text-reetik-gray-400 hover:text-white hover:bg-reetik-border/20'
                            }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="sidebar-indicator"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-reetik-gold rounded-full"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
                <tab.icon className="w-4 h-4 flex-shrink-0" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </aside>

      {/* ── Main content ── */}
      <main className="flex-1 min-w-0 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 lg:px-8 py-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25 }}
            >
              <TabContent projectId={id} project={project} onRefresh={loadProject} />
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  )
}
