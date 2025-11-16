<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { marked } from 'marked'
import markedKatex from 'marked-katex-extension'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import javascript from 'highlight.js/lib/languages/javascript'
import json from 'highlight.js/lib/languages/json'
import 'highlight.js/styles/github-dark.css'
import 'katex/dist/katex.min.css'
import { computed, ref, inject, type Ref } from 'vue'
import { AgentType } from '@/utils/enum'
import { ChevronDown, ChevronRight, Copy, Check } from 'lucide-vue-next'
import type { Message, ToolMessage } from '@/utils/response'
import DebugPanel from './DebugPanel.vue'

// 注册代码高亮语言
hljs.registerLanguage('python', python)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('json', json)

interface BubbleProps {
  type: 'agent' | 'user' | 'tool'
  agentType?: AgentType
  class?: HTMLAttributes['class']
  content?: string
  message?: Message  // 完整的消息对象，用于显示工具调用
}

const props = withDefaults(defineProps<BubbleProps>(), {
  type: 'user'
})

// 注入调试模式状态
const debugMode = inject<Ref<boolean>>('debugMode', ref(false))

const isCollapsed = ref(false)
const isToolExpanded = ref(false)
const copied = ref(false)

// 配置marked选项
marked.use({
  breaks: true,
  gfm: true
})

// 添加KaTeX数学公式支持
marked.use(markedKatex({
  throwOnError: false
}))

const renderedContent = computed(() => {
  if (!props.content) return ''
  let html = marked.parse(props.content) as string
  
  // 对代码块进行高亮处理
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const codeBlocks = doc.querySelectorAll('pre code')
  
  codeBlocks.forEach((block) => {
    const codeElement = block as HTMLElement
    const code = codeElement.textContent || ''
    const classList = Array.from(codeElement.classList)
    const langClass = classList.find(cls => cls.startsWith('language-'))
    const language = langClass ? langClass.replace('language-', '') : 'plaintext'
    
    try {
      const validLanguage = hljs.getLanguage(language) ? language : 'plaintext'
      const highlighted = hljs.highlight(code, { language: validLanguage }).value
      codeElement.innerHTML = highlighted
      codeElement.classList.add('hljs')
    } catch (e) {
      console.error('Highlight error:', e)
    }
  })
  
  return doc.body.innerHTML
})

// 判断是否为工具消息
const isToolMessage = computed(() => {
  return props.message && props.message.msg_type === 'tool'
})

// 获取工具消息详情
const toolMessage = computed(() => {
  if (isToolMessage.value) {
    return props.message as ToolMessage
  }
  return null
})

// 获取工具名称显示
const toolDisplayName = computed(() => {
  if (!toolMessage.value) return ''
  switch (toolMessage.value.tool_name) {
    case 'execute_code':
      return '代码执行'
    case 'search_scholar':
      return '学术搜索'
    default:
      return toolMessage.value.tool_name
  }
})

// 切换折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleToolExpand = () => {
  isToolExpanded.value = !isToolExpanded.value
}

// 复制内容功能
const copyContent = async () => {
  if (!props.content) return
  try {
    await navigator.clipboard.writeText(props.content)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// 获取消息时间戳
const messageTime = computed(() => {
  const msg = props.message as any
  if (!msg?.timestamp) return ''
  const date = new Date(msg.timestamp)
  return date.toLocaleString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  })
})
</script>

