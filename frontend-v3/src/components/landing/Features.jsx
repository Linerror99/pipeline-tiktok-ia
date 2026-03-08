import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown, Users, MessageSquare, Film, Hash, Image } from 'lucide-react'
import { RevealOnScroll, StaggerContainer, StaggerItem } from '../ui/Animations'

const FEATURES = [
  {
    icon: Users,
    title: 'Personnages IA uniques',
    subtitle: 'Imagen 4',
    description:
      'Créez des personnages par conversation naturelle. Décrivez leur style, personnalité, couleurs — l\'IA génère un portrait réaliste en 9:16 avec Imagen 4.',
    details: [
      'Chat IA pour définir les traits du personnage',
      'Génération d\'image haute qualité 9:16',
      'Jusqu\'à 4 variations par génération',
      'Régénération illimitée',
    ],
  },
  {
    icon: MessageSquare,
    title: 'Scénarios conversationnels',
    subtitle: 'Gemini 3.1 Pro',
    description:
      'Construisez votre script TikTok en discutant avec Gemini. Uploadez des références, intégrez vos personnages, et validez un scénario structuré automatiquement.',
    details: [
      'Chat IA contextuel avec vos personnages',
      'Upload de fichiers (texte, images, PDF)',
      'Génération automatique du script JSON',
      'Choix de durée : 8s à 57s',
    ],
  },
  {
    icon: Film,
    title: 'Vidéos continues sans coupure',
    subtitle: 'Veo 3.1 Extensions',
    description:
      'Fini les clips collés avec des coupures audio. Veo 3.1 génère une vidéo initiale de 8s puis l\'étend séquentiellement jusqu\'à 57 secondes, en continu.',
    details: [
      'Vidéo initiale 8s + extensions de 7s',
      'Audio continu sans coupure',
      'Durées : 8 / 15 / 22 / 29 / 36 / 43 / 50 / 57s',
      'Suivi en temps réel via WebSocket',
    ],
  },
  {
    icon: Hash,
    title: 'Assistant TikTok IA',
    subtitle: 'Gemini 3.1 Pro',
    description:
      'Obtenez des suggestions de profil, hashtags tendance et titres accrocheurs générés par Gemini pour maximiser la viralité de vos vidéos.',
    details: [
      'Suggestions de profil optimisé',
      'Hashtags trending + niche',
      '5 titres avec hook types variés',
      'Adapté à votre cible et thème',
    ],
  },
  {
    icon: Image,
    title: 'Miniatures automatiques',
    subtitle: 'Imagen 4',
    description:
      'Une miniature 9:16 est automatiquement générée quand votre vidéo est prête. Basée sur le scénario et les personnages pour un maximum de cohérence.',
    details: [
      'Génération automatique à la fin de la vidéo',
      'Format 9:16 optimisé TikTok',
      'Basée sur le contexte du scénario',
      'Fallback intelligent si le premier prompt échoue',
    ],
  },
]

function FeatureAccordion({ feature, isOpen, onClick, index }) {
  return (
    <motion.div
      layout
      className={`border-b border-reetik-border/40 transition-colors duration-300 ${
        isOpen ? 'bg-reetik-card/30' : ''
      }`}
    >
      <button
        onClick={onClick}
        className="w-full flex items-center gap-6 py-6 px-6 text-left group"
      >
        <span className="text-xs text-reetik-gray-500 font-mono w-6">
          {String(index + 1).padStart(2, '0')}
        </span>
        <feature.icon className={`w-5 h-5 flex-shrink-0 transition-colors duration-300 ${
          isOpen ? 'text-reetik-gold' : 'text-reetik-gray-400 group-hover:text-reetik-gold'
        }`} />
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h3 className={`text-lg font-medium transition-colors duration-300 ${
              isOpen ? 'text-white' : 'text-reetik-gray-200 group-hover:text-white'
            }`}>
              {feature.title}
            </h3>
            <span className="text-[10px] uppercase tracking-wider text-reetik-gold/60 bg-reetik-gold/[0.06] 
                             px-2.5 py-0.5 rounded-full border border-reetik-gold/10">
              {feature.subtitle}
            </span>
          </div>
        </div>
        <ChevronDown className={`w-4 h-4 text-reetik-gray-500 transition-transform duration-300 ${
          isOpen ? 'rotate-180 text-reetik-gold' : ''
        }`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-6 pl-[4.5rem]">
              <p className="text-reetik-gray-400 text-sm leading-relaxed mb-4">
                {feature.description}
              </p>
              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {feature.details.map((detail, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-reetik-gray-300">
                    <span className="w-1 h-1 rounded-full bg-reetik-gold mt-2 flex-shrink-0" />
                    {detail}
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default function Features() {
  const [openIndex, setOpenIndex] = useState(0)

  return (
    <section id="features" className="relative py-24 lg:py-32">
      {/* Section header */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8">
        <RevealOnScroll>
          <div className="max-w-2xl">
            <p className="text-xs uppercase tracking-[0.2em] text-reetik-gold mb-4">Fonctionnalités</p>
            <h2 className="font-serif text-display text-reetik-cream">
              Tout ce qu'il faut pour{' '}
              <span className="italic text-gold-gradient">produire</span>.
            </h2>
            <p className="mt-4 text-reetik-gray-400 leading-relaxed">
              Un pipeline complet de création TikTok, de l'idée au contenu publié. 
              Chaque étape est assistée par l'IA.
            </p>
          </div>
        </RevealOnScroll>

        {/* Accordion */}
        <div className="mt-16 max-w-3xl">
          <StaggerContainer staggerDelay={0.08}>
            {FEATURES.map((feature, i) => (
              <StaggerItem key={feature.title}>
                <FeatureAccordion
                  feature={feature}
                  isOpen={openIndex === i}
                  onClick={() => setOpenIndex(openIndex === i ? -1 : i)}
                  index={i}
                />
              </StaggerItem>
            ))}
          </StaggerContainer>
        </div>
      </div>
    </section>
  )
}
