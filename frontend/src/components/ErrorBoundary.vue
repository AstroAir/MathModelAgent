<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue'
import { AlertTriangle, RefreshCw } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

interface Props {
  fallbackMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  fallbackMessage: '组件发生错误'
})

const hasError = ref(false)
const errorMessage = ref('')
const errorDetails = ref('')

const resetError = () => {
  hasError.value = false
  errorMessage.value = ''
  errorDetails.value = ''
}

onErrorCaptured((error: Error) => {
  hasError.value = true
  errorMessage.value = error.message || '未知错误'
  errorDetails.value = error.stack || ''
  
  // Log error for debugging
  console.error('ErrorBoundary caught error:', error)
  
  // Return false to prevent the error from propagating further
  return false
})
</script>

<template>
  <div v-if="hasError" class="error-boundary p-6 bg-destructive/10 border border-destructive/20 rounded-lg">
    <div class="flex items-start gap-3">
      <AlertTriangle class="w-6 h-6 text-destructive flex-shrink-0 mt-0.5" />
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-destructive mb-2">{{ props.fallbackMessage }}</h3>
        <p class="text-destructive/80 mb-3">{{ errorMessage }}</p>

        <details v-if="errorDetails" class="mb-4">
          <summary class="cursor-pointer text-sm text-destructive/80 hover:text-destructive">查看详细信息</summary>
          <pre class="mt-2 p-3 bg-destructive/10 border border-destructive/20 rounded text-xs text-destructive/80 overflow-x-auto">{{ errorDetails }}</pre>
        </details>

        <Button
          @click="resetError"
          variant="destructive"
        >
          <RefreshCw class="w-4 h-4 mr-2" />
          重试
        </Button>
      </div>
    </div>
  </div>

  <slot v-else />
</template>


