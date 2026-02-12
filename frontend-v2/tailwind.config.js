/** @type {import('tailwindcss').Config} */
export default {
  content: [
  './index.html',
  './src/**/*.{js,ts,jsx,tsx}'
],
  theme: {
    extend: {
      colors: {
        emerald: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
        lime: {
          400: '#a3e635',
          500: '#84cc16',
          600: '#65a30d',
        },
        dark: {
          900: '#030712',
          800: '#0a0f1a',
          700: '#111827',
          600: '#1f2937',
        }
      },
      fontFamily: {
        sans: ['"Inter"', 'sans-serif'],
        display: ['"Space Grotesk"', 'sans-serif'],
      },
      animation: {
        'spin-slow': 'spin 20s linear infinite',
        'spin-slower': 'spin 30s linear infinite',
        'spin-reverse': 'spin 25s linear infinite reverse',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'float': 'float-rotate 8s ease-in-out infinite',
        'matrix': 'matrix-fall 10s linear infinite',
      },
      boxShadow: {
        'glow-sm': '0 0 10px rgba(16, 185, 129, 0.3)',
        'glow': '0 0 20px rgba(16, 185, 129, 0.4), 0 0 40px rgba(16, 185, 129, 0.2)',
        'glow-lg': '0 0 30px rgba(16, 185, 129, 0.5), 0 0 60px rgba(16, 185, 129, 0.3)',
        'glow-lime': '0 0 20px rgba(132, 204, 22, 0.4), 0 0 40px rgba(132, 204, 22, 0.2)',
      },
    },
  },
  plugins: [],
}
