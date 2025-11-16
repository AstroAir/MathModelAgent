<template>
  <div class="h-screen flex flex-col bg-gray-100">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b p-4">
      <h1 class="text-2xl font-bold text-gray-800">日志面板测试</h1>
      <p class="text-gray-600 mt-1">测试日志面板的各种功能</p>
    </div>

    <!-- Main content -->
    <div class="flex-1 flex gap-4 p-4">
      <!-- Test controls -->
      <div class="w-80 bg-white rounded-lg shadow-sm border p-4">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">测试控制</h2>

        <div class="space-y-4">
          <!-- Add sample logs -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-2">添加示例日志</h3>
            <div class="grid grid-cols-2 gap-2">
              <button
                @click="addSampleLog('DEBUG')"
                class="px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                DEBUG
              </button>
              <button
                @click="addSampleLog('INFO')"
                class="px-3 py-2 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
              >
                INFO
              </button>
              <button
                @click="addSampleLog('WARN')"
                class="px-3 py-2 text-xs bg-yellow-100 text-yellow-700 rounded hover:bg-yellow-200"
              >
                WARN
              </button>
              <button
                @click="addSampleLog('ERROR')"
                class="px-3 py-2 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
              >
                ERROR
              </button>
              <button
                @click="addSampleLog('FATAL')"
                class="px-3 py-2 text-xs bg-red-200 text-red-800 rounded hover:bg-red-300 col-span-2"
              >
                FATAL
              </button>
            </div>
          </div>

          <!-- Batch operations -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-2">批量操作</h3>
            <div class="space-y-2">
              <button
                @click="addMultipleLogs"
                class="w-full px-3 py-2 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
              >
                添加100条随机日志
              </button>
              <button
                @click="simulateRealTimeLogging"
                class="w-full px-3 py-2 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
              >
                {{ isSimulating ? '停止' : '开始' }}实时日志模拟
              </button>
            </div>
          </div>

          <!-- Log statistics -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 mb-2">统计信息</h3>
            <div class="text-sm text-gray-600">
              <p>总日志数: {{ logStore.logs.length }}</p>
              <p>最大日志数: {{ logStore.maxLogs }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Log panel -->
      <div class="flex-1">
        <ErrorBoundary fallback-message="日志面板出现错误">
          <LogPanel />
        </ErrorBoundary>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onUnmounted } from 'vue'
import LogPanel from '@/components/LogPanel.vue'
import ErrorBoundary from '@/components/ErrorBoundary.vue'
import { useLogStore } from '@/stores/log'
import type { LogLevel } from '@/types/log'

const logStore = useLogStore()
const isSimulating = ref(false)
let simulationInterval: number | null = null

// Sample log messages for different levels
const sampleMessages = {
  DEBUG: [
    '用户点击了按钮',
    '开始处理请求',
    '缓存命中',
    '数据库查询执行',
    '组件渲染完成'
  ],
  INFO: [
    '用户登录成功',
    '文件上传完成',
    '任务执行成功',
    '配置更新完成',
    '服务启动成功'
  ],
  WARN: [
    '内存使用率较高',
    '网络连接不稳定',
    '缓存即将过期',
    '磁盘空间不足',
    'API调用频率过高'
  ],
  ERROR: [
    '数据库连接失败',
    '文件读取错误',
    '网络请求超时',
    '权限验证失败',
    '数据解析错误'
  ],
  FATAL: [
    '系统崩溃',
    '内存溢出',
    '核心服务停止',
    '数据损坏',
    '安全漏洞'
  ]
}

const sources = ['Frontend', 'Backend', 'Database', 'Cache', 'Auth', 'API', 'WebSocket', 'FileSystem']

const addSampleLog = (level: LogLevel) => {
  const messages = sampleMessages[level] || ['示例日志消息']
  const message = messages[Math.floor(Math.random() * messages.length)]
  const source = sources[Math.floor(Math.random() * sources.length)]

  logStore.addLog({
    level,
    source,
    message,
    details: level === 'ERROR' ? {
      stack: 'Error: Something went wrong\n    at function1 (file.js:10:5)\n    at function2 (file.js:20:10)',
      code: 500,
      timestamp: new Date().toISOString()
    } : undefined
  })
}

const addMultipleLogs = () => {
  const levels: LogLevel[] = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']

  for (let i = 0; i < 100; i++) {
    const level = levels[Math.floor(Math.random() * levels.length)]
    addSampleLog(level)
  }
}

const simulateRealTimeLogging = () => {
  if (isSimulating.value) {
    if (simulationInterval) {
      clearInterval(simulationInterval)
      simulationInterval = null
    }
    isSimulating.value = false
  } else {
    isSimulating.value = true
    simulationInterval = setInterval(() => {
      const levels: LogLevel[] = ['DEBUG', 'INFO', 'WARN', 'ERROR']
      const level = levels[Math.floor(Math.random() * levels.length)]
      addSampleLog(level)
    }, 1000) // Add a log every second
  }
}

onUnmounted(() => {
  if (simulationInterval) {
    clearInterval(simulationInterval)
  }
})
</script>
