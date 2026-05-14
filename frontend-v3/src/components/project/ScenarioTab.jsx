import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare, Upload, CheckCircle2, Clock, AlertCircle,
  Loader2, FileText, ArrowLeft, Plus, Users, Trash2,
} from 'lucide-react'
import ChatPanel from './ChatPanel'
import { GoldButton, SecondaryButton } from '../ui/Buttons'
import { scenarioService } from '../../services/scenarios'
import { characterService } from '../../services/characters'
import { VALID_DURATIONS } from '../../config/api'

// ── Carte scénario ──────────────────────────────────────────────────────────
function ScenarioCard({ scenario, onSelect, onValidate, validating, onDelete }) {
  const isValidated = scenario.status === 'validated'
  const statusCfg = {
    validated: { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-400/5 border-emerald-400/20' },
    draft: { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-400/5 border-yellow-400/20' },
    error: { icon: AlertCircle, color: 'text-red-400', bg: 'bg-red-400/5 border-red-400/20' },
  }
  const cfg = statusCfg[scenario.status] || statusCfg.draft
  const StatusIcon = cfg.icon

  return (
    <motion.div
      layout
      className="card-hover-glow rounded-2xl p-4 space-y-3 cursor-pointer"
      onClick={() => onSelect(scenario)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <FileText className="w-4 h-4 text-reetik-gold flex-shrink-0" />
          <span className="text-sm font-semibold text-white truncate">
            {scenario.title || `Scénario ${scenario.id?.slice(0, 6)}`}
          </span>
        </div>
        <span className={`text-xs px-2 py-0.5 rounded-full border flex items-center gap-1 flex-shrink-0 ${cfg.bg}`}>
          <StatusIcon className={`w-3 h-3 ${cfg.color}`} />
          <span className={cfg.color}>{scenario.status}</span>
        </span>
      </div>

      {scenario.target_duration && (
        <p className="text-xs text-reetik-gray-500">{scenario.target_duration}s</p>
      )}

      {!isValidated && (
        <div onClick={(e) => e.stopPropagation()}>
          <GoldButton
            size="sm"
            onClick={() => onValidate(scenario)}
            loading={validating === scenario.id}
            className="w-full text-xs"
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            Valider
          </GoldButton>
        </div>
      )}

      {/* Delete */}
      <div className="flex justify-end" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={() => onDelete(scenario.id)}
          className="p-1.5 rounded-lg text-reetik-gray-600
                     hover:text-red-400 hover:bg-red-500/10
                     transition-colors"
          title="Supprimer le scénario"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
    </motion.div>
  )
}

// ── Chat scénario individuel ────────────────────────────────────────────────
function ScenarioChat({ projectId, scenario, characters = [], onBack, onUpdate }) {
  const [messages, setMessages] = useState([])
  const [chatLoading, setChatLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [validating, setValidating] = useState(false)
  const [selectedDuration, setSelectedDuration] = useState(scenario?.target_duration || 22)
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState(null)
  // Personnages sélectionnés pour la vidéo (ceux avec une image par défaut)
  const [selectedCharIds, setSelectedCharIds] = useState([])
  const fileRef = useRef(null)
  const scenarioIdRef = useRef(scenario?.id || null)

  useEffect(() => {
    if (scenario?.chat_history?.length) {
      setMessages(
        scenario.chat_history.map((m) => ({
          role: m.role === 'model' ? 'assistant' : m.role,
          content: m.content,
        }))
      )
    } else {
      setMessages([])
    }
    scenarioIdRef.current = scenario?.id || null
    if (scenario?.target_duration) setSelectedDuration(scenario.target_duration)
  }, [scenario?.id])

  // Pré-sélectionner les personnages avec une image
  useEffect(() => {
    const withImage = characters.filter((c) => c.image_url || c.gcs_path).map((c) => c.id)
    setSelectedCharIds(withImage)
  }, [characters])

  const toggleChar = (id) => {
    setSelectedCharIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    )
  }

  const handleChat = async (message) => {
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setChatLoading(true)
    setError(null)
    try {
      const payload = { project_id: projectId, message, character_ids: selectedCharIds }
      if (scenarioIdRef.current) payload.scenario_id = scenarioIdRef.current

      const res = await scenarioService.chat(payload)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.ai_message }])

      if (res.scenario_id && !scenarioIdRef.current) scenarioIdRef.current = res.scenario_id
      if (res.ready_to_validate) onUpdate()
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
      onUpdate()
    } catch {
      setError("Erreur lors de l'upload")
    } finally {
      setUploading(false)
    }
  }

  const handleValidate = async () => {
    setValidating(true)
    setError(null)
    try {
      await scenarioService.validate(scenarioIdRef.current, {
        scenario_id: scenarioIdRef.current,
        project_id: projectId,
        target_duration: selectedDuration,
        character_ids: selectedCharIds,
      })
      onUpdate()
    } catch {
      setError('Erreur lors de la validation')
    } finally {
      setValidating(false)
    }
  }

  const showValidate = !!scenarioIdRef.current && scenario?.status !== 'validated'

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3 flex-wrap">
        <button
          onClick={onBack}
          className="p-2 rounded-xl hover:bg-reetik-border/20 text-reetik-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>
        <MessageSquare className="w-5 h-5 text-reetik-gold" />
        <h3 className="font-semibold text-white text-sm flex-1 truncate">
          {scenario ? scenario.title || `Scénario ${scenario.id?.slice(0, 6)}` : 'Nouveau scénario'}
        </h3>

        {/* Duration */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-reetik-gray-400">Durée :</span>
          <select
            value={selectedDuration}
            onChange={(e) => setSelectedDuration(Number(e.target.value))}
            className="px-2 py-1 rounded-lg bg-reetik-dark border border-reetik-border text-white text-sm
                       focus:outline-none focus:border-reetik-gold/40"
          >
            {VALID_DURATIONS.map((d) => <option key={d} value={d}>{d}s</option>)}
          </select>
        </div>

        {showValidate && (
          <GoldButton size="sm" onClick={handleValidate} loading={validating}>
            <CheckCircle2 className="w-3.5 h-3.5" />
            Valider
          </GoldButton>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/5 border border-red-400/20 rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-[1fr,280px]">
        {/* Chat */}
        <ChatPanel
          messages={messages}
          onSend={handleChat}
          loading={chatLoading}
          placeholder={`Décrivez votre scénario pour ${selectedDuration}s...`}
        />

        {/* Panneau droit : upload + personnages */}
        <div className="space-y-3">
          {/* Sélection des personnages */}
          {characters.length > 0 && (
            <div className="rounded-2xl border border-reetik-border/40 bg-reetik-card/30 p-4 space-y-2">
              <p className="text-xs font-semibold text-reetik-gray-400 uppercase tracking-wide flex items-center gap-1">
                <Users className="w-3.5 h-3.5" />
                Personnages
              </p>
              {characters.map((c) => {
                const checked = selectedCharIds.includes(c.id)
                const hasImage = !!(c.image_url || c.gcs_path)
                return (
                  <button
                    key={c.id}
                    onClick={() => toggleChar(c.id)}
                    className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-left text-xs transition-colors
                      ${checked
                        ? 'bg-reetik-gold/10 border border-reetik-gold/30 text-white'
                        : 'bg-reetik-dark/50 border border-reetik-border/20 text-reetik-gray-400 hover:border-reetik-border/40'}`}
                  >
                    {c.image_url
                      ? <img src={c.image_url} alt={c.name} className="w-6 h-6 rounded-full object-cover flex-shrink-0" />
                      : <div className="w-6 h-6 rounded-full bg-reetik-border/40 flex-shrink-0" />}
                    <span className="truncate flex-1">{c.name || c.id?.slice(0, 8)}</span>
                    {!hasImage && (
                      <span className="text-yellow-500/60 text-[10px] flex-shrink-0">sans image</span>
                    )}
                    {checked && <CheckCircle2 className="w-3.5 h-3.5 text-reetik-gold flex-shrink-0" />}
                  </button>
                )
              })}
            </div>
          )}

          {/* Upload */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
            onDragLeave={() => setDragActive(false)}
            onDrop={(e) => { e.preventDefault(); setDragActive(false); handleUpload(e.dataTransfer?.files?.[0]) }}
            onClick={() => fileRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-colors
              ${dragActive
                ? 'border-reetik-gold bg-reetik-gold/5'
                : 'border-reetik-border/40 hover:border-reetik-gold/30 bg-reetik-card/30'}`}
          >
            <input
              ref={fileRef}
              type="file"
              accept=".txt,.md,.json"
              className="hidden"
              onChange={(e) => handleUpload(e.target.files?.[0])}
            />
            {uploading
              ? <Loader2 className="w-8 h-8 mx-auto text-reetik-gold animate-spin" />
              : (
                <>
                  <Upload className="w-8 h-8 mx-auto text-reetik-gray-500 mb-2" />
                  <p className="text-sm text-reetik-gray-400">
                    Glissez un fichier ou <span className="text-reetik-gold">parcourez</span>
                  </p>
                  <p className="text-xs text-reetik-gray-600 mt-1">.txt, .md, .json</p>
                </>
              )
            }
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Export principal ────────────────────────────────────────────────────────
export default function ScenarioTab({ projectId }) {
  const [scenarios, setScenarios] = useState([])
  const [characters, setCharacters] = useState([])
  const [readyChars, setReadyChars] = useState(0)
  const [loading, setLoading] = useState(true)
  const [validating, setValidating] = useState(null)
  const [error, setError] = useState(null)
  // null = liste, undefined = nouveau, object = scénario sélectionné
  const [selectedScenario, setSelectedScenario] = useState(null)
  const [selectedDurationForValidate, setSelectedDurationForValidate] = useState(22)

  const loadData = useCallback(async () => {
    try {
      setLoading(true)
      const [scenRes, charRes] = await Promise.all([
        scenarioService.list(projectId),
        characterService.list(projectId),
      ])
      setScenarios(scenRes.scenarios || [])
      const chars = charRes.characters || []
      setCharacters(chars)
      const ready = chars.filter((c) => c.status === 'ready' || c.image_url).length
      setReadyChars(ready)
    } catch {
      setError('Erreur lors du chargement')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => { loadData() }, [loadData])

  const handleValidate = async (scenario) => {
    setValidating(scenario.id)
    setError(null)
    try {
      await scenarioService.validate(scenario.id, {
        scenario_id: scenario.id,
        project_id: projectId,
        target_duration: scenario.target_duration || selectedDurationForValidate,
      })
      await loadData()
    } catch {
      setError('Erreur lors de la validation')
    } finally {
      setValidating(null)
    }
  }

  const handleDelete = async (scenarioId) => {
    try {
      await scenarioService.remove(scenarioId)
      setScenarios((prev) => prev.filter((s) => s.id !== scenarioId))
    } catch {
      setError('Erreur lors de la suppression')
    }
  }

  // ── Vue chat ──
  if (selectedScenario !== null) {
    const sc = selectedScenario === undefined ? null : selectedScenario
    return (
      <ScenarioChat
        projectId={projectId}
        scenario={sc}
        characters={characters}
        onBack={async () => { await loadData(); setSelectedScenario(null) }}
        onUpdate={async () => { await loadData(); setSelectedScenario(null) }}
      />
    )
  }

  // ── Garde : au moins 1 personnage ready ──
  if (!loading && readyChars === 0) {
    return (
      <div className="text-center py-16 text-reetik-gray-500">
        <Users className="w-14 h-14 mx-auto mb-4 opacity-20" />
        <p className="text-sm font-medium text-white mb-2">Personnage requis</p>
        <p className="text-xs">Créez et générez l'image d'au moins un personnage avant de créer un scénario.</p>
      </div>
    )
  }

  // ── Vue liste ──
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-reetik-gold" />
            Scénarios
          </h3>
          <p className="text-sm text-reetik-gray-400 mt-1">
            Créez et validez vos scénarios pour la génération vidéo.
          </p>
        </div>
        <GoldButton size="sm" onClick={() => setSelectedScenario(undefined)}>
          <Plus className="w-4 h-4" />
          Nouveau
        </GoldButton>
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
      ) : scenarios.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {scenarios.map((sc) => (
            <ScenarioCard
              key={sc.id}
              scenario={sc}
              onSelect={setSelectedScenario}
              onValidate={handleValidate}
              validating={validating}
              onDelete={handleDelete}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 text-reetik-gray-500">
          <MessageSquare className="w-14 h-14 mx-auto mb-4 opacity-20" />
          <p className="text-sm mb-4">Aucun scénario pour l'instant</p>
          <GoldButton size="sm" onClick={() => setSelectedScenario(undefined)}>
            <Plus className="w-4 h-4" />
            Créer le premier scénario
          </GoldButton>
        </div>
      )}
    </div>
  )
}
