import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Users, Wand2, RefreshCw, Loader2, AlertCircle, Image,
  ArrowLeft, Plus, CheckCircle2, Clock, Trash2,
} from 'lucide-react'
import ChatPanel from './ChatPanel'
import { GoldButton, SecondaryButton } from '../ui/Buttons'
import { characterService } from '../../services/characters'

// ── Vue liste ──────────────────────────────────────────────────────────────
function CharacterCard({ char, onSelect, generating, onGenerate, onRegenerate, onDelete }) {
  const isReady = char.status === 'ready' || !!char.image_url

  return (
    <motion.div
      layout
      className="card-hover-glow rounded-2xl overflow-hidden cursor-pointer group"
      onClick={() => onSelect(char)}
    >
      {/* Image */}
      <div className="aspect-square bg-reetik-dark border-b border-reetik-border/20 relative">
        {char.image_url ? (
          <img src={char.image_url} alt={char.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center text-reetik-gray-500">
            <Image className="w-10 h-10 mb-2 opacity-30" />
            <span className="text-xs">Pas d'image</span>
          </div>
        )}
        {/* Status badge */}
        <div className={`absolute top-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-full text-xs border
          ${isReady
            ? 'bg-emerald-400/10 border-emerald-400/20 text-emerald-400'
            : 'bg-yellow-400/10 border-yellow-400/20 text-yellow-400'}`}
        >
          {isReady ? <CheckCircle2 className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
          {isReady ? 'Prêt' : 'Brouillon'}
        </div>
      </div>

      {/* Info */}
      <div className="p-3 space-y-2">
        <div>
          <h4 className="font-semibold text-white text-sm truncate">{char.name || 'Nouveau personnage'}</h4>
          {char.role && (
            <span className="text-xs text-reetik-gold/80 bg-reetik-gold/5 border border-reetik-gold/10
                             px-2 py-0.5 rounded-full inline-block mt-0.5">
              {char.role}
            </span>
          )}
        </div>

        {/* Action */}
        <div onClick={(e) => e.stopPropagation()}>
          {char.image_url ? (
            <SecondaryButton size="sm" onClick={() => onRegenerate(char.id)}
              disabled={generating === char.id} className="w-full text-xs">
              {generating === char.id
                ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                : <RefreshCw className="w-3.5 h-3.5" />}
              Régénérer image
            </SecondaryButton>
          ) : (
            <GoldButton size="sm" onClick={() => onGenerate(char.id)}
              disabled={generating === char.id} loading={generating === char.id}
              className="w-full text-xs">
              <Wand2 className="w-3.5 h-3.5" />
              Générer image
            </GoldButton>
          )}
        </div>

        {/* Delete */}
        <div className="flex justify-end" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => onDelete(char.id)}
            className="p-1.5 rounded-lg text-reetik-gray-600
                       hover:text-red-400 hover:bg-red-500/10
                       transition-colors"
            title="Supprimer le personnage"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}

// ── Vue chat individuel ────────────────────────────────────────────────────
function CharacterChat({ projectId, character, onBack, onUpdate }) {
  const [messages, setMessages] = useState([])
  const [loading, setChatLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState(null)
  const characterIdRef = useRef(character?.id || null)

  // Restaurer historique depuis le personnage
  useEffect(() => {
    if (character?.chat_history?.length) {
      setMessages(
        character.chat_history.map((m) => ({
          role: m.role === 'model' ? 'assistant' : m.role,
          content: m.content,
        }))
      )
    } else {
      setMessages([])
    }
    characterIdRef.current = character?.id || null
  }, [character?.id])

  const handleChat = async (message) => {
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setChatLoading(true)
    setError(null)
    try {
      const payload = { project_id: projectId, message }
      if (characterIdRef.current) payload.character_id = characterIdRef.current

      const res = await characterService.chat(payload)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.ai_message }])

      if (res.character_id && !characterIdRef.current) {
        characterIdRef.current = res.character_id
      }
      if (res.ready_to_generate) onUpdate()
    } catch {
      setError('Erreur lors de la conversation')
    } finally {
      setChatLoading(false)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    setError(null)
    try {
      await characterService.generate(projectId, characterIdRef.current)
      onUpdate()
    } catch {
      setError('Erreur lors de la génération')
    } finally {
      setGenerating(false)
    }
  }

  const handleRegenerate = async () => {
    setGenerating(true)
    setError(null)
    try {
      await characterService.regenerate(projectId, characterIdRef.current)
      onUpdate()
    } catch {
      setError('Erreur lors de la régénération')
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          className="p-2 rounded-xl hover:bg-reetik-border/20 text-reetik-gray-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>
        {character?.image_url ? (
          <img src={character.image_url} alt={character.name}
            className="w-9 h-9 rounded-xl object-cover border border-reetik-border/30" />
        ) : (
          <div className="w-9 h-9 rounded-xl bg-reetik-dark border border-reetik-border/30
                           flex items-center justify-center">
            <Users className="w-4 h-4 text-reetik-gray-500" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white text-sm truncate">
            {character ? character.name || 'Nouveau personnage' : 'Créer un personnage'}
          </h3>
          {character?.role && (
            <p className="text-xs text-reetik-gray-500 truncate">{character.role}</p>
          )}
        </div>

        {/* Generate / Regenerate button */}
        {characterIdRef.current && (
          <div>
            {character?.image_url ? (
              <SecondaryButton size="sm" onClick={handleRegenerate} disabled={generating}>
                {generating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
                Régénérer
              </SecondaryButton>
            ) : (
              <GoldButton size="sm" onClick={handleGenerate} disabled={generating} loading={generating}>
                <Wand2 className="w-3.5 h-3.5" />
                Image
              </GoldButton>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/5 border border-red-400/20 rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      <ChatPanel
        messages={messages}
        onSend={handleChat}
        loading={loading}
        placeholder="Décrivez votre personnage (apparence, personnalité, rôle...)..."
      />
    </div>
  )
}

// ── Export principal ───────────────────────────────────────────────────────
export default function CharactersTab({ projectId }) {
  const [characters, setCharacters] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(null)
  const [error, setError] = useState(null)
  // null = liste, undefined = nouveau chat, object = chat pour ce personnage
  const [selectedChar, setSelectedChar] = useState(null)

  const loadCharacters = useCallback(async () => {
    try {
      setLoading(true)
      const res = await characterService.list(projectId)
      setCharacters(res.characters || [])
    } catch {
      setError('Erreur lors du chargement des personnages')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => { loadCharacters() }, [loadCharacters])

  const handleGenerate = async (charId) => {
    setGenerating(charId)
    setError(null)
    try {
      await characterService.generate(projectId, charId)
      await loadCharacters()
    } catch {
      setError('Erreur lors de la génération')
    } finally {
      setGenerating(null)
    }
  }

  const handleRegenerate = async (charId) => {
    setGenerating(charId)
    setError(null)
    try {
      await characterService.regenerate(projectId, charId)
      await loadCharacters()
    } catch {
      setError('Erreur lors de la régénération')
    } finally {
      setGenerating(null)
    }
  }

  const handleDelete = async (charId) => {
    try {
      await characterService.remove(charId)
      setCharacters((prev) => prev.filter((c) => c.id !== charId))
    } catch {
      setError('Erreur lors de la suppression')
    }
  }

  const handleUpdate = useCallback(async () => {
    await loadCharacters()
    // Mettre à jour le personnage sélectionné avec les données fraîches
    setSelectedChar((prev) => {
      if (!prev) return prev
      return undefined // retour liste après update automatique (image générée)
    })
    await loadCharacters()
  }, [loadCharacters])

  // ── Vue chat ──
  if (selectedChar !== null) {
    // selectedChar = undefined => nouveau personnage, object => existant
    const char = selectedChar === undefined ? null : selectedChar
    return (
      <CharacterChat
        projectId={projectId}
        character={char}
        onBack={async () => {
          await loadCharacters()
          setSelectedChar(null)
        }}
        onUpdate={async () => {
          await loadCharacters()
          setSelectedChar(null)
        }}
      />
    )
  }

  // ── Vue liste ──
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-reetik-gold" />
            Personnages
          </h3>
          <p className="text-sm text-reetik-gray-400 mt-1">
            Créez vos personnages et générez leurs images via l'IA.
          </p>
        </div>
        <GoldButton size="sm" onClick={() => setSelectedChar(undefined)}>
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
      ) : characters.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {characters.map((char) => (
            <CharacterCard
              key={char.id}
              char={char}
              onSelect={setSelectedChar}
              generating={generating}
              onGenerate={handleGenerate}
              onRegenerate={handleRegenerate}
              onDelete={handleDelete}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 text-reetik-gray-500">
          <Users className="w-14 h-14 mx-auto mb-4 opacity-20" />
          <p className="text-sm mb-4">Aucun personnage pour l'instant</p>
          <GoldButton size="sm" onClick={() => setSelectedChar(undefined)}>
            <Plus className="w-4 h-4" />
            Créer le premier personnage
          </GoldButton>
        </div>
      )}
    </div>
  )
}
