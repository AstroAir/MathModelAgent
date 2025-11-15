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
import AgentWorkflowStatus from '@/components/AgentWorkflowStatus.vue'
import { onMounted, onBeforeUnmount, ref, computed, provide } from 'vue'
import { useTaskStore } from '@/stores/task'
import { getWriterSeque } from '@/apis/commonApi';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/toast/use-toast'
import FilesSheet from '@/pages/task/components/FileSheet.vue'
import { Brain, Code2, PenTool, Bug } from 'lucide-vue-next'
const { toast } = useToast()

// 调试模式状态
const debugMode = ref(false)
provide('debugMode', debugMode)

const props = defineProps<{ task_id: string }>()
const taskStore = useTaskStore()

const writerSequence = ref<string[]>([]);

// Agent状态管理
const agentStatuses = computed(() => [
  {
    name: 'Coordinator',
    status: (taskStore.coordinatorMessages?.length || 0) > 0 ? 'completed' : 'pending',
    icon: '🎯',
    description: '任务协调与分析'
  },
  {
    name: 'ModelerAgent',
    status: (taskStore.modelerMessages?.length || 0) > 0 ? 'completed' : (taskStore.coordinatorMessages?.length || 0) > 0 ? 'running' : 'pending',
    icon: '🧮',
    description: '建模方案设计'
  },
  {
    name: 'CoderAgent',
    status: (taskStore.notebookCells?.length || 0) > 0 ? 'completed' : (taskStore.modelerMessages?.length || 0) > 0 ? 'running' : 'pending',
    icon: '👨‍💻',
    description: '代码实现与执行'
  },
  {
    name: 'WriterAgent',
    status: (taskStore.writerMessages?.length || 0) > 0 ? 'completed' : (taskStore.notebookCells?.length || 0) > 0 ? 'running' : 'pending',
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
})

onBeforeUnmount(() => {
  taskStore.closeWebSocket()
  // 清理计时器
  if (timer) {
    clearInterval(timer)
    timer = null
  }
})

</script>

<template>
  <div class="fixed inset-0 bg-gradient-to-br from-slate-50 to-gray-100">
    <!-- 桌面端布局 -->
    <div class="hidden md:block h-full">
      <ResizablePanelGroup direction="horizontal" class="h-full">
        <!-- 左侧：工作流程状态 + 聊天区域 -->
        <ResizablePanel :default-size="20" :min-size="15" class="h-full">
          <div class="h-full flex flex-col bg-white border-r">
            <div class="border-b px-4 py-3 bg-gradient-to-r from-blue-50 to-purple-50">
              <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Brain class="w-5 h-5 text-blue-600" />
                工作流程
              </h2>
            </div>
            <div class="flex-1 overflow-y-auto p-4">
              <AgentWorkflowStatus :agents="agentStatuses" />
            </div>
          </div>
        </ResizablePanel>
      
      <ResizableHandle class="w-1 hover:bg-blue-400 transition-colors" />
      
      <!-- 中间：聊天区域 -->
      <ResizablePanel :default-size="35" :min-size="25" class="h-full">
        <div class="h-full bg-white border-r flex flex-col">
          <div class="flex-1 overflow-hidden">
            <ChatArea :messages="taskStore.chatMessages" />
          </div>
          <!-- 调试模式指示器 -->
          <div v-if="debugMode" class="border-t bg-yellow-50 px-4 py-2 flex items-center gap-2 text-xs text-yellow-700">
            <Bug class="w-3.5 h-3.5" />
            <span class="font-semibold">调试模式已启用</span>
            <span class="text-yellow-600">- 显示详细信息和时间戳</span>
          </div>
        </div>
      </ResizablePanel>
      
      <ResizableHandle class="w-1 hover:bg-blue-400 transition-colors" />
      
      <!-- 右侧：Agent编辑器 -->
      <ResizablePanel :default-size="45" :min-size="30" class="h-full min-w-0">
        <div class="flex h-full flex-col min-w-0 bg-white">
          <Tabs default-value="modeler" class="w-full h-full flex flex-col">
            <!-- 顶部工具栏 -->
            <div class="border-b bg-gradient-to-r from-slate-50 to-gray-50">
              <div class="px-4 py-3 flex justify-between items-center">
                <div class="flex items-center gap-4">
                  <!-- 运行时长显示 -->
                  <div class="flex items-center gap-2 px-3 py-1.5 bg-white rounded-lg shadow-sm border">
                    <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span class="text-sm text-gray-600">运行时长:</span>
                    <span class="font-mono text-sm font-semibold text-blue-600">{{ runningDuration }}</span>
                  </div>
                  
                  <!-- Agent切换标签 -->
                  <TabsList class="bg-white shadow-sm">
                    <TabsTrigger value="modeler" class="text-sm data-[state=active]:bg-blue-500 data-[state=active]:text-white">
                      <Brain class="w-4 h-4 mr-1" />
                      ModelerAgent
                    </TabsTrigger>
                    <TabsTrigger value="coder" class="text-sm data-[state=active]:bg-green-500 data-[state=active]:text-white">
                      <Code2 class="w-4 h-4 mr-1" />
                      CoderAgent
                    </TabsTrigger>
                    <TabsTrigger value="writer" class="text-sm data-[state=active]:bg-purple-500 data-[state=active]:text-white">
                      <PenTool class="w-4 h-4 mr-1" />
                      WriterAgent
                    </TabsTrigger>
                  </TabsList>
                </div>

                <!-- 操作按钮 -->
                <div class="flex justify-end gap-2 items-center">
                  <!-- 调试模式开关 -->
                  <Button 
                    @click="debugMode = !debugMode" 
                    size="sm" 
                    :variant="debugMode ? 'default' : 'outline'"
                    class="shadow-sm transition-all"
                    :class="debugMode ? 'bg-yellow-500 hover:bg-yellow-600 text-white' : ''"
                  >
                    <Bug class="w-4 h-4" :class="debugMode ? 'mr-1' : ''" />
                    <span v-if="debugMode" class="hidden md:inline">调试模式</span>
                  </Button>
                  <Button @click="taskStore.downloadMessages" size="sm" variant="outline" class="shadow-sm">
                    <span class="hidden md:inline">下载消息</span>
                    <span class="md:hidden">下载</span>
                  </Button>
                  <FilesSheet />
                </div>
              </div>
            </div>

            <TabsContent value="modeler" class="flex-1 p-1 min-w-0 h-full overflow-hidden">
              <ModelerEditor />
            </TabsContent>

            <TabsContent value="coder" class="flex-1 p-1 min-w-0 h-full overflow-hidden">
              <CoderEditor />
            </TabsContent>

            <TabsContent value="writer" class="flex-1 p-1 min-w-0 h-full overflow-hidden">
              <WriterEditor :messages="taskStore.writerMessages" :writerSequence="writerSequence" />
            </TabsContent>
          </Tabs>
        </div>
      </ResizablePanel>
    </ResizablePanelGroup>

  </div>

    <!-- 移动端布局 -->
    <div class="md:hidden h-full flex flex-col bg-white">
      <Tabs default-value="chat" class="h-full flex flex-col">
        <div class="border-b px-3 py-2 bg-gradient-to-r from-blue-50 to-purple-50 shadow-sm">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-1.5">
              <Brain class="w-4 h-4 text-blue-600" />
              <h2 class="text-sm font-semibold">任务执行</h2>
              <!-- 移动端调试模式指示 -->
              <Button 
                v-if="debugMode"
                size="sm"
                variant="ghost"
                class="h-5 px-1.5 bg-yellow-100 text-yellow-700 hover:bg-yellow-200"
              >
                <Bug class="w-3 h-3" />
              </Button>
            </div>
            <div class="flex items-center gap-1.5">
              <!-- 调试模式开关 -->
              <Button 
                @click="debugMode = !debugMode" 
                size="sm" 
                variant="ghost"
                class="h-6 w-6 p-0"
                :class="debugMode ? 'text-yellow-600' : 'text-gray-400'"
              >
                <Bug class="w-3.5 h-3.5" />
              </Button>
              <div class="flex items-center gap-1 px-2 py-0.5 bg-white rounded text-xs border">
                <div class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                <span class="font-mono font-semibold text-blue-600">{{ runningDuration }}</span>
              </div>
            </div>
          </div>
          <TabsList class="grid w-full grid-cols-3 h-8 bg-white">
            <TabsTrigger value="chat" class="text-xs">对话</TabsTrigger>
            <TabsTrigger value="coder" class="text-xs">代码</TabsTrigger>
            <TabsTrigger value="writer" class="text-xs">论文</TabsTrigger>
          </TabsList>
        </div>
        <div class="flex-1 overflow-hidden">
          <TabsContent value="chat" class="h-full m-0">
            <ChatArea :messages="taskStore.chatMessages" />
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

<style scoped></style>