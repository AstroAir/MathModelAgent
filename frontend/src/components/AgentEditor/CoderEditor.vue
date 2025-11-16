<script setup lang="ts">
import NotebookArea from '@/components/NotebookArea.vue'
</script>

<template>
  <div class="h-full flex flex-col bg-background">
    <div class="h-full">
      <div class="border-b border-border bg-green-500/10 px-3 py-2">
        <h2 class="text-sm font-semibold text-foreground flex items-center gap-2">
          💻 代码执行
        </h2>
      </div>
      <div class="h-full pb-10">
        <NotebookArea class="h-full" />
      </div>
    </div>
  </div>
</template>
