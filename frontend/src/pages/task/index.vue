<script setup lang="ts">
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import CoderEditor from '@/components/AgentEditor/CoderEditor.vue'
import WriterEditor from '@/components/AgentEditor/WriterEditor.vue'
import ModelerEditor from '@/components/AgentEditor/ModelerEditor.vue'
import ChatArea from '@/components/ChatArea.vue'
import WorkflowDialog from '@/components/WorkflowDialog.vue'
import { onMounted, onBeforeUnmount, ref, computed, provide } from 'vue'
import { useTaskStore } from '@/stores/task'
import { getWriterSeque } from '@/apis/commonApi';
import { Button } from '@/components/ui/button';
import FilesSheet from '@/pages/task/components/FileSheet.vue'
import { Brain, Code2, PenTool, Bug, Network, MessageSquare, GripVertical } from 'lucide-vue-next'
import Sortable from 'sortablejs'

// 调试模式状态
const debugMode = ref(false)
provide('debugMode', debugMode)

// 工作流程弹窗状态
const workflowDialogOpen = ref(false)

const props = defineProps<{ task_id: string }>()
const taskStore = useTaskStore()

const writerSequence = ref<string[]>([]);

// Agent状态管理
const agentStatuses = computed(() => [
  {
    name: 'Coordinator',
    status: (taskStore.coordinatorMessages?.length || 0) > 0 ? 'completed' as const : 'pending' as const,
    icon: '🎯',
    description: '任务协调与分析'
  },
  {
    name: 'ModelerAgent',
    status: (taskStore.modelerMessages?.length || 0) > 0 ? 'completed' as const : (taskStore.coordinatorMessages?.length || 0) > 0 ? 'running' as const : 'pending' as const,
    icon: '🧮',
    description: '建模方案设计'
  },
  {
    name: 'CoderAgent',
    status: (taskStore.coderMessages?.length || 0) > 0 ? 'completed' as const : (taskStore.modelerMessages?.length || 0) > 0 ? 'running' as const : 'pending' as const,
    icon: '👨‍💻',
    description: '代码实现与执行'
  },
  {
    name: 'WriterAgent',
    status: (taskStore.writerMessages?.length || 0) > 0 ? 'completed' as const : (taskStore.coderMessages?.length || 0) > 0 ? 'running' as const : 'pending' as const,
    icon: '✍️',
    description: '论文撰写'
  }
]);

// 项目运行时长相关
const startTime = ref<number>(Date.now())
const currentTime = ref<number>(Date.now())
let timer: ReturnType<typeof setInterval> | null = null

