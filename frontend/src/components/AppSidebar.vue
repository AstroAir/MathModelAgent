<script setup lang="ts">
import { QQ_GROUP, TWITTER, GITHUB_LINK, BILLBILL, XHS, DISCORD } from '@/utils/const'
import NavUser from './NavUser.vue'
import { ref, onMounted, computed } from 'vue'
import { 
  getTaskHistoryList, 
  toggleTaskPin, 
  deleteTaskHistory 
} from '@/apis/historyApi'
import type { TaskHistoryItem } from '@/types/history'
import { 
  Pin, 
  PinOff, 
  Trash2, 
  Plus, 
  FileText, 
  Package, 
  Loader2,
  CheckCircle2,
  XCircle,
  Clock
} from 'lucide-vue-next'

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  type SidebarProps,
  SidebarRail,
} from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { ScrollArea } from '@/components/ui/scroll-area'

const props = defineProps<SidebarProps>()

// 历史记录相关状态
const historyTasks = ref<TaskHistoryItem[]>([])
const loading = ref(false)
const activeFilter = ref<'all' | 'custom' | 'example' | 'pinned'>('all')

// 过滤后的任务列表
const filteredTasks = computed(() => {
  switch (activeFilter.value) {
    case 'custom':
      return historyTasks.value.filter(task => task.task_type === 'custom')
    case 'example':
      return historyTasks.value.filter(task => task.task_type === 'example')
    case 'pinned':
      return historyTasks.value.filter(task => task.is_pinned)
    default:
      return historyTasks.value
  }
})

// 加载历史记录
const loadHistory = async () => {
  loading.value = true
  try {
    const response = await getTaskHistoryList()
    historyTasks.value = response.tasks
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 切换收藏状态
const handleTogglePin = async (taskId: string, event: MouseEvent) => {
  event.stopPropagation()
  try {
    await toggleTaskPin(taskId)
    await loadHistory()
  } catch (error) {
    console.error('切换收藏状态失败:', error)
  }
}

// 删除任务
const handleDelete = async (taskId: string, event: MouseEvent) => {
  event.stopPropagation()
  if (confirm('确定要删除这个任务吗？')) {
    try {
      await deleteTaskHistory(taskId)
      await loadHistory()
    } catch (error) {
      console.error('删除任务失败:', error)
    }
  }
}

// 获取状态图标
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'completed':
      return CheckCircle2
    case 'failed':
      return XCircle
    case 'processing':
      return Loader2
    default:
      return Clock
  }
}

// 获取状态颜色类
const getStatusColorClass = (status: string) => {
  switch (status) {
    case 'completed':
      return 'text-green-600'
    case 'failed':
      return 'text-red-600'
    case 'processing':
      return 'text-blue-600 animate-spin'
    default:
      return 'text-gray-600'
  }
}

// 格式化时间
const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    const hours = Math.floor(diff / (1000 * 60 * 60))
    if (hours === 0) {
      const minutes = Math.floor(diff / (1000 * 60))
      return minutes === 0 ? '刚刚' : `${minutes}分钟前`
    }
    return `${hours}小时前`
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  }
}

// 页面挂载时加载历史记录
onMounted(() => {
  loadHistory()
})

const socialMedia = [
  {
    name: 'QQ',
    url: QQ_GROUP,
    icon: '/qq.svg',
  },
  {
    name: 'Twitter',
    url: TWITTER,
    icon: '/twitter.svg',
  },
  {
    name: 'GitHub',
    url: GITHUB_LINK,
    icon: '/github.svg',
  },
  {
    name: '哔哩哔哩',
    url: BILLBILL,
    icon: '/bilibili.svg',
  },
  {
    name: '小红书',
    url: XHS,
    icon: '/xiaohongshu.svg',
  },
  {
    name: 'Discord',
    url: DISCORD,
    icon: '/discord.svg',
  },
]

</script>

