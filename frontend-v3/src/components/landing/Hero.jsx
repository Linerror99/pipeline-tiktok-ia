import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Play, Sparkles } from 'lucide-react'

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background: grid + radial gradient */}
      <div className="absolute inset-0 grid-lines opacity-40" />
      <div className="absolute inset-0 bg-gradient-radial from-reetik-gold/[0.03] via-transparent to-transparent" />

      {/* Decorative arcs (like ROX curved lines) */}
      <svg className="absolute bottom-0 left-0 w-[600px] h-[600px] opacity-[0.06]" viewBox="0 0 600 600">
        <circle cx="0" cy="600" r="300" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
        <circle cx="0" cy="600" r="400" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
        <circle cx="0" cy="600" r="500" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
      </svg>
      <svg className="absolute top-0 right-0 w-[400px] h-[400px] opacity-[0.04]" viewBox="0 0 400 400">
        <circle cx="400" cy="0" r="200" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
        <circle cx="400" cy="0" r="300" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
      </svg>

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center pt-24">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full 
                     border border-reetik-gold/30 bg-reetik-gold/[0.05] mb-8"
        >
          <Sparkles className="w-3.5 h-3.5 text-reetik-gold" />
          <span className="text-xs font-medium text-reetik-gold tracking-wider uppercase">
            Propulsé par Veo 3.1 & Gemini
          </span>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          className="font-serif text-hero text-reetik-cream text-balance"
        >
          Créez des TikToks{' '}
          <span className="text-gold-gradient italic">viraux</span>
          <br />
          avec l'IA générative.
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="mt-6 text-lg text-reetik-gray-300 max-w-2xl mx-auto leading-relaxed"
        >
          Des personnages uniques aux vidéos de 57 secondes sans coupure.
          Reetik transforme vos idées en contenu viral prêt à publier.
        </motion.p>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.7 }}
          className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            to="/login"
            className="group inline-flex items-center gap-3 px-8 py-4 rounded-full
                       border border-reetik-gold text-reetik-gold font-medium
                       transition-all duration-300
                       hover:bg-reetik-gold hover:text-reetik-black hover:shadow-gold"
          >
            Commencer gratuitement
            <span className="text-lg transition-transform duration-300 group-hover:translate-x-1">›</span>
          </Link>
          <a
            href="#how-it-works"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-full
                       border border-reetik-border text-white font-medium
                       transition-all duration-300
                       hover:border-white/40 hover:bg-white/5"
          >
            <Play className="w-4 h-4" />
            Voir comment ça marche
          </a>
        </motion.div>

        {/* Floating mockup / preview */}
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.9 }}
          className="mt-20 relative"
        >
          <div className="relative mx-auto max-w-4xl rounded-2xl border border-reetik-border/60 
                          bg-reetik-dark/80 backdrop-blur-sm p-1 shadow-2xl">
            {/* Browser chrome */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-reetik-border/40">
              <div className="flex gap-1.5">
                <span className="w-3 h-3 rounded-full bg-red-500/60" />
                <span className="w-3 h-3 rounded-full bg-yellow-500/60" />
                <span className="w-3 h-3 rounded-full bg-green-500/60" />
              </div>
              <div className="flex-1 mx-4">
                <div className="max-w-sm mx-auto h-6 rounded-md bg-reetik-card flex items-center px-3">
                  <span className="text-[10px] text-reetik-gray-500">reetik.app/dashboard</span>
                </div>
              </div>
            </div>

            {/* App preview */}
            <div className="aspect-[16/9] rounded-b-xl overflow-hidden bg-reetik-black p-6">
              <div className="grid grid-cols-3 gap-4 h-full">
                {/* Left: Chat panel */}
                <div className="col-span-1 bg-reetik-card rounded-xl p-4 border border-reetik-border/30">
                  <div className="flex items-center gap-2 mb-4">
                    <div className="w-8 h-8 rounded-full bg-reetik-gold/20 flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-reetik-gold" />
                    </div>
                    <div>
                      <div className="h-2.5 w-16 bg-reetik-gray-600 rounded" />
                      <div className="h-2 w-10 bg-reetik-gray-700 rounded mt-1" />
                    </div>
                  </div>
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className={`mb-3 p-3 rounded-lg ${i % 2 === 0 ? 'bg-reetik-gold/10 ml-4' : 'bg-reetik-border/30 mr-4'}`}>
                      <div className="h-2 w-full bg-reetik-gray-600/40 rounded" />
                      <div className="h-2 w-3/4 bg-reetik-gray-600/30 rounded mt-1.5" />
                    </div>
                  ))}
                </div>

                {/* Center: Video preview */}
                <div className="col-span-1 bg-reetik-card rounded-xl border border-reetik-border/30 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 rounded-full bg-reetik-gold/10 border border-reetik-gold/30 mx-auto flex items-center justify-center mb-3">
                      <Play className="w-6 h-6 text-reetik-gold" />
                    </div>
                    <div className="h-2 w-20 bg-reetik-gray-700 rounded mx-auto" />
                  </div>
                </div>

                {/* Right: Timeline */}
                <div className="col-span-1 bg-reetik-card rounded-xl p-4 border border-reetik-border/30">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="flex items-center gap-3 mb-3">
                      <div className={`w-10 h-10 rounded-lg flex-shrink-0 ${i <= 2 ? 'bg-reetik-gold/20' : 'bg-reetik-gray-700'}`} />
                      <div className="flex-1">
                        <div className="h-2 w-full bg-reetik-gray-600/40 rounded" />
                        <div className="h-1.5 w-2/3 bg-reetik-gray-700/30 rounded mt-1.5" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Glow effect under mockup */}
          <div className="absolute -bottom-20 left-1/2 -translate-x-1/2 w-[80%] h-40 
                          bg-reetik-gold/[0.05] blur-[80px] rounded-full" />
        </motion.div>
      </div>

      {/* Bottom fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-reetik-black to-transparent" />
    </section>
  )
}
