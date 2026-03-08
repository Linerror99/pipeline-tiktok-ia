import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, FolderOpen, Clock, Film, Trash2, Loader2 } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { projectService } from '../services/projects'
import { RevealOnScroll, StaggerContainer, StaggerItem } from '../components/ui/Animations'

export default function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [showNew, setShowNew] = useState(false)
  const [newName, setNewName] = useState('')
  const [newTheme, setNewTheme] = useState('')

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const data = await projectService.list()
      setProjects(data)
    } catch (err) {
      console.error('Failed to load projects', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e) => {
    e.preventDefault()
    if (!newName.trim()) return
    setCreating(true)
    try {
      const project = await projectService.create({ name: newName.trim(), theme: newTheme.trim() || undefined })
      navigate(`/projects/${project.id}`)
    } catch (err) {
      console.error('Failed to create project', err)
    } finally {
      setCreating(false)
    }
  }

  const handleDelete = async (id) => {
    try {
      await projectService.remove(id)
      setProjects((prev) => prev.filter((p) => p.id !== id))
    } catch (err) {
      console.error('Delete failed', err)
    }
  }

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        {/* Header */}
        <RevealOnScroll>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-12">
            <div>
              <h1 className="font-serif text-heading text-reetik-cream">
                {user?.name ? `Bonjour, ${user.name.split(' ')[0]}` : 'Dashboard'}
              </h1>
              <p className="mt-1 text-sm text-reetik-gray-400">
                {projects.length} projet{projects.length !== 1 ? 's' : ''} en cours
              </p>
            </div>
            <button
              onClick={() => setShowNew(true)}
              className="group inline-flex items-center gap-2 px-6 py-3 rounded-full
                         border border-reetik-gold text-reetik-gold font-medium text-sm
                         transition-all duration-300
                         hover:bg-reetik-gold hover:text-reetik-black"
            >
              <Plus className="w-4 h-4" />
              Nouveau projet
            </button>
          </div>
        </RevealOnScroll>

        {/* New project form */}
        <AnimatePresence>
          {showNew && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden mb-8"
            >
              <form
                onSubmit={handleCreate}
                className="card-hover-glow rounded-2xl bg-reetik-card/60 p-6 flex flex-col sm:flex-row gap-4"
              >
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Nom du projet"
                  className="flex-1 px-4 py-3 rounded-xl bg-reetik-dark border border-reetik-border
                             text-white placeholder-reetik-gray-500
                             focus:outline-none focus:border-reetik-gold/50
                             transition-colors"
                  required
                  autoFocus
                />
                <input
                  type="text"
                  value={newTheme}
                  onChange={(e) => setNewTheme(e.target.value)}
                  placeholder="Thème (optionnel)"
                  className="flex-1 px-4 py-3 rounded-xl bg-reetik-dark border border-reetik-border
                             text-white placeholder-reetik-gray-500
                             focus:outline-none focus:border-reetik-gold/50
                             transition-colors"
                />
                <div className="flex gap-2">
                  <button
                    type="submit"
                    disabled={creating}
                    className="px-6 py-3 rounded-xl bg-reetik-gold text-reetik-black font-medium
                               hover:bg-reetik-gold-light transition-colors disabled:opacity-50"
                  >
                    {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Créer'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowNew(false)}
                    className="px-4 py-3 rounded-xl border border-reetik-border text-reetik-gray-400
                               hover:border-white/30 hover:text-white transition-colors"
                  >
                    Annuler
                  </button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Projects grid */}
        {loading ? (
          <div className="flex items-center justify-center py-32">
            <Loader2 className="w-8 h-8 text-reetik-gold animate-spin" />
          </div>
        ) : projects.length === 0 ? (
          <RevealOnScroll>
            <div className="text-center py-32">
              <FolderOpen className="w-16 h-16 text-reetik-gray-600 mx-auto mb-4" />
              <h3 className="text-xl text-reetik-gray-300 font-serif">Aucun projet</h3>
              <p className="mt-2 text-sm text-reetik-gray-500">
                Créez votre premier projet pour commencer.
              </p>
            </div>
          </RevealOnScroll>
        ) : (
          <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" staggerDelay={0.08}>
            {projects.map((project) => (
              <StaggerItem key={project.id}>
                <Link
                  to={`/projects/${project.id}`}
                  className="block group card-hover-glow rounded-2xl bg-reetik-card/50 p-6 h-full"
                >
                  {/* Color accent bar */}
                  <div className="h-1 w-12 rounded-full bg-reetik-gold/40 mb-5 
                                  group-hover:w-20 group-hover:bg-reetik-gold
                                  transition-all duration-500" />

                  <h3 className="text-lg font-medium text-white group-hover:text-reetik-gold transition-colors duration-300">
                    {project.name}
                  </h3>
                  {project.theme && (
                    <p className="mt-1 text-sm text-reetik-gray-400">{project.theme}</p>
                  )}

                  <div className="mt-6 flex items-center justify-between">
                    <div className="flex items-center gap-4 text-xs text-reetik-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        {project.created_at
                          ? new Date(project.created_at).toLocaleDateString('fr-FR')
                          : '—'}
                      </span>
                      {project.video_count > 0 && (
                        <span className="flex items-center gap-1">
                          <Film className="w-3.5 h-3.5" />
                          {project.video_count}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        handleDelete(project.id)
                      }}
                      className="p-1.5 rounded-lg text-reetik-gray-600 
                                 hover:text-red-400 hover:bg-red-500/10
                                 transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </Link>
              </StaggerItem>
            ))}
          </StaggerContainer>
        )}
      </div>
    </div>
  )
}
