import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { RevealOnScroll } from '../ui/Animations'

export default function CTA() {
  return (
    <section id="pricing" className="relative py-32 lg:py-40 overflow-hidden">
      {/* Background elements */}
      <div className="absolute inset-0 bg-gradient-radial from-reetik-gold/[0.03] via-transparent to-transparent" />
      <svg className="absolute bottom-0 right-0 w-[500px] h-[500px] opacity-[0.04]" viewBox="0 0 500 500">
        <circle cx="500" cy="500" r="250" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
        <circle cx="500" cy="500" r="350" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
        <circle cx="500" cy="500" r="450" stroke="#C9A96E" strokeWidth="0.5" fill="none" />
      </svg>

      <div className="relative max-w-4xl mx-auto px-6 text-center">
        <RevealOnScroll>
          <h2 className="font-serif text-hero text-reetik-cream text-balance">
            Prêt à créer ?
          </h2>
          <p className="mt-6 text-lg text-reetik-gray-300 max-w-xl mx-auto">
            Commencez à produire des TikToks viraux avec les meilleurs modèles IA de Google.
          </p>
        </RevealOnScroll>

        <RevealOnScroll delay={0.2}>
          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/login"
              className="group inline-flex items-center gap-3 px-8 py-4 rounded-full
                         border border-reetik-gold text-reetik-gold font-medium
                         transition-all duration-300
                         hover:bg-reetik-gold hover:text-reetik-black hover:shadow-gold-lg"
            >
              Commencer maintenant
              <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
            </Link>
            <a
              href="#features"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full
                         border border-reetik-border text-white font-medium
                         transition-all duration-300
                         hover:border-white/40 hover:bg-white/5"
            >
              En savoir plus
            </a>
          </div>
        </RevealOnScroll>
      </div>
    </section>
  )
}
