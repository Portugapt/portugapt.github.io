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
      'doutone': '#404241',
      'douttext': '#E5E8E3',
      'doutp': '#2D3033',
      'douts': '#767A7B',
      'douta': '#60625B',
    },
    typography: ({ theme }) => ({
      DEFAULT: {
          css: {
              h1: {
                  fontWeight: theme('fontWeight.bold'),
                  fontSize: theme('fontSize.4xl'),
                  marginBottom: theme('spacing.2'),
              },
              h2: {
                  fontWeight: theme('fontWeight.bold'),
                  fontSize: theme('fontSize.2xl'),
                  marginTop: theme('spacing.8'),
                  marginBottom: theme('spacing.2'),
              },
              h3: {
                  fontWeight: theme('fontWeight.bold'),
                  fontSize: theme('fontSize.xl'),
                  marginTop: theme('spacing.6'),
                  marginBottom: theme('spacing.2'),
              },
              p: {
                  color: theme('colors.mytext'),
                  lineHeight: theme('lineHeight.relaxed'),
                  marginBottom: theme('spacing.4'),
              },
              'p code': {
                  fontStyle: theme('fontStyle.italic'),
                  borderRadius: theme('borderRadius.sm'),
                  padding: theme('spacing.1'),
              },
              pre: {
                  color: theme('colors.daouta'),
                  lineHeight: theme('lineHeight.relaxed'),
                  marginBottom: theme('spacing.2'),
                  padding: theme('spacing.4'),
                  overflowX: 'auto',
              },

          },
      },
      // Dark mode styles
      invert: {
          css: {
              p: {
                  color: theme('colors.douttext'),
                  code: {
                      backgroundColor: theme('colors.doutp'),
                  },
              },
              pre: {
                  color: theme('colors.daouta'),
                  backgroundColor: theme('colors.dmyprimary'),
              },
              // ... other dark mode styles
          },
      },
  }),
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
