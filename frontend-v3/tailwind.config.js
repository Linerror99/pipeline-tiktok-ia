/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'reetik-black': '#0A0A0A',
        'reetik-dark': '#111111',
        'reetik-card': '#161616',
        'reetik-border': '#222222',
        'reetik-gold': '#C9A96E',
        'reetik-gold-light': '#E0C992',
        'reetik-gold-dark': '#A88B4A',
        'reetik-cream': '#F5F0E8',
        'reetik-gray': {
          100: '#E5E5E5',
          200: '#CCCCCC',
          300: '#999999',
          400: '#666666',
          500: '#444444',
          600: '#333333',
          700: '#222222',
          800: '#1A1A1A',
          900: '#111111',
        },
      },
      fontFamily: {
        serif: ['Playfair Display', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'hero': ['clamp(2.5rem, 6vw, 5rem)', { lineHeight: '1.05', letterSpacing: '-0.02em' }],
        'display': ['clamp(2rem, 4vw, 3.5rem)', { lineHeight: '1.1', letterSpacing: '-0.01em' }],
        'heading': ['clamp(1.5rem, 3vw, 2.5rem)', { lineHeight: '1.2' }],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gold-gradient': 'linear-gradient(135deg, #C9A96E 0%, #E0C992 50%, #C9A96E 100%)',
        'dark-gradient': 'linear-gradient(180deg, #0A0A0A 0%, #111111 100%)',
      },
      boxShadow: {
        'gold': '0 0 20px rgba(201, 169, 110, 0.15)',
        'gold-lg': '0 0 40px rgba(201, 169, 110, 0.2)',
        'card': '0 4px 24px rgba(0, 0, 0, 0.4)',
        'card-hover': '0 8px 40px rgba(0, 0, 0, 0.6)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.6s ease-out',
        'fade-in': 'fadeIn 0.8s ease-out',
        'marquee': 'marquee 30s linear infinite',
        'spin-slow': 'spin 20s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(201,169,110,0.2)' },
          '100%': { boxShadow: '0 0 20px rgba(201,169,110,0.4)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        marquee: {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-50%)' },
        },
      },
      borderRadius: {
        '4xl': '2rem',
      },
    },
  },
  plugins: [],
}
