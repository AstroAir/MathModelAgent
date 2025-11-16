<script setup lang="ts">
import { cn } from '@/lib/utils'
import type { HTMLAttributes } from 'vue'

interface SystemMessageProps {
  class?: HTMLAttributes['class']
  content: string
  type?: 'info' | 'warning' | 'success' | 'error'
}

const props = withDefaults(defineProps<SystemMessageProps>(), {
  type: 'info'
})

const typeStyles = {
  info: 'text-primary bg-primary/10 border-primary/20',
  warning: 'text-yellow-500 dark:text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  success: 'text-green-500 dark:text-green-400 bg-green-500/10 border-green-500/20',
  error: 'text-destructive bg-destructive/10 border-destructive/20'
}
</script>

<template>
  <div class="flex justify-center my-3 system-message-animate">
    <div :class="cn(
      'inline-flex items-center gap-2 px-4 py-2 text-xs rounded-full border-2 shadow-sm font-medium backdrop-blur-sm',
      typeStyles[props.type],
      props.class
    )">
      <!-- 不同类型的图标 -->
      <svg v-if="props.type === 'info'" class="w-4 h-4 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M12 16v-4" />
        <path d="M12 8h.01" />
      </svg>
      <svg v-else-if="props.type === 'warning'" class="w-4 h-4 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <path d="M12 9v4" />
        <path d="M12 17h.01" />
      </svg>
      <svg v-else-if="props.type === 'success'" class="w-4 h-4 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <path d="M22 4L12 14.01l-3-3" />
      </svg>
      <svg v-else-if="props.type === 'error'" class="w-4 h-4 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10" />
        <path d="M15 9l-6 6" />
        <path d="M9 9l6 6" />
      </svg>

      <span class="leading-none">{{ props.content }}</span>
    </div>
  </div>
</template>

