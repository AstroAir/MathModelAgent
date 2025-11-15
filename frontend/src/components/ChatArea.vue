<script setup lang="ts">
import Bubble from './Bubble.vue'
import SystemMessage from './SystemMessage.vue'
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, MessageSquare } from 'lucide-vue-next'
import type { Message } from '@/utils/response'

const props = defineProps<{ messages: Message[] }>()

const inputValue = ref('')
const inputRef = ref<HTMLInputElement | null>(null)
const scrollRef = ref<HTMLDivElement | null>(null)

const sendMessage = () => {
  // 这里只处理本地 user 消息输入，如需和后端交互请在父组件处理
  if (!inputValue.value.trim()) return
  // 可以通过 emit 事件让父组件处理 user 消息
  inputValue.value = ''
  inputRef.value?.focus()
}
</script>

<template>
  <div class="flex h-full flex-col bg-gradient-to-b from-gray-50 to-white">
    <!-- 聊天区域标题 - 移动端优化 -->
    <div class="border-b px-3 sm:px-4 md:px-6 py-3 sm:py-4 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 backdrop-blur-sm shadow-sm">
      <div class="flex items-center justify-between">
        <h2 class="text-base sm:text-lg font-semibold text-gray-900 flex items-center gap-2">
          <MessageSquare class="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
          <span class="hidden sm:inline">对话记录</span>
          <span class="sm:hidden">对话</span>
        </h2>
        <div class="text-xs text-gray-500">
          {{ props.messages.length }} 条消息
        </div>
      </div>
    </div>
    
    <!-- 消息列表 - 优化滚动和间距 -->
    <div ref="scrollRef" class="flex-1 overflow-y-auto px-2 sm:px-4 md:px-6 py-3 sm:py-4 space-y-2 sm:space-y-3">
      <!-- 空状态提示 -->
      <div v-if="props.messages.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400">
        <MessageSquare class="w-12 h-12 sm:w-16 sm:h-16 mb-3 sm:mb-4 opacity-30" />
        <p class="text-sm sm:text-base">暂无消息</p>
        <p class="text-xs sm:text-sm mt-1 sm:mt-2">开始对话吧</p>
      </div>
      
      <template v-for="message in props.messages" :key="message.id">
        <!-- 用户消息 -->
        <Bubble v-if="message.msg_type === 'user'" type="user" :content="message.content || ''" :message="message" />
        <!-- agent 消息（CoderAgent/WriterAgent，只显示 content） -->
        <Bubble v-else-if="message.msg_type === 'agent'" type="agent" :agentType="message.agent_type"
          :content="message.content || ''" :message="message" />
        <!-- 工具消息 -->
        <Bubble v-else-if="message.msg_type === 'tool'" type="tool" 
          :content="message.content || '工具调用'" :message="message" />
        <!-- 系统消息 -->
        <SystemMessage v-else-if="message.msg_type === 'system'" :content="message.content || ''"
          :type="message.type" />
      </template>
    </div>
    
    <!-- 输入区域 - 移动端优化 -->
    <div class="border-t bg-white/80 backdrop-blur-sm p-2 sm:p-3 md:p-4 shadow-lg">
      <form class="w-full flex items-center gap-2" @submit.prevent="sendMessage">
        <Input 
          ref="inputRef" 
          v-model="inputValue" 
          type="text" 
          placeholder="输入消息..." 
          class="flex-1 shadow-sm text-sm sm:text-base h-9 sm:h-10" 
          autocomplete="off" 
        />
        <Button 
          type="submit" 
          :disabled="!inputValue.trim()" 
          class="shadow-md hover:shadow-lg transition-all h-9 sm:h-10 px-3 sm:px-4"
          size="sm"
        >
          <Send class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          <span class="hidden sm:inline ml-1.5">发送</span>
        </Button>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* 自定义滚动条样式 - 移动端友好 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

@media (max-width: 640px) {
  .overflow-y-auto::-webkit-scrollbar {
    width: 3px;
  }
}

.overflow-y-auto::-webkit-scrollbar-track {
  @apply bg-gray-100/50;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  @apply bg-gradient-to-b from-blue-300 to-purple-300 rounded-full;
  transition: background 0.3s ease;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  @apply bg-gradient-to-b from-blue-400 to-purple-400;
}

/* 移动端优化 - 隐藏滚动条但保持功能 */
@media (max-width: 640px) {
  .overflow-y-auto {
    -webkit-overflow-scrolling: touch;
  }
}

/* 平滑滚动 */
.overflow-y-auto {
  scroll-behavior: smooth;
}
</style>