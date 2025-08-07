/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./serverproject/templates/**/*.html",
    "./serverproject/static/**/*.js",
  ],
  safelist: [
    {
      pattern: /^(text|border|btn-outline)-(info|success|warning|secondary)$/,
    },
  ],
  theme: {
    extend: {
      animation: {
        marquee: 'marquee 40s linear infinite',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-100%)' },
        }
      }
    },
  },
  plugins: [
    require("daisyui"),
    function ({ addVariant }) {
      addVariant('hover-paused', '&:hover');
    }
  ],
  daisyui: {
    themes: [
      {
        light: {
          "primary": "#6366f1",          // Indigo 500
          "secondary": "#14b8a6",        // Teal 500
          "accent": "#f43f5e",           // Rose 500
          "neutral": "#3d4451",
          "base-100": "#ffffff",
          "info": "#3abff8",
          "success": "#36d399",
          "warning": "#fbbd23",
          "error": "#f87272",
        },
      },
      {
        dark: {
          "primary": "#6366f1",          // Indigo 500
          "secondary": "#14b8a6",        // Teal 500
          "accent": "#f43f5e",           // Rose 500
          "neutral": "#191d24",
          "base-100": "#2a303c",
          "info": "#3abff8",
          "success": "#36d399",
          "warning": "#fbbd23",
          "error": "#f87272",
        },
      },
    ],
  },
};