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
    extend: {},
  },
  plugins: [require("daisyui")],
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