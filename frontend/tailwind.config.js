/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#FF0050',
        secondary: '#00F2EA',
        dark: '#0F0F0F',
      },
    },
  },
  plugins: [],
}
