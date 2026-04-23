import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare, Upload, CheckCircle2, Clock, AlertCircle,
  Loader2, FileText, X
} from 'lucide-react'
import ChatPanel from './ChatPanel'
import { GoldButton, SecondaryButton } from '../ui/Buttons'
import { scenarioService } from '../../services/scenarios'
import { VALID_DURATIONS } from '../../config/api'

export default function ScenarioTab({ projectId }) {
  const [scenarios, setScenarios] = useState([])
  const [messages, setMessages] = useState([])
  const [scenarioId, setScenarioId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [chatLoading, setChatLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [validating, setValidating] = useState(null)
  const [selectedDuration, setSelectedDuration] = useState(22)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState(null)
  const fileRef = useRef(null)
  const restoredRef = useRef(false)

  const loadScenarios = useCallback(async () => {
    try {
      setLoading(true)
      const res = await scenarioService.list(projectId)
      const scens = res.scenarios || []
      setScenarios(scens)

      // Restaurer l'historique au premier chargement
      if (!restoredRef.current && scens.length > 0) {
        restoredRef.current = true
        const last = scens[scens.length - 1]
        setScenarioId(last.id)
        if (last.target_duration) setSelectedDuration(last.target_duration)
        const history = (last.chat_history || []).map((m) => ({
          role: m.role === 'model' ? 'assistant' : m.role,
          content: m.content,
        }))
        if (history.length > 0) setMessages(history)
      }
    } catch {
      setError('Erreur lors du chargement des scénarios')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => { loadScenarios() }, [loadScenarios])

  const handleChat = async (message) => {
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setChatLoading(true)
    setError(null)
    try {
      const payload = { project_id: projectId, message }
      if (scenarioId) payload.scenario_id = scenarioId

      const res = await scenarioService.chat(payload)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.ai_message }])

      if (res.scenario_id && !scenarioId) {
        setScenarioId(res.scenario_id)
        restoredRef.current = true
      }
      if (res.ready_to_validate) loadScenarios()
    } catch {
      setError('Erreur lors de la conversation')
    } finally {
      setChatLoading(false)
    }
  }

  const handleUpload = async (file) => {
    if (!file) return
    setUploading(true)
    setError(null)
    try {
      await scenarioService.upload(projectId, file)
      await loadScenarios()
    } catch {
      setError('Erreur lors de l\'upload du fichier')
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    const file = e.dataTransfer?.files?.[0]
    if (file) handleUpload(file)
  }

  const handleValidate = async (scenarioId) => {
    setValidating(scenarioId)
    setError(null)
    try {
      await scenarioService.validate(scenarioId, {
        scenario_id: scenarioId,
        project_id: projectId,
        target_duration: selectedDuration,
      })
      await loadScenarios()
    } catch {
      setError('Erreur lors de la validation')
    } finally {
      setValidating(null)
    }
  }

  const statusColors = {
    draft: 'text-yellow-400 bg-yellow-400/5 border-yellow-400/20',
    validated: 'text-emerald-400 bg-emerald-400/5 border-emerald-400/20',
    error: 'text-red-400 bg-red-400/5 border-red-400/20',
  }

  const statusIcons = {
    draft: Clock,
    validated: CheckCircle2,
    error: AlertCircle,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-reetik-gold" />
            Scénario
          </h3>
          <p className="text-sm text-reetik-gray-400 mt-1">
            Discutez avec l'IA ou uploadez un fichier pour créer votre scénario.
          </p>
        </div>

        {/* Duration selector */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-reetik-gray-400">Durée :</span>
          <select
            value={selectedDuration}
            onChange={(e) => setSelectedDuration(Number(e.target.value))}
            className="px-3 py-1.5 rounded-lg bg-reetik-dark border border-reetik-border text-white text-sm
                       focus:outline-none focus:border-reetik-gold/40"
          >
            {VALID_DURATIONS.map((d) => (
              <option key={d} value={d}>{d}s</option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/5 border border-red-400/20 rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1fr,320px]">
        {/* Chat */}
        <ChatPanel
          messages={messages}
          onSend={handleChat}
          loading={chatLoading}
          placeholder={`Décrivez votre scénario (durée : ${selectedDuration}s)...`}
        />

        {/* Upload & Scenarios sidebar */}
        <div className="space-y-4">
          {/* Upload zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-colors
              ${dragActive
                ? 'border-reetik-gold bg-reetik-gold/5'
                : 'border-reetik-border/40 hover:border-reetik-gold/30 bg-reetik-card/30'
              }`}
          >
            <input
              ref={fileRef}
              type="file"
              accept=".txt,.md,.json"
              className="hidden"
              onChange={(e) => handleUpload(e.target.files?.[0])}
            />
            {uploading ? (
              <Loader2 className="w-8 h-8 mx-auto text-reetik-gold animate-spin" />
            ) : (
              <>
                <Upload className="w-8 h-8 mx-auto text-reetik-gray-500 mb-2" />
                <p className="text-sm text-reetik-gray-400">
                  Glissez un fichier ou <span className="text-reetik-gold">parcourez</span>
                </p>
                <p className="text-xs text-reetik-gray-600 mt-1">.txt, .md, .json</p>
              </>
            )}
          </div>

          {/* Scenario list */}
          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-reetik-gold/60" />
            </div>
          ) : scenarios.length > 0 ? (
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-reetik-gray-300">Scénarios créés</h4>
              {scenarios.map((sc) => {
                const StatusIcon = statusIcons[sc.status] || Clock
                const colorClass = statusColors[sc.status] || statusColors.draft
                return (
                  <motion.div
                    key={sc.id}
                    layout
                    className="card-hover-glow rounded-xl p-4 space-y-2"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <FileText className="w-4 h-4 text-reetik-gold flex-shrink-0" />
                        <span className="text-sm font-medium text-white truncate">
                          {sc.title || `Scénario ${sc.id?.slice(0, 6)}`}
                        </span>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full border flex items-center gap-1 flex-shrink-0 ${colorClass}`}>
                        <StatusIcon className="w-3 h-3" />
                        {sc.status}
                      </span>
                    </div>

                    {sc.duration && (
                      <p className="text-xs text-reetik-gray-500">{sc.duration}s • {sc.clips_count || '?'} clips</p>
                    )}

                    {sc.status === 'draft' && (
                      <GoldButton
                        size="sm"
                        onClick={() => handleValidate(sc.id)}
                        loading={validating === sc.id}
                        className="w-full text-xs mt-1"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Valider le scénario
                      </GoldButton>
                    )}
                  </motion.div>
                )
              })}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