<template>
  <Sidebar v-bind="props" class="flex flex-col h-full">
    <SidebarHeader class="shrink-0">
      <!-- Logo -->
      <div class="flex items-center gap-2 h-15 px-2">
        <router-link to="/" class="flex items-center gap-2">
          <img src="@/assets/icon.png" alt="logo" class="w-10 h-10">
          <div class="text-lg font-bold">MathModelAgent</div>
        </router-link>
      </div>
    </SidebarHeader>
    
    <SidebarContent class="flex-1 flex flex-col min-h-0">
      <!-- 新建任务按钮 -->
      <SidebarGroup class="shrink-0">
        <SidebarGroupContent class="px-2">
          <Button class="w-full" variant="default" size="sm" @click="$router.push('/chat')">
            <Plus class="w-4 h-4 mr-2" />
            开始新任务
          </Button>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- 筛选器 -->
      <SidebarGroup class="shrink-0">
        <SidebarGroupLabel>筛选</SidebarGroupLabel>
        <SidebarGroupContent>
          <div class="flex flex-wrap gap-1 px-2">
            <Button 
              variant="ghost" 
              size="sm" 
              :class="activeFilter === 'all' ? 'bg-accent' : ''"
              @click="activeFilter = 'all'"
              class="text-xs"
            >
              全部
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              :class="activeFilter === 'pinned' ? 'bg-accent' : ''"
              @click="activeFilter = 'pinned'"
              class="text-xs"
            >
              <Pin class="w-3 h-3 mr-1" />
              收藏
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              :class="activeFilter === 'custom' ? 'bg-accent' : ''"
              @click="activeFilter = 'custom'"
              class="text-xs"
            >
              <FileText class="w-3 h-3 mr-1" />
              自定义
            </Button>
            <Button 
              variant="ghost" 
              size="sm" 
              :class="activeFilter === 'example' ? 'bg-accent' : ''"
              @click="activeFilter = 'example'"
              class="text-xs"
            >
              <Package class="w-3 h-3 mr-1" />
              示例
            </Button>
          </div>
        </SidebarGroupContent>
      </SidebarGroup>

      <!-- 历史任务列表 -->
      <SidebarGroup class="flex-1 flex flex-col min-h-0">
        <SidebarGroupLabel class="flex items-center justify-between px-2 shrink-0">
          <span>历史任务</span>
          <Button variant="ghost" size="sm" @click="loadHistory" :disabled="loading" class="h-6 w-6 p-0">
            <Loader2 v-if="loading" class="w-3 h-3 animate-spin" />
            <span v-else class="text-xs">↻</span>
          </Button>
        </SidebarGroupLabel>
        <SidebarGroupContent class="flex-1 min-h-0">
          <ScrollArea class="h-full">
            <SidebarMenu>
              <!-- 加载中状态 -->
              <div v-if="loading" class="flex items-center justify-center py-8 text-muted-foreground">
                <Loader2 class="w-5 h-5 animate-spin" />
              </div>
              
              <!-- 空状态 -->
              <div v-else-if="filteredTasks.length === 0" class="px-4 py-8 text-center text-sm text-muted-foreground">
                <FileText class="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p>暂无{{ activeFilter === 'pinned' ? '收藏的' : '' }}任务</p>
              </div>
              
              <!-- 任务列表 -->
              <SidebarMenuItem v-for="task in filteredTasks" :key="task.task_id">
                <div class="group relative w-full">
                  <SidebarMenuButton
                    as-child
                    class="w-full cursor-pointer hover:bg-accent transition-colors"
                  >
                    <div class="flex items-start gap-2 py-2 px-2">
                      <!-- 状态图标 -->
                      <component 
                        :is="getStatusIcon(task.status)" 
                        :class="['w-4 h-4 mt-0.5 shrink-0', getStatusColorClass(task.status)]"
                      />
                      
                      <!-- 任务信息 -->
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-1 mb-1">
                          <Pin v-if="task.is_pinned" class="w-3 h-3 text-yellow-600 shrink-0" />
                          <h4 class="text-sm font-medium truncate">{{ task.title }}</h4>
                        </div>
                        <p class="text-xs text-muted-foreground line-clamp-2 mb-1">
                          {{ task.description }}
                        </p>
                        <div class="flex items-center gap-2 text-xs text-muted-foreground">
                          <span>{{ formatTime(task.created_at) }}</span>
                          <span v-if="task.file_count > 0">· {{ task.file_count }} 个文件</span>
                          <span class="px-1.5 py-0.5 rounded text-xs" :class="task.task_type === 'example' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'">
                            {{ task.task_type === 'example' ? '示例' : '自定义' }}
                          </span>
                        </div>
                      </div>
                      
                      <!-- 操作按钮 -->
                      <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                        <Button
                          variant="ghost"
                          size="sm"
                          class="h-6 w-6 p-0"
                          @click="(e: MouseEvent) => handleTogglePin(task.task_id, e)"
                        >
                          <component :is="task.is_pinned ? PinOff : Pin" class="w-3 h-3" />
                        </Button>
                        <DropdownMenu>
                          <DropdownMenuTrigger as-child>
                            <Button variant="ghost" size="sm" class="h-6 w-6 p-0" @click.stop>
                              <span>⋮</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem @click="(e: MouseEvent) => handleDelete(task.task_id, e)" class="text-red-600">
                              <Trash2 class="w-3 h-3 mr-2" />
                              删除
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  </SidebarMenuButton>
                </div>
              </SidebarMenuItem>
            </SidebarMenu>
          </ScrollArea>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    
    <SidebarRail />
    
    <SidebarFooter class="shrink-0">
      <NavUser />
      <!-- 社交媒体图标 -->
      <div class="flex items-center gap-4 justify-center mt-2 border-t border-light-purple pt-3">
        <a v-for="item in socialMedia" :key="item.name" :href="item.url" target="_blank" rel="noopener noreferrer">
          <img :src="item.icon" :alt="item.name" width="24" height="24" class="icon hover:opacity-70 transition-opacity">
        </a>
      </div>
    </SidebarFooter>
  </Sidebar>
</template>