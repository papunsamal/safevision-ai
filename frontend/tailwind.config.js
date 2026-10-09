/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}', // Ensures all React components are scanned for classes
  ],
  theme: {
    extend: {
      /**
       * Custom Animations & Keyframes
       * Used for: Loading Spinners, Pulse Effects on Violations, Smooth Transitions
       */
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 3s linear infinite',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.3s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      /**
       * Box Shadows
       * Adds depth to cards and modals without heavy CSS overrides
       */
      boxShadow: {
        'glow-emerald': '0 0 15px rgba(16, 185, 129, 0.3)',
        'glow-red': '0 0 15px rgba(239, 68, 68, 0.3)',
        'card-dark': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
      },
    },
  },
  plugins: [],
};
