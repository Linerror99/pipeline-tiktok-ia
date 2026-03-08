import { Link } from 'react-router-dom'
import Logo from '../ui/Logo'

const FOOTER_COLS = [
  {
    title: 'Produit',
    links: [
      { label: 'Personnages IA', href: '/#features' },
      { label: 'Scénarios', href: '/#features' },
      { label: 'Vidéos Veo 3.1', href: '/#features' },
      { label: 'Assistant TikTok', href: '/#features' },
      { label: 'Miniatures auto', href: '/#features' },
    ],
  },
  {
    title: 'Technologies',
    links: [
      { label: 'Gemini 3.1 Pro', href: '/#how-it-works' },
      { label: 'Veo 3.1', href: '/#how-it-works' },
      { label: 'Imagen 4', href: '/#how-it-works' },
      { label: 'Google Cloud', href: '/#how-it-works' },
      { label: 'Firebase', href: '/#how-it-works' },
    ],
  },
  {
    title: 'Ressources',
    links: [
      { label: 'Documentation', href: '#' },
      { label: 'API', href: '#' },
      { label: 'Tarifs', href: '/#pricing' },
      { label: 'Status', href: '#' },
    ],
  },
]

export default function Footer() {
  return (
    <footer className="relative border-t border-reetik-border/50">
      {/* Corner decorations */}
      <div className="absolute top-0 left-8 w-px h-8 bg-gradient-to-b from-reetik-gold/30 to-transparent" />
      <div className="absolute top-0 right-8 w-px h-8 bg-gradient-to-b from-reetik-gold/30 to-transparent" />

      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-16 lg:py-20">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12">
          {/* Logo + tagline */}
          <div className="lg:col-span-2">
            <Link to="/" className="text-white">
              <Logo className="h-7" />
            </Link>
            <p className="mt-4 text-sm text-reetik-gray-400 max-w-xs leading-relaxed">
              Studio de production TikTok propulsé par l'IA générative. 
              De l'idée à la vidéo virale.
            </p>
            <div className="mt-6 flex items-center gap-1 text-xs text-reetik-gray-500">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              All systems operational
            </div>
          </div>

          {/* Link columns */}
          {FOOTER_COLS.map((col) => (
            <div key={col.title}>
              <h4 className="text-sm font-semibold text-white mb-4">{col.title}</h4>
              <ul className="space-y-3">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-reetik-gray-400 hover:text-reetik-gold transition-colors duration-300"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-16 pt-8 border-t border-reetik-border/30 flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-xs text-reetik-gray-500">
            © {new Date().getFullYear()} Reetik. Propulsé par Google Cloud AI.
          </p>
          <div className="flex items-center gap-6 text-xs text-reetik-gray-500">
            <a href="#" className="hover:text-reetik-gray-300 transition-colors">Confidentialité</a>
            <a href="#" className="hover:text-reetik-gray-300 transition-colors">Conditions</a>
          </div>
        </div>
      </div>
    </footer>
  )
}
