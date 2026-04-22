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

  useEffect(() => {
    loadProject()
  }, [loadProject])

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
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Back + Title */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-sm text-reetik-gray-400 hover:text-white transition-colors mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Dashboard
          </button>
          <h1 className="font-serif text-heading text-reetik-cream">{project?.name}</h1>
          {project?.theme && (
            <p className="mt-1 text-sm text-reetik-gray-400">{project.theme}</p>
          )}
        </div>

        {/* Tabs */}
        <div className="border-b border-reetik-border/40 mb-8">
          <div className="flex gap-1 overflow-x-auto">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative flex items-center gap-2 px-5 py-3 text-sm font-medium
                            transition-colors duration-300 whitespace-nowrap
                            ${activeTab === tab.id
                              ? 'text-reetik-gold'
                              : 'text-reetik-gray-400 hover:text-white'
                            }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
                {activeTab === tab.id && (
                  <motion.div
                    layoutId="tab-indicator"
                    className="absolute bottom-0 left-0 right-0 h-0.5 bg-reetik-gold rounded-full"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Tab content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            <TabContent projectId={id} project={project} onRefresh={loadProject} />
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  )
}
