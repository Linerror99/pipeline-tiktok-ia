import { RevealOnScroll, StaggerContainer, StaggerItem } from '../ui/Animations'

const STATS = [
  { value: '57s', label: 'de vidéo continue max' },
  { value: '9:16', label: 'format TikTok natif' },
  { value: '<3min', label: 'pour une vidéo de 8s' },
  { value: '5', label: 'modèles IA de pointe' },
]

export default function Stats() {
  return (
    <section className="relative py-24 border-y border-reetik-border/30">
      {/* Background pattern */}
      <div className="absolute inset-0 grid-lines opacity-20" />

      <div className="relative max-w-7xl mx-auto px-6 lg:px-8">
        <RevealOnScroll>
          <div className="text-center max-w-2xl mx-auto mb-16">
            <p className="text-xs uppercase tracking-[0.2em] text-reetik-gold mb-4">Performance</p>
            <h2 className="font-serif text-display text-reetik-cream">
              La puissance de{' '}
              <span className="italic text-gold-gradient">Google Cloud AI</span>.
            </h2>
          </div>
        </RevealOnScroll>

        <StaggerContainer className="grid grid-cols-2 lg:grid-cols-4 gap-8" staggerDelay={0.1}>
          {STATS.map((stat) => (
            <StaggerItem key={stat.label}>
              <div className="text-center group">
                <div className="font-serif text-5xl lg:text-6xl text-reetik-cream 
                               group-hover:text-gold-gradient transition-all duration-500">
                  {stat.value}
                </div>
                <p className="mt-3 text-sm text-reetik-gray-400">{stat.label}</p>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>

        {/* Architecture diagram */}
        <RevealOnScroll className="mt-24">
          <div className="relative max-w-3xl mx-auto">
            <div className="corner-decoration rounded-2xl border border-reetik-border/40 
                           bg-reetik-card/30 p-8 lg:p-12">
              <p className="text-xs uppercase tracking-[0.2em] text-reetik-gold/60 mb-6 text-center">
                Architecture
              </p>
              <div className="grid grid-cols-3 gap-4 text-center">
                {/* Row 1: Frontend */}
                <div className="col-span-3 p-4 rounded-xl bg-reetik-dark border border-reetik-border/30">
                  <span className="text-xs text-reetik-gray-400">Frontend</span>
                  <p className="text-sm text-white mt-1">React + Vite</p>
                </div>

                {/* Row 2: Backend */}
                <div className="col-span-3 p-4 rounded-xl bg-reetik-dark border border-reetik-border/30">
                  <span className="text-xs text-reetik-gray-400">API Backend</span>
                  <p className="text-sm text-white mt-1">FastAPI — Cloud Run</p>
                </div>

                {/* Row 3: AI Agents */}
                {['Agent Video\nVeo 3.1', 'Agent Thumbnail\nImagen 4', 'Monitor\nExtensions'].map((agent) => (
                  <div key={agent} className="p-4 rounded-xl bg-reetik-gold/[0.05] border border-reetik-gold/20">
                    <p className="text-xs text-reetik-gold whitespace-pre-line">{agent}</p>
                  </div>
                ))}

                {/* Row 4: Data */}
                <div className="p-3 rounded-xl bg-reetik-dark border border-reetik-border/30">
                  <p className="text-xs text-reetik-gray-300">Firestore<br /><span className="text-reetik-gray-500">reetik-v3</span></p>
                </div>
                <div className="p-3 rounded-xl bg-reetik-dark border border-reetik-border/30">
                  <p className="text-xs text-reetik-gray-300">Cloud Storage<br /><span className="text-reetik-gray-500">3 buckets</span></p>
                </div>
                <div className="p-3 rounded-xl bg-reetik-dark border border-reetik-border/30">
                  <p className="text-xs text-reetik-gray-300">Firebase Auth<br /><span className="text-reetik-gray-500">Google Sign-In</span></p>
                </div>
              </div>
            </div>
          </div>
        </RevealOnScroll>
      </div>
    </section>
  )
}
