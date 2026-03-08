import Hero from '../components/landing/Hero'
import LogoBar from '../components/landing/LogoBar'
import Features from '../components/landing/Features'
import HowItWorks from '../components/landing/HowItWorks'
import Stats from '../components/landing/Stats'
import CTA from '../components/landing/CTA'

export default function LandingPage() {
  return (
    <main>
      <Hero />
      <LogoBar />
      <Features />
      <HowItWorks />
      <Stats />
      <CTA />
    </main>
  )
}
