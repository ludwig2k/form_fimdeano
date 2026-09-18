/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        confra: {
          red: '#8b1d24',
          gold: '#d4af37',
          green: '#1f4d3a',
          cream: '#fdf8ef',
        },
      },
    },
  },
  plugins: [],
}
