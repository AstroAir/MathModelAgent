<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronRight, Bug, Code2, Clock, Hash, User } from 'lucide-vue-next'
import type { Message } from '@/utils/response'
import hljs from 'highlight.js/lib/core'
import json from 'highlight.js/lib/languages/json'


// 注册JSON语言
hljs.registerLanguage('json', json)

interface Props {
  message: Message
  agentType?: string
}

const props = defineProps<Props>()
const isExpanded = ref(false)

// 格式化时间戳
const formatTimestamp = (timestamp?: string | number) => {
  if (!timestamp) return '未知时间'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }) + '.' + String(date.getMilliseconds()).padStart(3, '0')
}

// JSON高亮
const highlightedJson = computed(() => {
  try {
    const jsonStr = JSON.stringify(props.message, null, 2)
    const highlighted = hljs.highlight(jsonStr, { language: 'json' }).value
    return highlighted
  } catch (e) {
    return JSON.stringify(props.message, null, 2)
  }
})

// 提取关键信息
const messageInfo = computed(() => {
  const msg = props.message as any
  return {
    id: msg.id || '无',
    msgType: msg.msg_type || '未知',
    agentType: msg.agent_type || props.agentType || '-',
    timestamp: msg.timestamp,
    contentLength: msg.content?.length || 0,
    toolName: msg.tool_name || '-',
    hasInput: !!msg.input,
    hasOutput: !!msg.output
  }
})