// 格式化运行时长
const formatDuration = (ms: number): string => {
  const seconds = Math.floor(ms / 1000)
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`
  } else {
    return `${remainingSeconds}s`
  }
}

// 计算运行时长
const runningDuration = ref<string>('0s')
const updateDuration = () => {
  currentTime.value = Date.now()
  runningDuration.value = formatDuration(currentTime.value - startTime.value)
}

console.log('Task ID:', props.task_id)

onMounted(async () => {
  taskStore.connectWebSocket(props.task_id)
  const res = await getWriterSeque();
  writerSequence.value = Array.isArray(res.data) ? res.data : [];

  // 开始计时
  timer = setInterval(updateDuration, 1000)
  updateDuration() // 立即更新一次
  
  // 初始化拖拽功能
  setTimeout(initDraggableTabs, 100)
})

onBeforeUnmount(() => {
  taskStore.closeWebSocket()
  // 清理计时器
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})

// Tab management
const currentTab = ref('modeler')
const tabsListRef = ref<HTMLElement | null>(null)
const tabs = ref([
  { value: 'modeler', label: 'Modeler', icon: Brain, color: 'blue' },
  { value: 'coder', label: 'Coder', icon: Code2, color: 'green' },
  { value: 'writer', label: 'Writer', icon: PenTool, color: 'purple' }
])

const initDraggableTabs = () => {
  if (!tabsListRef.value) return
  
  Sortable.create(tabsListRef.value, {
    animation: 200,
    handle: '.drag-handle',
    ghostClass: 'tab-ghost',
    chosenClass: 'tab-chosen',
    dragClass: 'tab-drag',
    onEnd: (evt) => {
      if (evt.oldIndex !== undefined && evt.newIndex !== undefined) {
        const newTabs = [...tabs.value]
        const [movedTab] = newTabs.splice(evt.oldIndex, 1)
        newTabs.splice(evt.newIndex, 0, movedTab)
        tabs.value = newTabs
      }
    }
  })
}
</script>

<template>
  <div class="fixed inset-0 bg-muted">
    <!-- 工作流程弹窗 -->
    <WorkflowDialog v-model:open="workflowDialogOpen" :agents="agentStatuses" />

    <!-- 桌面端布局 - VSCode风格 -->
    <div class="hidden md:flex h-full flex-col">
      <!-- 顶部工具栏 -->
      <div class="h-9 border-b border-border bg-background flex items-center justify-between px-3 shrink-0">
        <div class="flex items-center gap-2">
          <h1 class="text-sm font-medium text-foreground">
            MathModelAgent
          </h1>
          <div class="h-3 w-px bg-border"></div>
          <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
            <div class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
            <span class="font-mono font-medium">{{ runningDuration }}</span>
          </div>
        </div>

        <div class="flex items-center gap-1">
          <!-- 工作流程按钮 -->
          <Button
            @click="workflowDialogOpen = true"
            size="sm"
            variant="ghost"
            class="h-7 px-2 text-xs hover:bg-accent"
          >
            <Network class="w-3.5 h-3.5 mr-1" />
            <span>工作流程</span>
          </Button>

          <!-- 调试模式开关 -->
          <Button
            @click="debugMode = !debugMode"
            size="sm"
            variant="ghost"
            class="h-7 px-2 text-xs"
            :class="debugMode ? 'bg-destructive/10 text-destructive hover:bg-destructive/20' : 'hover:bg-accent'"
          >
            <Bug class="w-3.5 h-3.5" :class="debugMode ? 'mr-1' : ''" />
            <span v-if="debugMode">调试</span>
          </Button>

          <Button @click="taskStore.downloadMessages" size="sm" variant="ghost" class="h-7 px-2 text-xs hover:bg-accent">
            下载消息
          </Button>

          <FilesSheet />
        </div>
      </div>
      
      <!-- 主编辑区域 -->
      <div class="flex-1 overflow-hidden">
        <ResizablePanelGroup direction="horizontal" class="h-full">
          <!-- 左侧：对话区域 -->
          <ResizablePanel :default-size="40" :min-size="30" class="h-full">
            <div class="h-full bg-background border-r border-border flex flex-col">
              <div class="flex-1 overflow-hidden">
                <ChatArea :messages="taskStore.chatMessages" />
              </div>
              <!-- 调试模式指示器 -->
              <div v-if="debugMode" class="border-t border-border bg-destructive/10 px-3 py-1.5 flex items-center gap-2 text-xs text-destructive">
                <Bug class="w-3 h-3" />
                <span class="font-medium">调试模式</span>
                <span class="text-destructive/80">显示详细信息</span>
              </div>
            </div>
          </ResizablePanel>

          <ResizableHandle class="w-1 hover:bg-primary transition-colors" />
          
          <!-- 右侧：Agent编辑器 -->
          <ResizablePanel :default-size="60" :min-size="40" class="h-full min-w-0">
            <div class="flex h-full flex-col min-w-0 bg-background">
              <Tabs v-model="currentTab" class="w-full h-full flex flex-col">
                <!-- Agent切换标签栏 - Enhanced with drag-and-drop -->
                <div class="border-b border-border bg-muted flex items-center">
                  <TabsList ref="tabsListRef" class="h-9 bg-transparent border-0 p-0 space-x-0 rounded-none flex">
                    <TabsTrigger
                      v-for="tab in tabs"
                      :key="tab.value"
                      :value="tab.value"
                      class="vscode-tab group relative h-9 px-3 rounded-none border-r border-border bg-muted text-muted-foreground text-xs font-medium transition-all duration-200 hover:bg-background data-[state=active]:bg-background flex items-center gap-1.5"
                      :class="{
                        'data-[state=active]:text-primary': tab.color === 'blue',
                        'data-[state=active]:text-green-500': tab.color === 'green',
                        'data-[state=active]:text-purple-500': tab.color === 'purple'
                      }"
                    >
                      <GripVertical class="drag-handle w-3 h-3 opacity-0 group-hover:opacity-50 hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing" />
                      <component :is="tab.icon" class="w-3.5 h-3.5 transition-colors" />
                      <span>{{ tab.label }}</span>
                      <div
                        class="absolute bottom-0 left-0 right-0 h-0.5 transform scale-x-0 group-data-[state=active]:scale-x-100 transition-transform duration-200"
                        :class="{
                          'bg-primary': tab.color === 'blue',
                          'bg-green-500': tab.color === 'green',
                          'bg-purple-500': tab.color === 'purple'
                        }"
                      ></div>
                    </TabsTrigger>
                  </TabsList>
                </div>

                <TabsContent value="modeler" class="flex-1 p-0 min-w-0 h-full overflow-hidden animate-in fade-in-50 duration-200">
                  <ModelerEditor />
                </TabsContent>

                <TabsContent value="coder" class="flex-1 p-0 min-w-0 h-full overflow-hidden animate-in fade-in-50 duration-200">
                  <CoderEditor />
                </TabsContent>

                <TabsContent value="writer" class="flex-1 p-0 min-w-0 h-full overflow-hidden animate-in fade-in-50 duration-200">
                  <WriterEditor :messages="taskStore.writerMessages" :writerSequence="writerSequence" />
                </TabsContent>
              </Tabs>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>

    <!-- 移动端布局 -->
    <div class="md:hidden h-full flex flex-col bg-background">
      <Tabs default-value="chat" class="h-full flex flex-col">
        <div class="border-b border-border px-3 py-2 bg-muted shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-1.5">
              <h2 class="text-sm font-semibold text-foreground">MathModelAgent</h2>
              <!-- 移动端调试模式指示 -->
              <Button
                v-if="debugMode"
                size="sm"
                variant="ghost"
                class="h-5 px-1.5 bg-destructive/10 text-destructive hover:bg-destructive/20"
              >
                <Bug class="w-3 h-3" />
              </Button>
            </div>
            <div class="flex items-center gap-1.5">
              <!-- 工作流程按钮 -->
              <Button
                @click="workflowDialogOpen = true"
                size="sm"
                variant="ghost"
                class="h-6 w-6 p-0"
              >
                <Network class="w-3.5 h-3.5" />
              </Button>

              <!-- 调试模式开关 -->
              <Button
                @click="debugMode = !debugMode"
                size="sm"
                variant="ghost"
                class="h-6 w-6 p-0"
                :class="debugMode ? 'text-destructive' : 'text-muted-foreground'"
              >
                <Bug class="w-3.5 h-3.5" />
              </Button>

              <div class="flex items-center gap-1 px-2 py-0.5 bg-background rounded text-xs border border-border">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                <span class="font-mono font-semibold text-primary">{{ runningDuration }}</span>
              </div>
            </div>
          </div>
          <TabsList class="grid w-full grid-cols-4 h-8 bg-background text-xs">
            <TabsTrigger value="chat" class="text-xs">
              <MessageSquare class="w-3 h-3 mr-1" />
              对话
            </TabsTrigger>
            <TabsTrigger value="modeler" class="text-xs">
              <Brain class="w-3 h-3 mr-1" />
              建模
            </TabsTrigger>
            <TabsTrigger value="coder" class="text-xs">
              <Code2 class="w-3 h-3 mr-1" />
              代码
            </TabsTrigger>
            <TabsTrigger value="writer" class="text-xs">
              <PenTool class="w-3 h-3 mr-1" />
              论文
            </TabsTrigger>
          </TabsList>
        </div>
        <div class="flex-1 overflow-hidden">
          <TabsContent value="chat" class="h-full m-0">
            <ChatArea :messages="taskStore.chatMessages" />
          </TabsContent>
          <TabsContent value="modeler" class="h-full m-0">
            <ModelerEditor />
          </TabsContent>
          <TabsContent value="coder" class="h-full m-0">
            <CoderEditor />
          </TabsContent>
          <TabsContent value="writer" class="h-full m-0">
            <WriterEditor :messages="taskStore.writerMessages" :writerSequence="writerSequence" />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  </div>
</template>

