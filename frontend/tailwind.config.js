/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ['class'],
    content: ['./index.html', './src/**/*.{ts,js,vue}'],
  theme: {
  	extend: {
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		colors: {
  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			},
  			sidebar: {
  				DEFAULT: 'hsl(var(--sidebar-background))',
  				foreground: 'hsl(var(--sidebar-foreground))',
  				primary: 'hsl(var(--sidebar-primary))',
  				'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
  				accent: 'hsl(var(--sidebar-accent))',
  				'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
  				border: 'hsl(var(--sidebar-border))',
  				ring: 'hsl(var(--sidebar-ring))'
  			},
  			// Enhanced color palette for modern design
  			'light-purple': '#C084FC',
  			'deep-purple': '#7E22CE',
  			'gradient-start': '#8B5CF6',
  			'gradient-end': '#3B82F6'
  		},
  		fontFamily: {
  			sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
  		},
  		animation: {
  			'blob': 'blob 7s infinite',
  			'shimmer': 'shimmer 2s infinite',
  			'fade-in': 'fadeIn 0.5s ease-in-out',
  			'slide-up': 'slideUp 0.5s ease-out',
  		},
  		keyframes: {
  			blob: {
  				'0%': {
  					transform: 'translate(0px, 0px) scale(1)',
  				},
  				'33%': {
  					transform: 'translate(30px, -50px) scale(1.1)',
  				},
  				'66%': {
  					transform: 'translate(-20px, 20px) scale(0.9)',
  				},
  				'100%': {
  					transform: 'translate(0px, 0px) scale(1)',
  				},
  			},
  			shimmer: {
  				'0%': {
  					'background-position': '-200% 0',
  				},
  				'100%': {
  					'background-position': '200% 0',
  				},
  			},
  			fadeIn: {
  				'0%': {
  					opacity: '0',
  				},
  				'100%': {
  					opacity: '1',
  				},
  			},
  			slideUp: {
  				'0%': {
  					transform: 'translateY(20px)',
  					opacity: '0',
  				},
  				'100%': {
  					transform: 'translateY(0)',
  					opacity: '1',
  				},
  			},
  		},
  	}
  },
  plugins: [require("tailwindcss-animate")],
}