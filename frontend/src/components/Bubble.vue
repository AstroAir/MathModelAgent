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
import { ChevronDown, ChevronRight, Bug, Copy, Check } from 'lucide-vue-next'
import type { Message, ToolMessage } from '@/utils/response'

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
  <div class="message-item flex gap-1.5 sm:gap-2 md:gap-3 py-1.5 sm:py-2 md:py-3 px-2 sm:px-3 md:px-4 hover:bg-slate-50/50 rounded-lg transition-all duration-200 group">
    <!-- 左侧：项目符号/图标 - 移动端优化 -->
    <div class="flex-shrink-0 mt-1">
      <div class="w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full shadow-sm" :class="{
        'bg-blue-500 shadow-blue-200': props.type === 'user',
        'bg-green-500 shadow-green-200': props.type === 'agent' && props.agentType === 'CoderAgent',
        'bg-purple-500 shadow-purple-200': props.type === 'agent' && props.agentType === 'WriterAgent',
        'bg-orange-500 shadow-orange-200': props.type === 'tool'
      }"></div>
    </div>
    
    <!-- 右侧：内容 -->
    <div class="flex-1 min-w-0">
      <!-- 消息头：类型标签 + 操作按钮 -->
      <div class="flex items-start justify-between gap-1.5 sm:gap-2 mb-1.5 sm:mb-2">
        <div class="flex items-center gap-1.5 sm:gap-2 flex-wrap">
          <!-- 消息类型标签 - 移动端优化 -->
          <span v-if="props.type === 'user'" class="text-[10px] sm:text-xs font-semibold text-blue-600 px-1.5 sm:px-2 py-0.5 bg-blue-50 rounded shadow-sm">User</span>
          <span v-else-if="props.type === 'tool'" class="text-[10px] sm:text-xs font-semibold text-orange-600 flex items-center gap-1 px-1.5 sm:px-2 py-0.5 bg-orange-50 rounded shadow-sm">
            {{ toolDisplayName }}
          </span>
          <span v-else-if="props.type === 'agent' && props.agentType === 'CoderAgent'" 
            class="text-[10px] sm:text-xs font-semibold text-green-600 px-1.5 sm:px-2 py-0.5 bg-green-50 rounded shadow-sm">Coder Agent</span>
          <span v-else-if="props.type === 'agent' && props.agentType === 'WriterAgent'" 
            class="text-[10px] sm:text-xs font-semibold text-purple-600 px-1.5 sm:px-2 py-0.5 bg-purple-50 rounded shadow-sm">Writer Agent</span>
          
          <!-- 调试模式显示时间戳 -->
          <span v-if="debugMode && messageTime" class="text-[9px] sm:text-[10px] text-gray-400 font-mono px-1.5 py-0.5 bg-gray-50 rounded border border-gray-200">
            {{ messageTime }}
          </span>
        </div>
        
        <!-- 操作按钮组 -->
        <div class="flex items-center gap-1 opacity-70 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
          <!-- 复制按钮 -->
          <button 
            v-if="props.content"
            @click="copyContent"
            class="p-1 rounded hover:bg-gray-200 transition-all active:scale-95 touch-manipulation"
            :title="copied ? '已复制' : '复制内容'"
          >
            <Check v-if="copied" class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-green-500" />
            <Copy v-else class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-gray-500" />
          </button>
          
          <!-- 折叠按钮 -->
          <button 
            v-if="props.content && props.content.length > 300"
            @click="toggleCollapse"
            class="p-1 rounded hover:bg-gray-200 transition-all active:scale-95 touch-manipulation"
            :title="isCollapsed ? '展开' : '折叠'"
          >
            <ChevronDown v-if="!isCollapsed" class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-gray-500" />
            <ChevronRight v-else class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-gray-500" />
          </button>
        </div>
      </div>
      
      <!-- 消息内容 - 移动端字体优化 -->
      <div v-if="!isCollapsed" class="text-xs sm:text-sm text-gray-700 leading-relaxed break-words">
        <div v-if="props.content" v-html="renderedContent" class="prose prose-sm max-w-none"></div>
        
        <!-- 调试模式：显示原始消息 -->
        <div v-if="debugMode && props.message" class="mt-3 p-2 sm:p-3 bg-gray-900 rounded-lg border border-gray-700">
          <div class="flex items-center gap-1.5 mb-2">
            <Bug class="w-3 h-3 text-yellow-400" />
            <span class="text-[10px] sm:text-xs font-semibold text-yellow-400">调试信息</span>
          </div>
          <pre class="text-[9px] sm:text-[10px] text-gray-300 overflow-x-auto max-h-40 overflow-y-auto font-mono">{{ JSON.stringify(props.message, null, 2) }}</pre>
        </div>
        
        <!-- 工具调用详情 -->
        <div v-if="isToolMessage && toolMessage" class="mt-2 sm:mt-3">
          <button 
            @click="toggleToolExpand"
            class="flex items-center gap-1 sm:gap-1.5 text-[10px] sm:text-xs text-gray-500 hover:text-orange-600 transition-colors active:scale-95 touch-manipulation"
          >
            <ChevronRight :class="['w-2.5 h-2.5 sm:w-3 sm:h-3 transition-transform', isToolExpanded ? 'rotate-90' : '']" />
            <span>{{ isToolExpanded ? '隐藏详情' : '查看详情' }}</span>
          </button>
          
          <!-- 工具输入输出 - 移动端优化 -->
          <div v-if="isToolExpanded" class="mt-2 sm:mt-3 space-y-2 sm:space-y-3 text-[10px] sm:text-xs bg-gray-50 rounded-lg p-2 sm:p-3 md:p-4 border border-gray-200">
            <!-- 输入 -->
            <div v-if="toolMessage.input">
              <div class="font-semibold text-gray-700 mb-1 sm:mb-2">输入参数:</div>
              <pre class="text-[10px] sm:text-xs bg-white p-2 sm:p-3 rounded border overflow-x-auto max-h-40 sm:max-h-60 overflow-y-auto">{{ JSON.stringify(toolMessage.input, null, 2) }}</pre>
            </div>
            
            <!-- 输出预览 -->
            <div v-if="toolMessage.output">
              <div class="font-semibold text-gray-700 mb-1 sm:mb-2">输出结果:</div>
              <div class="text-gray-600 bg-white p-2 sm:p-3 rounded border max-h-40 sm:max-h-60 overflow-y-auto">
                {{ Array.isArray(toolMessage.output) ? `${toolMessage.output.length} 条结果` : '查看结果' }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 折叠状态的预览 - 移动端优化 -->
      <div v-else class="text-xs sm:text-sm text-gray-500 cursor-pointer hover:text-gray-700 transition-colors active:opacity-70" @click="toggleCollapse">
        {{ props.content?.substring(0, 100) }}<span class="hidden sm:inline">{{ props.content?.substring(100, 150) }}</span>...
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
  @apply my-3 font-semibold;
  color: #1f2937;
}

