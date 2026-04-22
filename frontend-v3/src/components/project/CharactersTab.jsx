import { useState, useEffect, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Users, Wand2, RefreshCw, ChevronDown, ChevronUp, Loader2, AlertCircle, Image } from 'lucide-react'
import ChatPanel from './ChatPanel'
import { GoldButton, SecondaryButton } from '../ui/Buttons'
import { characterService } from '../../services/characters'

export default function CharactersTab({ projectId }) {
  const [characters, setCharacters] = useState([])
  const [messages, setMessages] = useState([])
  const [characterId, setCharacterId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [chatLoading, setChatLoading] = useState(false)
  const [generating, setGenerating] = useState(null)
  const [expanded, setExpanded] = useState(null)
  const [error, setError] = useState(null)
  const restoredRef = useRef(false)

  const loadCharacters = useCallback(async () => {
    try {
      setLoading(true)
      const res = await characterService.list(projectId)
      const chars = res.characters || []
      setCharacters(chars)

      // Restaurer l'historique au premier chargement
      if (!restoredRef.current && chars.length > 0) {
        restoredRef.current = true
        // Prendre le dernier personnage créé (le plus récent)
        const lastChar = chars[chars.length - 1]
        setCharacterId(lastChar.id)
        const history = (lastChar.chat_history || []).map((m) => ({
          role: m.role === 'model' ? 'assistant' : m.role,
          content: m.content,
        }))
        if (history.length > 0) setMessages(history)
      }
    } catch {
      setError('Erreur lors du chargement des personnages')
    } finally {
      setLoading(false)
    }
  }, [projectId])

  useEffect(() => { loadCharacters() }, [loadCharacters])

  const handleChat = async (message) => {
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setChatLoading(true)
    setError(null)
    try {
      const payload = { project_id: projectId, message }
      if (characterId) payload.character_id = characterId

      const res = await characterService.chat(payload)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.ai_message }])

      // Mémoriser l'ID du personnage créé au premier message
      if (res.character_id && !characterId) {
        setCharacterId(res.character_id)
        restoredRef.current = true // évite l'écrasement des messages au prochain loadCharacters
      }

      if (res.ready_to_generate) loadCharacters()
    } catch {
      setError('Erreur lors de la conversation')
    } finally {
      setChatLoading(false)
    }
  }

  const handleGenerate = async (characterId) => {
    setGenerating(characterId)
    setError(null)
    try {
      await characterService.generate(projectId, characterId)
      await loadCharacters()
    } catch {
      setError('Erreur lors de la génération')
    } finally {
      setGenerating(null)
    }
  }

  const handleRegenerate = async (characterId) => {
    setGenerating(characterId)
    setError(null)
    try {
      await characterService.regenerate(projectId, characterId)
      await loadCharacters()
    } catch {
      setError('Erreur lors de la régénération')
    } finally {
      setGenerating(null)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-reetik-gold" />
            Personnages
          </h3>
          <p className="text-sm text-reetik-gray-400 mt-1">
            Discutez avec l'IA pour créer vos personnages, puis générez leurs images.
          </p>
        </div>
        <span className="text-sm text-reetik-gray-500">
          {characters.length} personnage{characters.length !== 1 ? 's' : ''}
        </span>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-400/5 border border-red-400/20 rounded-xl px-4 py-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Chat */}
      <ChatPanel
        messages={messages}
        onSend={handleChat}
        loading={chatLoading}
        placeholder="Décrivez vos personnages (ex: un héros aventurier, une vilaine sorcière...)"
      />

      {/* Character Cards */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-reetik-gold/60" />
        </div>
      ) : characters.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {characters.map((char) => (
            <motion.div
              key={char.id}
              layout
              className="card-hover-glow rounded-2xl p-4 space-y-3"
            >
              {/* Image or placeholder */}
              <div className="aspect-square rounded-xl overflow-hidden bg-reetik-dark border border-reetik-border/30">
                {char.image_url ? (
                  <img src={char.image_url} alt={char.name} className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-reetik-gray-500">
                    <Image className="w-10 h-10 mb-2 opacity-30" />
                    <span className="text-xs">Pas encore d'image</span>
                  </div>
                )}
              </div>

              {/* Info */}
              <div>
                <h4 className="font-semibold text-white text-sm">{char.name}</h4>
                {char.role && (
                  <span className="text-xs text-reetik-gold/80 bg-reetik-gold/5 border border-reetik-gold/10 
                                   px-2 py-0.5 rounded-full inline-block mt-1">
                    {char.role}
                  </span>
                )}
              </div>

              {/* Expandable description */}
              {char.description && (
                <div>
                  <button
                    onClick={() => setExpanded(expanded === char.id ? null : char.id)}
                    className="text-xs text-reetik-gray-400 hover:text-reetik-gray-300 flex items-center gap-1"
                  >
                    Détails
                    {expanded === char.id ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                  </button>
                  <AnimatePresence>
                    {expanded === char.id && (
                      <motion.p
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="text-xs text-reetik-gray-400 mt-2 leading-relaxed overflow-hidden"
                      >
                        {char.description}
                      </motion.p>
                    )}
                  </AnimatePresence>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2">
                {char.image_url ? (
                  <SecondaryButton
                    size="sm"
                    onClick={() => handleRegenerate(char.id)}
                    disabled={generating === char.id}
                    className="flex-1 text-xs"
                  >
                    {generating === char.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <RefreshCw className="w-3.5 h-3.5" />
                    )}
                    Régénérer
                  </SecondaryButton>
                ) : (
                  <GoldButton
                    size="sm"
                    onClick={() => handleGenerate(char.id)}
                    disabled={generating === char.id}
                    loading={generating === char.id}
                    className="flex-1 text-xs"
                  >
                    <Wand2 className="w-3.5 h-3.5" />
                    Générer l'image
                  </GoldButton>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        !loading && messages.length === 0 && (
          <div className="text-center py-12 text-reetik-gray-500">
            <Users className="w-12 h-12 mx-auto mb-3 opacity-20" />
            <p className="text-sm">Commencez par discuter avec l'IA pour créer vos personnages</p>
          </div>
        )
      )}
    </div>
  )
}
