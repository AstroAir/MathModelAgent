<script setup lang="ts">
import NotebookArea from '@/components/NotebookArea.vue'
</script>

<template>
  <div class="h-full flex flex-col p-4 bg-gradient-to-br from-gray-50 to-slate-50">
    <div class="h-full bg-white rounded-xl border-2 shadow-lg hover:shadow-xl transition-all duration-300">
      <div class="border-b bg-gradient-to-r from-green-50 to-teal-50 px-4 py-3 rounded-t-xl">
        <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
          💻 代码执行
        </h2>
      </div>
      <div class="h-full pb-14">
        <NotebookArea class="h-full" />
      </div>
    </div>
  </div>
</template>

<style scoped>
::-webkit-scrollbar {
  display: none;
  /* 或者 width: 0; height: 0; */
}
</style>
