import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export type ThemeMode = 'light' | 'dark' | 'system'

export interface ThemeConfig {
  mode: ThemeMode
  colors: {
    light: Record<string, string>
    dark: Record<string, string>
  }
  transitions: {
    duration: string
    easing: string
  }
}

const defaultThemeConfig: ThemeConfig = {
  mode: 'system',
  colors: {
    light: {
      // Primary colors
      background: '0 0% 100%',
      foreground: '224 71.4% 4.1%',
      card: '0 0% 100%',
      'card-foreground': '224 71.4% 4.1%',
      popover: '0 0% 100%',
      'popover-foreground': '224 71.4% 4.1%',
      primary: '262.1 83.3% 57.8%',
      'primary-foreground': '210 20% 98%',
      secondary: '220 14.3% 95.9%',
      'secondary-foreground': '220.9 39.3% 11%',
      muted: '220 14.3% 95.9%',
      'muted-foreground': '220 8.9% 46.1%',
      accent: '220 14.3% 95.9%',
      'accent-foreground': '220.9 39.3% 11%',
      destructive: '0 84.2% 60.2%',
      'destructive-foreground': '210 20% 98%',
      border: '220 13% 91%',
      input: '220 13% 91%',
      ring: '262.1 83.3% 57.8%',
      // Sidebar colors
      'sidebar-background': '0 0% 98%',
      'sidebar-foreground': '240 5.3% 26.1%',
      'sidebar-primary': '240 5.9% 10%',
      'sidebar-primary-foreground': '0 0% 98%',
      'sidebar-accent': '240 4.8% 95.9%',
      'sidebar-accent-foreground': '240 5.9% 10%',
      'sidebar-border': '220 13% 91%',
      'sidebar-ring': '217.2 91.2% 59.8%',
      // Chart colors
      'chart-1': '12 76% 61%',
      'chart-2': '173 58% 39%',
      'chart-3': '197 37% 24%',
      'chart-4': '43 74% 66%',
      'chart-5': '27 87% 67%',
    },
    dark: {
      // Primary colors
      background: '224 71.4% 4.1%',
      foreground: '210 20% 98%',
      card: '224 71.4% 4.1%',
      'card-foreground': '210 20% 98%',
      popover: '224 71.4% 4.1%',
      'popover-foreground': '210 20% 98%',
      primary: '263.4 70% 50.4%',
      'primary-foreground': '210 20% 98%',
      secondary: '215 27.9% 16.9%',
      'secondary-foreground': '210 20% 98%',
      muted: '215 27.9% 16.9%',
      'muted-foreground': '217.9 10.6% 64.9%',
      accent: '215 27.9% 16.9%',
      'accent-foreground': '210 20% 98%',
      destructive: '0 62.8% 30.6%',
      'destructive-foreground': '210 20% 98%',
      border: '215 27.9% 16.9%',
      input: '215 27.9% 16.9%',
      ring: '263.4 70% 50.4%',
      // Sidebar colors
      'sidebar-background': '240 5.9% 10%',
      'sidebar-foreground': '240 4.8% 95.9%',
      'sidebar-primary': '224.3 76.3% 48%',
      'sidebar-primary-foreground': '0 0% 100%',
      'sidebar-accent': '240 3.7% 15.9%',
      'sidebar-accent-foreground': '240 4.8% 95.9%',
      'sidebar-border': '240 3.7% 15.9%',
      'sidebar-ring': '217.2 91.2% 59.8%',
      // Chart colors
      'chart-1': '220 70% 50%',
      'chart-2': '160 60% 45%',
      'chart-3': '30 80% 55%',
      'chart-4': '280 65% 60%',
      'chart-5': '340 75% 55%',
    }
  },
  transitions: {
    duration: '300ms',
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
  }
}

export const useThemeStore = defineStore('theme', () => {
  // State
  const config = ref<ThemeConfig>({ ...defaultThemeConfig })
  const isInitialized = ref(false)

  // Computed
  const isDark = computed(() => {
    if (config.value.mode === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return config.value.mode === 'dark'
  })

  const currentTheme = computed(() => isDark.value ? 'dark' : 'light')
  const currentColors = computed(() => config.value.colors[currentTheme.value])

  // Actions
  const setTheme = (mode: ThemeMode) => {
    config.value.mode = mode
    applyTheme()
  }

  const toggleTheme = () => {
    const newMode = config.value.mode === 'light' ? 'dark' : 'light'
    setTheme(newMode)
  }

  const applyTheme = () => {
    const root = document.documentElement
    const colors = currentColors.value

    // Add theme switching class to prevent flash
    root.classList.add('theme-switching')

    // Remove existing theme classes
    root.classList.remove('light', 'dark')

    // Add current theme class
    root.classList.add(currentTheme.value)

    // Apply CSS variables
    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--${key}`, value)
    })

    // Apply transition properties
    root.style.setProperty('--theme-transition-duration', config.value.transitions.duration)
    root.style.setProperty('--theme-transition-easing', config.value.transitions.easing)

    // Store preference in localStorage
    localStorage.setItem('theme-mode', config.value.mode)

    // Remove theme switching class after a brief delay
    requestAnimationFrame(() => {
      setTimeout(() => {
        root.classList.remove('theme-switching')
      }, 50)
    })
  }

  const initializeTheme = () => {
    if (isInitialized.value) return

    // Load saved theme preference
    const savedMode = localStorage.getItem('theme-mode') as ThemeMode
    if (savedMode && ['light', 'dark', 'system'].includes(savedMode)) {
      config.value.mode = savedMode
    }

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleSystemThemeChange = () => {
      if (config.value.mode === 'system') {
        applyTheme()
      }
    }
    
    mediaQuery.addEventListener('change', handleSystemThemeChange)

    // Apply initial theme
    applyTheme()
    isInitialized.value = true
  }

  const updateColors = (theme: 'light' | 'dark', colors: Partial<Record<string, string>>) => {
    config.value.colors[theme] = { ...config.value.colors[theme], ...colors }
    if (currentTheme.value === theme) {
      applyTheme()
    }
  }

  const resetToDefaults = () => {
    config.value = { ...defaultThemeConfig }
    applyTheme()
  }

  // Watch for theme changes
  watch(() => config.value.mode, applyTheme)

  return {
    // State
    config,
    isInitialized,
    
    // Computed
    isDark,
    currentTheme,
    currentColors,
    
    // Actions
    setTheme,
    toggleTheme,
    applyTheme,
    initializeTheme,
    updateColors,
    resetToDefaults
  }
}, {
  persist: {
    key: 'theme-store',
    storage: localStorage,
    paths: ['config.mode']
  }
})
