// tailwind.config.js (optional tweak)
module.exports = {
  content: ["./public/**/*.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        serif: ['Merriweather', 'Georgia', 'Times New Roman', 'serif'],
      },
    },
  },
  plugins: [],
};
