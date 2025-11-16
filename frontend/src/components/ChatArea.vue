<script setup lang="ts">
import Bubble from './Bubble.vue'
import SystemMessage from './SystemMessage.vue'
import StepTimeline from './StepTimeline.vue'
import { ref, computed, inject, type Ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, MessageSquare, ListTree } from 'lucide-vue-next'
import type { Message, StepMessage as StepMessageType } from '@/utils/response'

const props = defineProps<{ messages: Message[] }>()

// 注入调试模式
const debugMode = inject<Ref<boolean>>('debugMode', ref(false))

const inputValue = ref('')
const inputRef = ref<HTMLInputElement | null>(null)
const scrollRef = ref<HTMLDivElement | null>(null)

// 过滤出步骤消息
const stepMessages = computed(() => {
  return props.messages.filter(msg => msg.msg_type === 'step') as StepMessageType[]
})

// 过滤出非步骤消息（用于显示在聊天区）
const chatMessages = computed(() => {
  return props.messages.filter(msg => msg.msg_type !== 'step')
})

const sendMessage = () => {
  // 这里只处理本地 user 消息输入，如需和后端交互请在父组件处理
  if (!inputValue.value.trim()) return
  // 可以通过 emit 事件让父组件处理 user 消息
  inputValue.value = ''
  inputRef.value?.focus()
}
</script>

<template>
  <div class="flex h-full flex-col bg-background">
    <!-- 聊天区域标题 - Enhanced VSCode Style -->
    <div class="border-b border-border px-3 sm:px-4 py-2 sm:py-2.5 bg-background/90 backdrop-blur-sm shadow-sm">
      <div class="flex items-center justify-between">
        <h2 class="text-xs sm:text-sm font-semibold text-foreground flex items-center gap-2">
          <MessageSquare class="w-4 h-4 text-primary" />
          <span>对话</span>
          <span class="text-[10px] font-medium text-muted-foreground bg-muted px-2 py-0.5 rounded-full">{{ chatMessages.length }}</span>
        </h2>
        
        <!-- 步骤数量提示（调试模式） -->
        <div v-if="debugMode && stepMessages.length > 0" class="flex items-center gap-1.5 text-[9px] sm:text-[10px] text-destructive bg-destructive/10 px-2 sm:px-2.5 py-1 rounded-lg border border-destructive/20">
          <ListTree class="w-3 h-3" />
          <span class="font-medium">{{ stepMessages.length }} 个步骤</span>
        </div>
      </div>
    </div>
    
    <!-- 消息列表 - Enhanced scroll and spacing with smooth transitions -->
    <div ref="scrollRef" class="flex-1 overflow-y-auto px-3 sm:px-4 md:px-6 py-3 sm:py-4 space-y-2 scroll-smooth">
      <!-- Empty state with enhanced design -->
      <div v-if="chatMessages.length === 0 && !debugMode" class="flex flex-col items-center justify-center h-full text-muted-foreground animate-in fade-in-50 duration-300">
        <div class="relative mb-4 sm:mb-6">
          <MessageSquare class="w-16 h-16 sm:w-20 sm:h-20 opacity-20" />
          <div class="absolute inset-0 animate-pulse">
            <MessageSquare class="w-16 h-16 sm:w-20 sm:h-20 opacity-10" />
          </div>
        </div>
        <p class="text-base sm:text-lg font-semibold text-foreground">暂无消息</p>
        <p class="text-xs sm:text-sm mt-2 text-muted-foreground">开始对话吧 ✨</p>
      </div>
      
      <!-- Debug mode: Step timeline with enhanced design -->
      <div v-if="debugMode && stepMessages.length > 0" class="mb-4 animate-in slide-in-from-top-2 duration-300">
        <div class="bg-destructive/10 border-2 border-destructive/20 rounded-xl overflow-hidden shadow-sm">
          <div class="px-3 sm:px-4 py-2.5 sm:py-3 border-b border-destructive/20 bg-destructive/10">
            <div class="flex items-center gap-2">
              <ListTree class="w-4 h-4 sm:w-5 sm:h-5 text-destructive" />
              <span class="text-xs sm:text-sm font-bold text-destructive">执行步骤时间线</span>
              <span class="text-[9px] sm:text-[10px] text-destructive ml-auto bg-destructive/20 px-2 py-0.5 rounded-full font-semibold">共 {{ stepMessages.length }} 步</span>
            </div>
          </div>
          <StepTimeline :steps="stepMessages" />
        </div>
      </div>
      
      <!-- Messages with smooth animations -->
      <transition-group name="message-list" tag="div" class="space-y-2">
        <template v-for="message in chatMessages" :key="message.id">
          <!-- 用户消息 -->
          <div v-if="message.msg_type === 'user'" class="message-animate">
            <Bubble type="user" :content="message.content || ''" :message="message" />
          </div>
          <!-- agent 消息（CoderAgent/WriterAgent，只显示 content） -->
          <div v-else-if="message.msg_type === 'agent'" class="message-animate">
            <Bubble type="agent" :agentType="message.agent_type"
              :content="message.content || ''" :message="message" />
          </div>
          <!-- 工具消息 -->
          <div v-else-if="message.msg_type === 'tool'" class="message-animate">
            <Bubble type="tool" 
              :content="message.content || '工具调用'" :message="message" />
          </div>
          <!-- 系统消息 -->
          <div v-else-if="message.msg_type === 'system'" class="message-animate">
            <SystemMessage :content="message.content || ''"
              :type="message.type" />
          </div>
        </template>
      </transition-group>
    </div>
    
    <!-- Input area - Enhanced mobile optimization -->
    <div class="border-t border-border bg-background p-2.5 sm:p-3 shadow-sm">
      <form class="w-full flex items-center gap-2" @submit.prevent="sendMessage">
        <Input
          ref="inputRef"
          v-model="inputValue"
          type="text"
          placeholder="输入消息..."
          class="flex-1 text-xs sm:text-sm h-8 sm:h-9 rounded-lg transition-all"
          autocomplete="off"
        />
        <Button
          type="submit"
          :disabled="!inputValue.trim()"
          class="h-8 sm:h-9 px-3 sm:px-4 text-xs sm:text-sm shadow-sm hover:shadow transition-all"
          size="sm"
        >
          <Send class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          <span class="hidden sm:inline ml-1.5 font-medium">发送</span>
        </Button>
      </form>
    </div>
  </div>
</template>