// 获取消息类型颜色
const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    user: 'text-primary bg-primary/10 border-primary/20',
    agent: 'text-green-600 bg-green-500/10 border-green-500/20',
    tool: 'text-orange-600 bg-orange-500/10 border-orange-500/20',
    system: 'text-purple-600 bg-purple-500/10 border-purple-500/20'
  }
  return colors[type] || 'text-muted-foreground bg-muted border-border'
}

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
  <div class="debug-panel mt-2 border border-border rounded-lg overflow-hidden bg-muted shadow-sm">
    <!-- 调试面板头部 -->
    <div
      @click="toggleExpand"
      class="flex items-center justify-between px-3 py-2 cursor-pointer hover:bg-accent transition-all duration-200 border-b border-border"
    >
      <div class="flex items-center gap-2">
        <Bug class="w-3.5 h-3.5 text-destructive" />
        <span class="text-[10px] font-bold text-foreground tracking-wide">调试信息</span>
        <span :class="['text-[8px] font-semibold px-1.5 py-0.5 rounded border', getTypeColor(messageInfo.msgType)]">
          {{ messageInfo.msgType }}
        </span>
      </div>
      <ChevronRight
        :class="['w-3.5 h-3.5 text-muted-foreground transition-transform duration-200', isExpanded ? 'rotate-90' : '']"
      />
    </div>

    <!-- 调试面板内容 -->
    <div v-if="isExpanded" class="bg-background">
      <!-- 关键信息概览 -->
      <div class="grid grid-cols-2 gap-2 px-3 py-2 bg-muted/50 border-b border-border">
        <!-- ID -->
        <div class="flex items-start gap-1.5">
          <Hash class="w-3 h-3 text-muted-foreground mt-0.5 flex-shrink-0" />
          <div class="min-w-0 flex-1">
            <div class="text-[8px] text-muted-foreground font-medium mb-0.5">消息ID</div>
            <div class="text-[9px] text-foreground font-mono truncate" :title="messageInfo.id">
              {{ messageInfo.id }}
            </div>
          </div>
        </div>

        <!-- 时间戳 -->
        <div class="flex items-start gap-1.5">
          <Clock class="w-3 h-3 text-muted-foreground mt-0.5 flex-shrink-0" />
          <div class="min-w-0 flex-1">
            <div class="text-[8px] text-muted-foreground font-medium mb-0.5">时间戳</div>
            <div class="text-[9px] text-foreground font-mono">
              {{ formatTimestamp(messageInfo.timestamp) }}
            </div>
          </div>
        </div>

        <!-- Agent类型 -->
        <div class="flex items-start gap-1.5">
          <User class="w-3 h-3 text-muted-foreground mt-0.5 flex-shrink-0" />
          <div class="min-w-0 flex-1">
            <div class="text-[8px] text-muted-foreground font-medium mb-0.5">Agent类型</div>
            <div class="text-[9px] text-foreground font-semibold">
              {{ messageInfo.agentType }}
            </div>
          </div>
        </div>

        <!-- 内容长度 -->
        <div class="flex items-start gap-1.5">
          <Code2 class="w-3 h-3 text-muted-foreground mt-0.5 flex-shrink-0" />
          <div class="min-w-0 flex-1">
            <div class="text-[8px] text-muted-foreground font-medium mb-0.5">内容长度</div>
            <div class="text-[9px] text-foreground font-mono">
              {{ messageInfo.contentLength }} 字符
            </div>
          </div>
        </div>

        <!-- 工具名称 (如果是工具消息) -->
        <div v-if="messageInfo.msgType === 'tool'" class="col-span-2 flex items-start gap-1.5">
          <Code2 class="w-3 h-3 text-orange-500 mt-0.5 flex-shrink-0" />
          <div class="min-w-0 flex-1">
            <div class="text-[8px] text-orange-600 font-medium mb-0.5">工具名称</div>
            <div class="text-[9px] text-orange-700 font-semibold">
              {{ messageInfo.toolName }}
            </div>
          </div>
        </div>
      </div>

      <!-- Agent步骤信息 (如果是agent消息) -->
      <div v-if="messageInfo.msgType === 'agent'" class="px-3 py-2 bg-green-500/10 border-b border-green-500/20">
        <div class="text-[9px] font-semibold text-green-700 mb-1.5 flex items-center gap-1">
          <div class="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
          Agent执行步骤
        </div>
        <div class="space-y-1">
          <div class="text-[8px] text-green-600 bg-background rounded px-2 py-1 border border-green-500/20">
            <span class="font-medium">步骤类型:</span> {{ messageInfo.agentType }}
          </div>
          <div v-if="messageInfo.contentLength > 0" class="text-[8px] text-green-600 bg-background rounded px-2 py-1 border border-green-500/20">
            <span class="font-medium">输出内容:</span> {{ messageInfo.contentLength }} 字符
          </div>
        </div>
      </div>

      <!-- 工具调用信息 (如果是工具消息) -->
      <div v-if="messageInfo.msgType === 'tool'" class="px-3 py-2 bg-orange-500/10 border-b border-orange-500/20">
        <div class="text-[9px] font-semibold text-orange-700 mb-1.5 flex items-center gap-1">
          <div class="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
          工具调用详情
        </div>
        <div class="space-y-1">
          <div class="text-[8px] text-orange-600 bg-background rounded px-2 py-1 border border-orange-500/20 flex items-center gap-1">
            <span class="font-medium">工具:</span> {{ messageInfo.toolName }}
            <span v-if="messageInfo.hasInput" class="ml-auto text-[7px] px-1 py-0.5 bg-orange-500/20 rounded">有输入</span>
            <span v-if="messageInfo.hasOutput" class="text-[7px] px-1 py-0.5 bg-orange-500/20 rounded">有输出</span>
          </div>
        </div>
      </div>

      <!-- 完整JSON数据 -->
      <div class="px-3 py-2">
        <div class="text-[9px] font-semibold text-foreground mb-1.5 flex items-center gap-1">
          <Code2 class="w-3 h-3 text-muted-foreground" />
          完整消息结构
        </div>
        <div class="bg-gray-900 dark:bg-black rounded-lg overflow-hidden border border-border shadow-inner">
          <pre class="text-[8px] p-3 overflow-x-auto max-h-64 overflow-y-auto custom-scrollbar"><code class="hljs" v-html="highlightedJson"></code></pre>
        </div>
      </div>
    </div>
  </div>
</template>


