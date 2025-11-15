<script setup lang="ts">
import { computed } from 'vue'
import { useTaskStore } from '@/stores/task'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'

const taskStore = useTaskStore()

// 获取最新的CoordinatorMessage
const latestCoordinatorMessage = computed(() => {
  const messages = taskStore.coordinatorMessages
  return messages.length > 0 ? messages[messages.length - 1] : null
})

// 解析CoordinatorMessage的JSON内容
const coordinatorData = computed(() => {
  if (!latestCoordinatorMessage.value?.content) return null

  try {
    const content = latestCoordinatorMessage.value.content
    // 移除可能的```json标记
    const cleanContent = content.replace(/```json\n?/, '').replace(/```$/, '').trim()
    return JSON.parse(cleanContent)
  } catch (error) {
    console.error('解析CoordinatorMessage失败:', error)
    return null
  }
})

// 获取最新的ModelerMessage
const latestModelerMessage = computed(() => {
  const messages = taskStore.modelerMessages
  return messages.length > 0 ? messages[messages.length - 1] : null
})

// 解析ModelerMessage的JSON内容
const modelerData = computed(() => {
  if (!latestModelerMessage.value?.content) return null

  try {
    const content = latestModelerMessage.value.content
    // 移除可能的```json标记
    const cleanContent = content.replace(/```json\n?/, '').replace(/```$/, '').trim()
    return JSON.parse(cleanContent)
  } catch (error) {
    console.error('解析ModelerMessage失败:', error)
    return null
  }
})

// 生成问题列表
const questionsList = computed(() => {
  if (!coordinatorData.value) return []

  const questions = []
  for (let i = 1; i <= coordinatorData.value.ques_count; i++) {
    const quesKey = `ques${i}`
    if (coordinatorData.value[quesKey]) {
      questions.push({
        number: i,
        content: coordinatorData.value[quesKey]
      })
    }
  }
  return questions
})
</script>

<template>
  <div class="h-full flex flex-col p-4 bg-gradient-to-br from-gray-50 to-slate-50">
    <!-- 上半部分：CoordinatorMessage 结构化信息 -->
    <div class="h-1/2 mb-4 bg-white rounded-xl border-2 shadow-lg hover:shadow-xl transition-all duration-300">
      <div class="border-b bg-gradient-to-r from-blue-50 to-cyan-50 px-4 py-3 rounded-t-xl">
        <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
          📋 题目信息
        </h2>
      </div>
      <div class="h-full pb-14">
        <ScrollArea class="h-full">
          <div class="p-4 space-y-4">
            <div v-if="coordinatorData">
              <!-- 题目标题 -->
              <div class="space-y-2">
                <h3 class="text-base font-medium text-gray-700">题目标题</h3>
                <div class="text-lg font-semibold text-gray-900">
                  {{ coordinatorData.title }}
                </div>
              </div>

              <Separator />

              <!-- 题目背景 -->
              <div class="space-y-2">
                <h3 class="text-base font-medium text-gray-700">题目背景</h3>
                <div class="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {{ coordinatorData.background }}
                </div>
              </div>

              <Separator />

              <!-- 问题数量和问题列表 -->
              <div class="space-y-2">
                <div class="flex items-center gap-2">
                  <h3 class="text-base font-medium text-gray-700">问题列表</h3>
                  <span class="px-2 py-1 text-xs bg-gray-100 rounded">{{ coordinatorData.ques_count }} 个问题</span>
                </div>

                <div class="space-y-3">
                  <div v-for="question in questionsList" :key="question.number"
                    class="border-l-4 border-blue-500 pl-4 py-3 bg-gradient-to-r from-blue-50 to-blue-25 rounded-r-lg shadow-sm hover:shadow-md transition-all duration-200">
                    <div class="flex items-center gap-2 mb-1">
                      <span class="px-2 py-0.5 text-xs font-bold bg-blue-500 text-white rounded">Q{{ question.number }}</span>
                      <span class="text-sm font-medium text-blue-700">问题 {{ question.number }}</span>
                    </div>
                    <div class="text-sm text-gray-800 leading-relaxed">
                      {{ question.content }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="flex items-center justify-center h-32 text-gray-500">
              暂无题目信息
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>

    <!-- 下半部分：ModelerMessage 建模手册 -->
    <div class="h-1/2 bg-white rounded-xl border-2 shadow-lg hover:shadow-xl transition-all duration-300">
      <div class="border-b bg-gradient-to-r from-green-50 to-emerald-50 px-4 py-3 rounded-t-xl">
        <h2 class="text-lg font-semibold text-gray-900 flex items-center gap-2">
          📚 建模手册
        </h2>
      </div>
      <div class="h-full pb-14">
        <ScrollArea class="h-full">
          <div class="p-4">
            <div v-if="modelerData" class="space-y-4">
              <!-- EDA部分 -->
              <div v-if="modelerData.eda" class="space-y-2">
                <h3 class="text-base font-medium text-gray-700 flex items-center gap-2">
                  <span class="px-2 py-1 text-xs bg-gray-200 border rounded">EDA</span>
                  探索性数据分析
                </h3>
                <div class="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap bg-gray-50 p-3 rounded">
                  {{ modelerData.eda }}
                </div>
              </div>

              <!-- 问题解决方案 -->
              <div v-for="question in questionsList" :key="`solution-${question.number}`" class="space-y-2">
                <div v-if="modelerData[`ques${question.number}`]">
                  <h3 class="text-base font-medium text-gray-700 flex items-center gap-2 mb-2">
                    <span class="px-2 py-1 text-xs font-bold bg-green-500 text-white rounded">Q{{ question.number }}</span>
                    <span>解决方案</span>
                  </h3>
                  <div
                    class="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg border-l-4 border-green-500 shadow-sm hover:shadow-md transition-all duration-200">
                    {{ modelerData[`ques${question.number}`] }}
                  </div>
                </div>
              </div>

              <!-- 敏感性分析 -->
              <div v-if="modelerData.sensitivity_analysis" class="space-y-2">
                <h3 class="text-base font-medium text-gray-700 flex items-center gap-2">
                  <span class="px-2 py-1 text-xs bg-gray-200 border rounded">敏感性分析</span>
                </h3>
                <div
                  class="text-sm text-gray-800 leading-relaxed whitespace-pre-wrap bg-orange-50 p-3 rounded border-l-4 border-orange-500">
                  {{ modelerData.sensitivity_analysis }}
                </div>
              </div>
            </div>

            <div v-else class="flex items-center justify-center h-32 text-gray-500">
              暂无建模手册信息
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