.prose h1 {
  @apply text-xl sm:text-2xl;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.prose h2 {
  @apply text-lg sm:text-xl;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.25rem;
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
  @apply px-1.5 py-0.5 rounded text-xs sm:text-sm;
  background: #f3f4f6;
  color: #dc2626;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-weight: 500;
}

/* 代码块容器 */
.prose pre {
  @apply my-3 rounded-lg overflow-hidden shadow-sm;
  background: #1e293b !important;
  border: 1px solid #334155;
}

.prose pre code.hljs {
  @apply p-3 sm:p-4 block overflow-x-auto text-xs sm:text-sm;
  background: transparent !important;
  color: #e2e8f0;
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
  background: #334155;
  border-radius: 4px;
}

.prose pre code.hljs::-webkit-scrollbar-thumb {
  background: #64748b;
  border-radius: 4px;
}

.prose pre code.hljs::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.prose blockquote {
  @apply my-3 pl-4 border-l-4 italic;
  border-color: #3b82f6;
  color: #4b5563;
  background: #f9fafb;
  padding: 0.75rem 1rem;
  border-radius: 0.25rem;
}

.prose a {
  @apply underline underline-offset-2;
  color: #3b82f6;
  transition: color 0.2s;
}

.prose a:hover {
  color: #2563eb;
}

.prose img {
  @apply my-3 rounded-lg shadow-md;
  max-width: 100%;
  height: auto;
}

/* 表格样式 */
.prose table {
  @apply my-3 w-full border-collapse;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.prose thead {
  background: #f3f4f6;
}

.prose thead tr {
  border-bottom: 2px solid #d1d5db;
}

.prose th {
  @apply p-2 sm:p-3 text-left font-semibold text-xs sm:text-sm;
  color: #374151;
}

.prose td {
  @apply p-2 sm:p-3 text-xs sm:text-sm;
  border-top: 1px solid #e5e7eb;
  color: #4b5563;
}

.prose tbody tr:hover {
  background: #f9fafb;
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

.prose-invert {
  @apply text-primary-foreground;
}

/* 确保透明度样式不会被继承 */
.prose thead *,
.prose td * {
  @apply opacity-100;
}

.bubble {
  display: flex;
  flex: 1 1 0%;
}

.bubble-user {
  justify-content: flex-end;
}

.bubble-coder,
.bubble-writer {
  justify-content: flex-start;
}

/* 用户气泡颜色 */
.bubble-user .prose {
  background: #2563eb;
  /* 蓝色 */
  color: #fff;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.08);
  border: 1px solid #2563eb;
}

/* CoderAgent 气泡颜色 */
.bubble-coder .prose {
  background: #f1f5f9;
  /* 浅灰 */
  color: #0f172a;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.08);
}

/* WriterAgent 气泡颜色 */
.bubble-writer .prose {
  background: #fef9c3;
  /* 浅黄 */
  color: #92400e;
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.08);
}

/* 消息动画 */
@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-animate {
  animation: messageSlideIn 0.3s ease-out;
}

/* 头像容器样式 */
.avatar-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2px;
}

.bubble-user .avatar-container {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
}

.bubble-coder .avatar-container {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.bubble-writer .avatar-container {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}
</style>