<template>
  <div class="message-item flex gap-1.5 py-1 px-2 hover:bg-accent/50 transition-colors duration-150 group">
    <!-- 左侧：项目符号/图标 - 移动端优化 -->
    <div class="flex-shrink-0 mt-0.5">
      <div class="w-1.5 h-1.5 rounded-full" :class="{
        'bg-primary': props.type === 'user',
        'bg-green-500': props.type === 'agent' && props.agentType === 'CoderAgent',
        'bg-purple-500': props.type === 'agent' && props.agentType === 'WriterAgent',
        'bg-orange-500': props.type === 'tool'
      }"></div>
    </div>

    <!-- 右侧：内容 -->
    <div class="flex-1 min-w-0">
      <!-- 消息头：类型标签 + 操作按钮 -->
      <div class="flex items-start justify-between gap-1 mb-1">
        <div class="flex items-center gap-1 flex-wrap">
          <!-- 消息类型标签 - 移动端优化 -->
          <span v-if="props.type === 'user'" class="text-[9px] font-semibold text-primary px-1.5 py-0.5 bg-primary/10 rounded">User</span>
          <span v-else-if="props.type === 'tool'" class="text-[9px] font-semibold text-orange-600 flex items-center gap-0.5 px-1.5 py-0.5 bg-orange-500/10 rounded">
            {{ toolDisplayName }}
          </span>
          <span v-else-if="props.type === 'agent' && props.agentType === 'CoderAgent'"
            class="text-[9px] font-semibold text-green-600 px-1.5 py-0.5 bg-green-500/10 rounded">Coder</span>
          <span v-else-if="props.type === 'agent' && props.agentType === 'WriterAgent'"
            class="text-[9px] font-semibold text-purple-600 px-1.5 py-0.5 bg-purple-500/10 rounded">Writer</span>
          
          <!-- 调试模式显示时间戳 -->
          <span v-if="debugMode && messageTime" class="text-[8px] text-muted-foreground font-mono px-1 py-0.5 bg-muted rounded">
            {{ messageTime }}
          </span>
        </div>

        <!-- 操作按钮组 -->
        <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
          <!-- 复制按钮 -->
          <button
            v-if="props.content"
            @click="copyContent"
            class="p-0.5 rounded hover:bg-accent transition-colors"
            :title="copied ? '已复制' : '复制内容'"
          >
            <Check v-if="copied" class="w-3 h-3 text-green-500" />
            <Copy v-else class="w-3 h-3 text-muted-foreground" />
          </button>

          <!-- 折叠按钮 -->
          <button
            v-if="props.content && props.content.length > 300"
            @click="toggleCollapse"
            class="p-0.5 rounded hover:bg-accent transition-colors"
            :title="isCollapsed ? '展开' : '折叠'"
          >
            <ChevronDown v-if="!isCollapsed" class="w-3 h-3 text-muted-foreground" />
            <ChevronRight v-else class="w-3 h-3 text-muted-foreground" />
          </button>
        </div>
      </div>
      
      <!-- 消息内容 - 移动端字体优化 -->
      <div v-if="!isCollapsed" class="text-sm text-foreground leading-relaxed break-words">
        <div v-if="props.content" v-html="renderedContent" class="prose prose-sm max-w-none"></div>

        <!-- 调试模式：使用DebugPanel组件显示详细调试信息 -->
        <DebugPanel v-if="debugMode && props.message" :message="props.message" :agentType="props.agentType" />

        <!-- 工具调用详情 -->
        <div v-if="isToolMessage && toolMessage" class="mt-2">
          <button
            @click="toggleToolExpand"
            class="flex items-center gap-1 text-[9px] text-muted-foreground hover:text-orange-500 transition-colors"
          >
            <ChevronRight :class="['w-2.5 h-2.5 transition-transform', isToolExpanded ? 'rotate-90' : '']" />
            <span>{{ isToolExpanded ? '隐藏详情' : '查看详情' }}</span>
          </button>

          <!-- 工具输入输出 - 移动端优化 -->
          <div v-if="isToolExpanded" class="mt-2 space-y-2 text-[9px] bg-muted rounded p-2 border border-border">
            <!-- 输入 -->
            <div v-if="toolMessage.input">
              <div class="font-semibold text-foreground mb-1">输入参数:</div>
              <pre class="text-[8px] bg-background p-2 rounded border-border overflow-x-auto max-h-32 overflow-y-auto">{{ JSON.stringify(toolMessage.input, null, 2) }}</pre>
            </div>

            <!-- 输出预览 -->
            <div v-if="toolMessage.output">
              <div class="font-semibold text-foreground mb-1">输出结果:</div>
              <div class="text-muted-foreground bg-background p-2 rounded border-border max-h-32 overflow-y-auto">
                {{ Array.isArray(toolMessage.output) ? `${toolMessage.output.length} 条结果` : '查看结果' }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 折叠状态的预览 - 移动端优化 -->
      <div v-else class="text-sm text-muted-foreground cursor-pointer hover:text-foreground transition-colors" @click="toggleCollapse">
        {{ props.content?.substring(0, 80) }}...
      </div>
    </div>
  </div>
</template>

<style>
/* Prose基础样式 */
.prose {
  @apply text-inherit;
  color: inherit;
}

.prose p {
  @apply my-2;
  line-height: 1.6;
}

.prose h1,
.prose h2,
.prose h3,
.prose h4 {
  @apply my-3 font-semibold text-foreground;
}

.prose h1 {
  @apply text-xl sm:text-2xl border-b-2 border-border pb-2;
}

.prose h2 {
  @apply text-lg sm:text-xl border-b border-border pb-1;
}

.prose h3 {
  @apply text-base sm:text-lg;
}

.prose h4 {
  @apply text-sm sm:text-base;
}

.prose ul,
.prose ol {
  @apply my-2 pl-5 sm:pl-6;
}

.prose ul {
  @apply list-disc;
}

.prose ol {
  @apply list-decimal;
}

.prose li {
  @apply my-1;
  line-height: 1.6;
}

/* 行内代码 */
.prose code:not(.hljs) {
  @apply px-1.5 py-0.5 rounded text-xs sm:text-sm bg-muted text-destructive font-mono font-medium;
}

/* 代码块容器 */
.prose pre {
  @apply my-3 rounded-lg overflow-hidden shadow-sm bg-gray-800 border border-border;
}

.dark .prose pre {
  @apply bg-gray-900;
}

.prose pre code.hljs {
  @apply p-3 sm:p-4 block overflow-x-auto text-xs sm:text-sm bg-transparent text-gray-200;
  line-height: 1.6;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  max-height: 500px;
  overflow-y: auto;
}

/* 滚动条样式 */
.prose pre code.hljs::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.prose pre code.hljs::-webkit-scrollbar-track {
  @apply bg-muted rounded-md;
}

.prose pre code.hljs::-webkit-scrollbar-thumb {
  @apply bg-border rounded-md;
}

.prose pre code.hljs::-webkit-scrollbar-thumb:hover {
  @apply bg-border/80;
}

.prose blockquote {
  @apply my-3 pl-4 border-l-4 italic border-primary bg-muted p-4 rounded-md;
}

.prose a {
  @apply underline underline-offset-2 text-primary hover:text-primary/80 transition-colors;
}

.prose img {
  @apply my-3 rounded-lg shadow-md max-w-full h-auto;
}

/* 表格样式 */
.prose table {
  @apply my-3 w-full border-collapse border border-border rounded-lg overflow-hidden;
}

.prose thead {
  @apply bg-muted;
}

.prose thead tr {
  @apply border-b-2 border-border;
}

.prose th {
  @apply p-2 sm:p-3 text-left font-semibold text-xs sm:text-sm text-foreground;
}

.prose td {
  @apply p-2 sm:p-3 text-xs sm:text-sm border-t border-border text-muted-foreground;
}

.prose tbody tr:hover {
  @apply bg-accent;
}

/* KaTeX数学公式样式 */
.prose .katex {
  font-size: 1.1em;
}

.prose .katex-display {
  @apply my-3;
  overflow-x: auto;
  overflow-y: hidden;
}


</style>