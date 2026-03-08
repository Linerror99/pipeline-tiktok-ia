import { RevealOnScroll, StaggerContainer, StaggerItem } from '../ui/Animations'
import { MessageSquare, Palette, Film, Rocket } from 'lucide-react'

const STEPS = [
  {
    icon: MessageSquare,
    number: '01',
    title: 'Discutez avec l\'IA',
    description: 'Décrivez vos personnages et votre scénario par chat. Gemini 3.1 Pro comprend votre vision et structure le contenu.',
  },
  {
    icon: Palette,
    number: '02',
    title: 'Générez les visuels',
    description: 'Imagen 4 crée des portraits réalistes de vos personnages en 9:16, prêts pour TikTok.',
  },
  {
    icon: Film,
    number: '03',
    title: 'Produisez la vidéo',
    description: 'Veo 3.1 génère une vidéo continue jusqu\'à 57 secondes. Suivi en temps réel de la progression.',
  },
  {
    icon: Rocket,
    number: '04',
    title: 'Publiez sur TikTok',
    description: 'L\'assistant IA vous fournit hashtags, titre et suggestions de profil pour maximiser la viralité.',
  },
]

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="relative py-24 lg:py-32 overflow-hidden">
      {/* Background accent */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] 
                      bg-gradient-radial from-reetik-gold/[0.02] to-transparent rounded-full" />

      <div className="relative max-w-7xl mx-auto px-6 lg:px-8">
        <RevealOnScroll>
          <div className="text-center max-w-2xl mx-auto">
            <p className="text-xs uppercase tracking-[0.2em] text-reetik-gold mb-4">Comment ça marche</p>
            <h2 className="font-serif text-display text-reetik-cream">
              De l'idée au{' '}
              <span className="italic text-gold-gradient">TikTok viral</span>
              <br />en 4 étapes.
            </h2>
          </div>
        </RevealOnScroll>

        {/* Steps grid */}
        <StaggerContainer className="mt-20 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" staggerDelay={0.12}>
          {STEPS.map((step, i) => (
            <StaggerItem key={step.number}>
              <div className="group card-hover-glow rounded-2xl p-8 bg-reetik-card/50 h-full
                              relative overflow-hidden">
                {/* Corner accent */}
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-radial 
                               from-reetik-gold/[0.06] to-transparent opacity-0 
                               group-hover:opacity-100 transition-opacity duration-500" />

                <span className="text-4xl font-serif text-reetik-gold/20 group-hover:text-reetik-gold/40 
                                 transition-colors duration-500">
                  {step.number}
                </span>

                <div className="mt-6 w-12 h-12 rounded-xl bg-reetik-gold/10 border border-reetik-gold/20
                               flex items-center justify-center
                               group-hover:bg-reetik-gold/20 group-hover:border-reetik-gold/40
                               transition-all duration-500">
                  <step.icon className="w-5 h-5 text-reetik-gold" />
                </div>

                <h3 className="mt-5 text-lg font-medium text-white">{step.title}</h3>
                <p className="mt-3 text-sm text-reetik-gray-400 leading-relaxed">
                  {step.description}
                </p>

                {/* Connector line (except last) */}
                {i < STEPS.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 w-6 border-t 
                                  border-dashed border-reetik-border/40" />
                )}
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </section>
  )
}
