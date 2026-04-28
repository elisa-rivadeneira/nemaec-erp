/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 🟢 NEMAEC Verde Militar (Principal)
        'nemaec-green': {
          50: '#E8F5E8',
          100: '#C8E6C8',
          200: '#A4D4A4',
          300: '#7BC47B',
          400: '#4CAF50',  // Verde claro
          500: '#388E3C',  // Verde medio
          600: '#2E7D2E',
          700: '#1B5E20',  // Verde oscuro (principal)
          800: '#164B1C',
          900: '#0F3814',
        },

        // ⚫ Grises Mates Militares
        'nemaec-gray': {
          50: '#F8FAFC',
          100: '#ECEFF1',  // Textos secundarios
          200: '#CFD8DC',
          300: '#B0BEC5',
          400: '#90A4AE',
          500: '#607D8B',
          600: '#546E7A',
          700: '#455A64',  // Backgrounds
          800: '#37474F',  // Cards, borders
          900: '#263238',  // Sidebar, headers
        },

        // 🟡 Amarillo Institucional
        'nemaec-yellow': {
          50: '#FFFDE7',
          100: '#FFF9C4',
          200: '#FFF59D',
          300: '#FFF176',
          400: '#FFEB3B',  // Amarillo claro
          500: '#FFC107',  // Amarillo oro (principal)
          600: '#FFB300',
          700: '#FFA000',
          800: '#FF8F00',
          900: '#FF6F00',
        },

        // 🔴 Rojo Militar Crítico
        'nemaec-red': {
          50: '#FFEBEE',
          100: '#FFCDD2',
          200: '#EF9A9A',
          300: '#E57373',
          400: '#EF5350',  // Rojo claro
          500: '#F44336',
          600: '#E53935',
          700: '#D32F2F',
          800: '#C62828',  // Rojo militar (principal)
          900: '#B71C1C',
        },

        // Estados semafóricos
        'success': '#4CAF50',
        'warning': '#FFC107',
        'error': '#C62828',
        'info': '#2196F3',
      },

      fontFamily: {
        'sans': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'Consolas', 'monospace'],
      },

      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },

      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '100': '25rem',
        '112': '28rem',
        '128': '32rem',
      },

      boxShadow: {
        'nemaec': '0 4px 6px -1px rgba(27, 94, 32, 0.1), 0 2px 4px -1px rgba(27, 94, 32, 0.06)',
        'nemaec-lg': '0 10px 15px -3px rgba(27, 94, 32, 0.1), 0 4px 6px -2px rgba(27, 94, 32, 0.05)',
        'critical': '0 4px 6px -1px rgba(198, 40, 40, 0.3), 0 2px 4px -1px rgba(198, 40, 40, 0.2)',
      },

      animation: {
        'pulse-critical': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
        'bounce-subtle': 'bounceSubtle 1s ease-in-out infinite',
      },

      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },

      backdropBlur: {
        'xs': '2px',
      },

      backgroundImage: {
        'gradient-nemaec': 'linear-gradient(135deg, #1B5E20 0%, #263238 100%)',
        'gradient-critical': 'linear-gradient(135deg, #C62828 0%, #B71C1C 100%)',
        'gradient-warning': 'linear-gradient(135deg, #FFC107 0%, #FF8F00 100%)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    // Plugin personalizado para utilidades NEMAEC
    function({ addUtilities }) {
      const newUtilities = {
        '.border-nemaec': {
          borderColor: '#4CAF50',
          borderWidth: '1px',
        },
        '.border-nemaec-2': {
          borderColor: '#4CAF50',
          borderWidth: '2px',
        },
        '.bg-nemaec-card': {
          backgroundColor: '#37474F',
          borderColor: '#4CAF50',
          borderWidth: '1px',
        },
        '.text-critical': {
          color: '#C62828',
        },
        '.text-warning': {
          color: '#FFC107',
        },
        '.bg-critical-glow': {
          backgroundColor: 'rgba(198, 40, 40, 0.1)',
          borderColor: '#C62828',
          borderWidth: '1px',
          boxShadow: '0 0 10px rgba(198, 40, 40, 0.3)',
        },
        '.hover-nemaec': {
          '&:hover': {
            backgroundColor: '#388E3C',
            borderColor: '#4CAF50',
            transform: 'translateY(-1px)',
            boxShadow: '0 4px 6px -1px rgba(27, 94, 32, 0.2)',
          },
        },
      }
      addUtilities(newUtilities, ['responsive', 'hover'])
    }
  ],
}