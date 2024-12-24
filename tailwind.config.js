/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["src/electric_toolbox/templates/**/*.{html,js}"],
  darkMode: 'selector',
  theme: {
    extend: {},
    colors: {
      'outone': '#E8E1D9',
      'outtext': '#5C4B3F',
      'outp': '#BDB2A5',
      'outs': '#A7A9AC',
      'outa': '#FA4616',
      'doutone': '#43423E',
      'douttext': '#CCCCCC',
      'doutp': '#686868',
      'douts': '#72583F',
      'douta': '#FA4616',
    }
  },
  plugins: [],
}
