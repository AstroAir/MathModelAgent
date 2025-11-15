<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue';
import { renderMarkdown } from '@/utils/markdown';
import type { WriterMessage } from '@/utils/response'
import { ScrollArea } from '@/components/ui/scroll-area'

interface ContentSection {
  id: number;
  content: string;
  renderedContent: string;
  sub_title?: string;
}

const props = defineProps<{
  messages: WriterMessage[]
  writerSequence: string[]
}>()

const sections = ref<ContentSection[]>([]);
let nextId = 0;

// 添加新的内容段落
const appendContent = async (content: string, sub_title?: string) => {
  const renderedContent = await renderMarkdown(content);
  sections.value.push({
    id: nextId++,
    content,
    renderedContent,
    sub_title
  });
};

// 根据 writerSequence 排序内容
const sortedSections = computed(() => {
  if (!props.writerSequence.length) return sections.value;

  return [...sections.value].sort((a, b) => {
    const aIndex = a.sub_title ? props.writerSequence.indexOf(a.sub_title) : Infinity;
    const bIndex = b.sub_title ? props.writerSequence.indexOf(b.sub_title) : Infinity;

    if (aIndex === Infinity && bIndex === Infinity) return 0;
    if (aIndex === Infinity) return 1;
    if (bIndex === Infinity) return -1;

    return aIndex - bIndex;
  });
});

// 监听消息变化
watch(() => props.messages, async (messages) => {
  // 清空现有内容
  sections.value = [];
  nextId = 0;

  // 按顺序添加每个消息的内容
  for (const msg of messages) {
    if (msg.content) {
      await appendContent(msg.content, msg.sub_title);
    }
  }
}, { immediate: true });
</script>

<template>
  <div class="h-full flex flex-col p-4 bg-gradient-to-br from-gray-50 to-slate-50">
    <div class="h-full bg-white rounded-xl border-2 shadow-lg hover:shadow-xl transition-all duration-300">
      <div class="border-b bg-gradient-to-r from-purple-50 to-pink-50 px-4 py-3 rounded-t-xl">
        <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
          📝 论文内容
        </h2>
      </div>
      <div class="h-full pb-14">
        <ScrollArea class="h-full overflow-y-auto">
          <div class="p-6">
            <div class="max-w-4xl mx-auto overflow-y-auto space-y-6">
              <TransitionGroup name="section" tag="div" class="space-y-6">
                <div v-for="section in sortedSections" :key="section.id"
                  class="bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-md hover:shadow-lg border transform transition-all duration-500">
                  <div class="p-6">
                    <div class="prose prose-slate max-w-none" v-html="section.renderedContent"></div>
                  </div>
                </div>
              </TransitionGroup>
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  </div>
</template>

<style>
@import 'katex/dist/katex.min.css';

.section-enter-active,
.section-leave-active {
  transition: all 0.5s ease;
}

.section-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.section-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.prose {
  @apply text-gray-800;
}

.prose h1 {
  @apply text-3xl font-bold mb-6 text-gray-900;
}

.prose h2 {
  @apply text-2xl font-semibold mt-4 mb-4 text-gray-800;
}

.prose h3 {
  @apply text-xl font-semibold mt-3 mb-3 text-gray-800;
}

.prose p {
  @apply mb-4 leading-relaxed;
}

.prose ul {
  @apply list-disc ml-6 mb-4 space-y-2;
}

.prose ol {
  @apply list-decimal ml-6 mb-4 space-y-2;
}

.prose blockquote {
  @apply border-l-4 border-gray-300 pl-4 italic my-4 text-gray-600;
}

.prose a {
  @apply text-blue-600 hover:text-blue-800 underline;
}

.prose hr {
  @apply my-8 border-gray-200;
}

.prose table {
  @apply w-full border-collapse my-6 !border-2 !border-gray-400;
}

.prose th {
  @apply !bg-gray-200 p-3 text-left !font-bold !text-gray-900 !border !border-gray-400;
}

.prose td {
  @apply p-3 !text-gray-900 !border !border-gray-400;
}

.prose tr {
  @apply !border !border-gray-400;
}

.prose tr:nth-child(even) {
  @apply !bg-gray-50;
}

.prose tr:hover {
  @apply !bg-gray-100;
}

.prose code {
  @apply bg-gray-100 px-1 py-0.5 rounded text-sm font-mono;
}

.prose pre {
  @apply bg-gray-100 p-4 rounded-lg overflow-x-auto my-4;
}

.prose pre code {
  @apply bg-transparent p-0;
}

.prose .math-block {
  @apply my-4 overflow-x-auto;
  text-align: center;
}

.prose .katex-display {
  @apply my-4 overflow-x-auto;
}

.prose .katex {
  font-size: 1.1em;
}
</style>