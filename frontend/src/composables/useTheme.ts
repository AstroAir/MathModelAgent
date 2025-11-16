import { computed, onMounted, onUnmounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import type { ThemeMode } from '@/stores/theme'
import {
  applyThemeOptimized,
  ThemePerformanceMonitor,
  safeThemeSwitch
} from '@/utils/themeOptimization'

/**
 * Composable for theme management
 * Provides reactive theme state and methods for theme manipulation
 */
export function useTheme() {
  const themeStore = useThemeStore()
  const monitor = new ThemePerformanceMonitor()

  // Reactive theme state
  const isDark = computed(() => themeStore.isDark)
  const currentTheme = computed(() => themeStore.currentTheme)
  const themeMode = computed(() => themeStore.config.mode)
  const isSystemTheme = computed(() => themeStore.config.mode === 'system')

  // Theme actions
  const setTheme = (mode: ThemeMode) => {
    monitor.start()
    safeThemeSwitch(() => {
      themeStore.setTheme(mode)
    }, () => {
      // Fallback: reset to system theme
      themeStore.setTheme('system')
    })
    monitor.end('setTheme')
  }

  const toggleTheme = () => {
    monitor.start()
    safeThemeSwitch(() => {
      themeStore.toggleTheme()
    }, () => {
      themeStore.setTheme('system')
    })
    monitor.end('toggleTheme')
  }

  const setLightTheme = () => {
    setTheme('light')
  }

  const setDarkTheme = () => {
    setTheme('dark')
  }

  const setSystemTheme = () => {
    setTheme('system')
  }

  // Initialize theme on mount
  onMounted(() => {
    monitor.start()
    applyThemeOptimized(() => {
      themeStore.initializeTheme()
    })
    monitor.end('initializeTheme')
  })

  return {
    // State
    isDark,
    currentTheme,
    themeMode,
    isSystemTheme,

    // Actions
    setTheme,
    toggleTheme,
    setLightTheme,
    setDarkTheme,
    setSystemTheme,

    // Store reference for advanced usage
    themeStore
  }
}

/**
 * Composable for theme-aware CSS classes
 * Provides utility functions for conditional styling based on theme
 */
export function useThemeClasses() {
  const { isDark, currentTheme } = useTheme()

  const themeClass = computed(() => currentTheme.value)
  
  const conditionalClass = (lightClass: string, darkClass: string) => {
    return computed(() => isDark.value ? darkClass : lightClass)
  }

  const themeVariant = <T>(variants: { light: T; dark: T }) => {
    return computed(() => variants[currentTheme.value as keyof typeof variants])
  }

  return {
    themeClass,
    conditionalClass,
    themeVariant,
    isDark,
    currentTheme
  }
}

/**
 * Composable for theme transitions
 * Provides utilities for smooth theme switching animations
 */
export function useThemeTransitions() {
  const themeStore = useThemeStore()

  const enableTransitions = () => {
    const root = document.documentElement
    root.style.setProperty('--theme-transition', `all ${themeStore.config.transitions.duration} ${themeStore.config.transitions.easing}`)
  }

  const disableTransitions = () => {
    const root = document.documentElement
    root.style.removeProperty('--theme-transition')
  }

  const withTransition = async (callback: () => void | Promise<void>) => {
    enableTransitions()
    await callback()
    // Keep transitions enabled for smooth UX
  }

  return {
    enableTransitions,
    disableTransitions,
    withTransition
  }
}

/**
 * Composable for system theme detection
 * Provides utilities for detecting and responding to system theme changes
 */
export function useSystemTheme() {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  
  const isSystemDark = computed(() => mediaQuery.matches)
  
  const onSystemThemeChange = (callback: (isDark: boolean) => void) => {
    const handler = (e: MediaQueryListEvent) => callback(e.matches)
    mediaQuery.addEventListener('change', handler)
    
    onUnmounted(() => {
      mediaQuery.removeEventListener('change', handler)
    })
    
    return () => mediaQuery.removeEventListener('change', handler)
  }

  return {
    isSystemDark,
    onSystemThemeChange,
    mediaQuery
  }
}
