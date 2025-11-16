<script setup lang="ts">
import { ref, watch, computed } from 'vue';
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
  <div class="h-full flex flex-col bg-background">
    <div class="h-full">
      <div class="border-b border-border bg-purple-500/10 px-3 py-2">
        <h2 class="text-sm font-semibold text-foreground flex items-center gap-2">
          📝 论文内容
        </h2>
      </div>
      <div class="h-full pb-10">
        <ScrollArea class="h-full overflow-y-auto">
          <div class="p-3">
            <div class="overflow-y-auto space-y-3">
              <TransitionGroup name="section" tag="div" class="space-y-3">
                <div v-for="section in sortedSections" :key="section.id"
                  class="bg-card border-l-2 border-purple-500/50">
                  <div class="p-3">
                    <div class="prose prose-slate max-w-none prose-sm" v-html="section.renderedContent"></div>
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
  @apply text-foreground;
}

.prose h1 {
  @apply text-xl font-bold mb-3 text-foreground;
}

.prose h2 {
  @apply text-lg font-semibold mt-3 mb-2 text-foreground;
}

.prose h3 {
  @apply text-base font-semibold mt-2 mb-2 text-foreground;
}

.prose p {
  @apply mb-2 leading-relaxed text-sm;
}

.prose ul {
  @apply list-disc ml-6 mb-4 space-y-2;
}

.prose ol {
  @apply list-decimal ml-6 mb-4 space-y-2;
}

.prose blockquote {
  @apply border-l-4 border-border pl-4 italic my-4 text-muted-foreground;
}

.prose a {
  @apply text-primary hover:text-primary/80 underline;
}

.prose hr {
  @apply my-8 border-border;
}

.prose table {
  @apply w-full border-collapse my-6 !border-2 !border-border;
}

.prose th {
  @apply !bg-muted p-3 text-left !font-bold !text-foreground !border !border-border;
}

.prose td {
  @apply p-3 !text-foreground !border !border-border;
}


.prose tr:nth-child(even) {
  @apply !bg-muted/50;
}

.prose tr:hover {
  @apply !bg-accent;
}

.prose code {
  @apply bg-muted px-1 py-0.5 rounded text-sm font-mono;
}

.prose pre {
  @apply bg-muted p-4 rounded-lg overflow-x-auto my-4;
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