import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Zap,
  Film,
  Wand2,
  Clock,
  Globe,
  ArrowRight,
  Play,
  CheckCircle,
  Star,
  Users,
  Rocket,
  Shield,
  BarChart3 } from
'lucide-react';
import { MatrixParticles } from '../components/MatrixParticles';
import { RotatingRings } from '../components/RotatingRings';
import { GlowText } from '../components/GlowText';
import { PulseButton } from '../components/PulseButton';
import { AnimatedCounter } from '../components/AnimatedCounter';
import { FeatureCard } from '../components/FeatureCard';
import { TiltCard } from '../components/TiltCard';
export function LandingPage() {
  const navigate = useNavigate();
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], [0, -100]);
  const features = [
  {
    icon: Wand2,
    title: 'AI-Powered Scripts',
    description:
    'Our AI writes engaging scripts tailored to your topic and style in seconds.'
  },
  {
    icon: Film,
    title: 'Auto Video Generation',
    description:
    'Transform scripts into stunning videos with AI-generated visuals and transitions.'
  },
  {
    icon: Clock,
    title: 'Lightning Fast',
    description:
    'Create professional TikTok videos in under 3 minutes, not hours.'
  },
  {
    icon: Globe,
    title: 'Multi-Language',
    description:
    'Generate content in French, English, Spanish and more languages.'
  },
  {
    icon: Sparkles,
    title: 'Smart Subtitles',
    description:
    'Automatic captions with perfect timing and stylish animations.'
  },
  {
    icon: Zap,
    title: 'One-Click Export',
    description:
    'Download in TikTok-ready format (9:16) with optimal quality.'
  }];

  const stats = [
  {
    value: 50000,
    suffix: '+',
    label: 'Videos Created'
  },
  {
    value: 12000,
    suffix: '+',
    label: 'Happy Creators'
  },
  {
    value: 98,
    suffix: '%',
    label: 'Satisfaction Rate'
  }];

  return (
    <div className="min-h-screen relative overflow-hidden">
      <MatrixParticles />
      <div className="bg-mesh-green" />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 py-20">
        {/* Rotating Rings Background */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-30">
          <RotatingRings size="xl" />
        </div>

        <div className="relative z-10 max-w-5xl mx-auto text-center">
          {/* Badge */}
          <motion.div
            initial={{
              opacity: 0,
              y: 20
            }}
            animate={{
              opacity: 1,
              y: 0
            }}
            transition={{
              duration: 0.6
            }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-8">

            <motion.div
              animate={{
                rotate: 360
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: 'linear'
              }}>

              <Sparkles className="w-4 h-4 text-emerald-400" />
            </motion.div>
            <span className="text-sm text-emerald-400 font-medium">
              Powered by Advanced AI
            </span>
          </motion.div>

          {/* Main Title */}
          <GlowText
            text="Create Viral TikToks"
            className="text-5xl md:text-7xl lg:text-8xl text-white mb-4" />

          <motion.h2
            initial={{
              opacity: 0
            }}
            animate={{
              opacity: 1
            }}
            transition={{
              delay: 1,
              duration: 0.8
            }}
            className="text-3xl md:text-5xl lg:text-6xl font-display font-bold bg-gradient-to-r from-emerald-400 via-lime-400 to-emerald-400 bg-clip-text text-transparent mb-8">

            In Seconds, Not Hours
          </motion.h2>

          {/* Subtitle */}
          <motion.p
            initial={{
              opacity: 0,
              y: 20
            }}
            animate={{
              opacity: 1,
              y: 0
            }}
            transition={{
              delay: 1.2,
              duration: 0.6
            }}
            className="text-xl text-white/60 max-w-2xl mx-auto mb-12">

            Transform any idea into a professional, engaging TikTok video with
            AI-powered script writing, video generation, and automatic
            subtitles.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{
              opacity: 0,
              y: 20
            }}
            animate={{
              opacity: 1,
              y: 0
            }}
            transition={{
              delay: 1.4,
              duration: 0.6
            }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4">

            <PulseButton size="lg" onClick={() => navigate('/create')}>
              <Rocket className="w-5 h-5" />
              Start Creating Free
            </PulseButton>

            <motion.button
              whileHover={{
                scale: 1.02
              }}
              whileTap={{
                scale: 0.98
              }}
              className="flex items-center gap-2 px-6 py-4 text-white/70 hover:text-white transition-colors">

              <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center">
                <Play className="w-4 h-4 ml-0.5" fill="currentColor" />
              </div>
              Watch Demo
            </motion.button>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            initial={{
              opacity: 0
            }}
            animate={{
              opacity: 1
            }}
            transition={{
              delay: 2
            }}
            className="absolute bottom-10 left-1/2 -translate-x-1/2">

            <motion.div
              animate={{
                y: [0, 10, 0]
              }}
              transition={{
                duration: 2,
                repeat: Infinity
              }}
              className="w-6 h-10 rounded-full border-2 border-emerald-500/30 flex justify-center pt-2">

              <motion.div
                animate={{
                  y: [0, 12, 0],
                  opacity: [1, 0, 1]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity
                }}
                className="w-1.5 h-1.5 rounded-full bg-emerald-400" />

            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {stats.map((stat, index) =>
            <motion.div
              key={index}
              initial={{
                opacity: 0,
                y: 30
              }}
              whileInView={{
                opacity: 1,
                y: 0
              }}
              viewport={{
                once: true
              }}
              transition={{
                delay: index * 0.1
              }}
              className="text-center">

                <div className="text-5xl md:text-6xl text-emerald-400 mb-2">
                  <AnimatedCounter value={stat.value} suffix={stat.suffix} />
                </div>
                <p className="text-white/50 font-medium">{stat.label}</p>
              </motion.div>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{
              opacity: 0,
              y: 20
            }}
            whileInView={{
              opacity: 1,
              y: 0
            }}
            viewport={{
              once: true
            }}
            className="text-center mb-16">

            <h2 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">
              Everything You Need
            </h2>
            <p className="text-white/50 text-lg max-w-2xl mx-auto">
              A complete suite of AI tools to create stunning TikTok content
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) =>
            <FeatureCard key={index} {...feature} delay={index * 0.1} />
            )}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{
              opacity: 0,
              y: 20
            }}
            whileInView={{
              opacity: 1,
              y: 0
            }}
            viewport={{
              once: true
            }}
            className="text-center mb-16">

            <h2 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">
              Three Simple Steps
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
            {
              step: '01',
              title: 'Describe Your Idea',
              desc: 'Tell us your topic and preferred style'
            },
            {
              step: '02',
              title: 'AI Creates Magic',
              desc: 'Watch as AI generates your video'
            },
            {
              step: '03',
              title: 'Download & Share',
              desc: 'Get your TikTok-ready video instantly'
            }].
            map((item, index) =>
            <motion.div
              key={index}
              initial={{
                opacity: 0,
                y: 30
              }}
              whileInView={{
                opacity: 1,
                y: 0
              }}
              viewport={{
                once: true
              }}
              transition={{
                delay: index * 0.2
              }}
              className="relative">

                <div className="text-8xl font-display font-bold text-emerald-500/10 absolute -top-4 -left-2">
                  {item.step}
                </div>
                <div className="relative pt-12">
                  <h3 className="font-display text-xl font-semibold text-white mb-2">
                    {item.title}
                  </h3>
                  <p className="text-white/50">{item.desc}</p>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-32 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{
              opacity: 0,
              scale: 0.95
            }}
            whileInView={{
              opacity: 1,
              scale: 1
            }}
            viewport={{
              once: true
            }}
            className="rotating-border rounded-3xl p-12 md:p-16">

            <div className="relative z-10">
              <motion.div
                animate={{
                  rotate: 360
                }}
                transition={{
                  duration: 20,
                  repeat: Infinity,
                  ease: 'linear'
                }}
                className="w-20 h-20 mx-auto mb-8 rounded-full bg-gradient-to-br from-emerald-500 to-lime-500 flex items-center justify-center">

                <Zap className="w-10 h-10 text-dark-900" />
              </motion.div>

              <h2 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">
                Ready to Go Viral?
              </h2>
              <p className="text-white/50 text-lg mb-8 max-w-xl mx-auto">
                Join thousands of creators who are already making amazing TikTok
                content with AI.
              </p>

              <PulseButton size="lg" onClick={() => navigate('/create')}>
                Create Your First Video
                <ArrowRight className="w-5 h-5" />
              </PulseButton>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-12 px-6 border-t border-emerald-500/10">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-500 to-lime-500 flex items-center justify-center">
              <Zap className="w-4 h-4 text-dark-900" />
            </div>
            <span className="font-display font-bold text-white">Reetik</span>
          </div>

          <div className="flex items-center gap-8 text-sm text-white/40">
            <a href="#" className="hover:text-emerald-400 transition-colors">
              Terms
            </a>
            <a href="#" className="hover:text-emerald-400 transition-colors">
              Privacy
            </a>
            <a href="#" className="hover:text-emerald-400 transition-colors">
              Contact
            </a>
          </div>

          <p className="text-sm text-white/30">
            © 2026 Reetik. All rights reserved.
          </p>
        </div>
      </footer>
    </div>);

}