/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        pixel: ['"Press Start 2P"', '"VT323"', 'monospace',]
      },
      animation: {
        'slow-bounce': 'bounce 1.5s infinite',
        'pixel-pulse': 'pixel-pulse 3s infinite',
        'pet-float': 'pet-float 4s ease-in-out infinite',
        'glitch': 'glitch 1s linear infinite',
        'scanline': 'scanline 8s linear infinite',
        'retro-flicker': 'retro-flicker 0.15s infinite',
        'pet-eating': 'pet-eating 0.5s ease-in-out',
        'pet-playing': 'pet-playing 1s ease-in-out',
        'pet-teaching': 'pet-teaching 1s ease-in-out',
      },
      keyframes: {
        'pixel-pulse': {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
        'pet-float': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'pet-eating': {
          '0%': { transform: 'scale(1.2) rotate(0deg)' },
          '25%': { transform: 'scale(1.2) rotate(-10deg)' },
          '75%': { transform: 'scale(1.2) rotate(10deg)' },
          '100%': { transform: 'scale(1.2) rotate(0deg)' },
        },
        'pet-playing': {
          '0%': { transform: 'scale(1.2) translateY(0) rotate(0deg)' },
          '25%': { transform: 'scale(1.3) translateY(-15px) rotate(-15deg)' },
          '50%': { transform: 'scale(1.2) translateY(0) rotate(0deg)' },
          '75%': { transform: 'scale(1.3) translateY(-15px) rotate(15deg)' },
          '100%': { transform: 'scale(1.2) translateY(0) rotate(0deg)' },
        },
        'pet-teaching': {
          '0%': { transform: 'scale(1.2) translateY(0)' },
          '25%': { transform: 'scale(1.25) translateY(-5px)' },
          '50%': { transform: 'scale(1.2) translateY(0)' },
          '75%': { transform: 'scale(1.25) translateY(-5px)' },
          '100%': { transform: 'scale(1.2) translateY(0)' },
        },
        'glitch': {
          '0%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
          '100%': { transform: 'translate(0)' },
        },
        'scanline': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        'retro-flicker': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
      },
      boxShadow: {
        'retro': '0 0 10px rgba(147, 51, 234, 0.5), 0 0 20px rgba(147, 51, 234, 0.3)',
        'retro-glow': '0 0 15px rgba(147, 51, 234, 0.7), 0 0 30px rgba(147, 51, 234, 0.5)',
      },
    },
  },
  plugins: [],
} 