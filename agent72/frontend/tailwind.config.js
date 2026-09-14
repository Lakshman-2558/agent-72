/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: '#163A63',
        institutional: '#2F6EA6',
        sky: '#E8F4FB',
        mainbg: '#F5F9FC',
        surface: '#FFFFFF',
        customborder: '#D7E4EE',
        primarytext: '#19324A',
        mutedtext: '#6B7F91',
        success: '#16805C',
        warning: '#B7791F',
        danger: '#C44B55',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
