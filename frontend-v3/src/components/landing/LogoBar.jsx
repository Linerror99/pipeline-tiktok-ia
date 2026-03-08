import { RevealOnScroll } from '../ui/Animations'

const LOGOS = [
  { name: 'Gemini 3.1 Pro', label: 'Gemini' },
  { name: 'Veo 3.1', label: 'Veo 3.1' },
  { name: 'Imagen 4', label: 'Imagen 4' },
  { name: 'Google Cloud', label: 'Google Cloud' },
  { name: 'Firebase', label: 'Firebase' },
  { name: 'Vertex AI', label: 'Vertex AI' },
]

export default function LogoBar() {
  return (
    <section className="relative py-16 border-y border-reetik-border/30">
      <RevealOnScroll>
        <p className="text-center text-xs uppercase tracking-[0.2em] text-reetik-gray-500 mb-10">
          Propulsé par les dernières technologies IA de Google
        </p>
      </RevealOnScroll>

      {/* Infinite marquee */}
      <div className="relative overflow-hidden mask-fade-x">
        <div className="flex animate-marquee">
          {[...LOGOS, ...LOGOS].map((logo, i) => (
            <div
              key={i}
              className="flex-shrink-0 mx-10 flex items-center gap-2 text-reetik-gray-500 
                         hover:text-reetik-gold transition-colors duration-500 cursor-default"
            >
              <div className="w-8 h-8 rounded-lg bg-reetik-card border border-reetik-border/40 
                              flex items-center justify-center text-[10px] font-bold">
                {logo.label.charAt(0)}
              </div>
              <span className="text-sm font-medium whitespace-nowrap">{logo.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
