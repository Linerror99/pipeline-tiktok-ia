import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Send, Sparkles, User, Loader2 } from 'lucide-react'

export default function ChatPanel({ messages, onSend, loading, placeholder = 'Votre message...' }) {
  const [input, setInput] = useState('')
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    onSend(input.trim())
    setInput('')
  }

  return (
    <div className="flex flex-col h-[500px] rounded-2xl border border-reetik-border/40 bg-reetik-card/40 overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-reetik-gray-500 text-sm">
            <div className="text-center">
              <Sparkles className="w-8 h-8 mx-auto mb-2 text-reetik-gold/30" />
              <p>Commencez la conversation avec l'IA</p>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-reetik-gold/10 border border-reetik-gold/20 
                              flex items-center justify-center flex-shrink-0 mt-1">
                <Sparkles className="w-3.5 h-3.5 text-reetik-gold" />
              </div>
            )}
            <div
              className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-reetik-gold/10 border border-reetik-gold/20 text-reetik-cream rounded-br-md'
                  : 'bg-reetik-dark border border-reetik-border/30 text-reetik-gray-200 rounded-bl-md'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-reetik-border/50 flex items-center justify-center flex-shrink-0 mt-1">
                <User className="w-3.5 h-3.5 text-reetik-gray-400" />
              </div>
            )}
          </motion.div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-reetik-gold/10 border border-reetik-gold/20 
                            flex items-center justify-center flex-shrink-0">
              <Sparkles className="w-3.5 h-3.5 text-reetik-gold animate-pulse" />
            </div>
            <div className="px-4 py-3 rounded-2xl rounded-bl-md bg-reetik-dark border border-reetik-border/30">
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-reetik-gray-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full bg-reetik-gray-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full bg-reetik-gray-500 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-reetik-border/30 p-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={placeholder}
          disabled={loading}
          className="flex-1 px-4 py-2.5 rounded-xl bg-reetik-dark border border-reetik-border
                     text-white text-sm placeholder-reetik-gray-500
                     focus:outline-none focus:border-reetik-gold/40
                     transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="p-2.5 rounded-xl bg-reetik-gold/10 border border-reetik-gold/20
                     text-reetik-gold hover:bg-reetik-gold/20
                     transition-colors disabled:opacity-30"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </form>
    </div>
  )
}
