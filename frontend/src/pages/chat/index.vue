<script setup lang="ts">


import AppSidebar from '@/components/AppSidebar.vue'
import UserStepper from '@/components/UserStepper.vue'
import ModelingExamples from '@/components/ModelingExamples.vue'
import { onMounted, ref } from 'vue'
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from '@/components/ui/sidebar'
import { getHelloWorld } from '@/apis/commonApi'
import MoreDetail from '@/pages/chat/components/MoreDetail.vue'
import Button from '@/components/ui/button/Button.vue'
import ServiceStatus from '@/components/ServiceStatus.vue'
import { AppWindow, CircleEllipsis, Sparkles } from 'lucide-vue-next'
onMounted(() => {
  getHelloWorld().then((res) => {
    console.log(res.data)
  })
})


const isMoreDetailOpen = ref(false)
const showExamples = ref(false)

const toggleExamples = () => {
  showExamples.value = !showExamples.value
}

</script>

<template>

  <SidebarProvider>
    <MoreDetail v-model="isMoreDetailOpen" />
    <AppSidebar />
    <SidebarInset>
      <!-- 移动端优化的Header -->
      <header class="flex h-14 sm:h-16 shrink-0 items-center gap-2 px-3 sm:px-4 border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <SidebarTrigger class="-ml-1" />
        <div class="flex justify-between w-full gap-2 items-center">
          <ServiceStatus />
          <div class="flex gap-1.5 sm:gap-2">
            <Button
              variant="outline"
              size="sm"
              @click="toggleExamples"
              class="h-8 sm:h-9 transition-colors"
              :class="showExamples ? 'bg-accent text-accent-foreground' : ''"
            >
              <Sparkles class="w-4 h-4" />
              <span class="hidden sm:inline ml-1.5">探索示例</span>
            </Button>
            <Button variant="outline" size="sm" @click="isMoreDetailOpen = true" class="h-8 sm:h-9">
              <CircleEllipsis class="w-4 h-4" />
              <span class="hidden sm:inline ml-1.5">更多</span>
            </Button>
            <a href="https://www.mathmodel.top/" target="_blank">
              <Button variant="outline" size="sm" class="h-8 sm:h-9">
                <AppWindow class="w-4 h-4" />
                <span class="hidden sm:inline ml-1.5">官网</span>
              </Button>
            </a>
          </div>
        </div>
      </header>

      <!-- 优化的主内容区 -->
      <div class="relative h-[calc(100vh-3.5rem)] sm:h-[calc(100vh-4rem)] overflow-hidden">
        <!-- 主内容 -->
        <div 
          class="h-full py-4 sm:py-5 md:py-6 px-3 sm:px-4 md:px-6 overflow-y-auto transition-all duration-300"
          :class="showExamples ? 'blur-sm scale-95 pointer-events-none' : ''"
        >
          <div class="space-y-4 sm:space-y-6 max-w-6xl mx-auto">
            <!-- 标题区域 - 移动端优化 -->
            <div class="text-center space-y-2 mb-6 sm:mb-10">
              <h1 class="text-xl sm:text-2xl md:text-3xl font-semibold text-gradient">
                MathModelAgent
              </h1>
              <p class="text-xs sm:text-sm md:text-base text-muted-foreground px-4">
                让 Agent 数学建模，代码编写，论文写作
              </p>
            </div>

            <!-- UserStepper组件 -->
            <UserStepper />
            
            <!-- 提示信息 -->
            <div class="text-center text-[10px] sm:text-xs text-muted-foreground mt-6 sm:mt-8 px-4">
              项目处于内测阶段，欢迎进群反馈
            </div>
          </div>
        </div>

        <!-- 示例展示覆盖层 -->
        <Transition name="examples">
          <div
            v-if="showExamples"
            class="absolute inset-0 bg-background/95 backdrop-blur-sm overflow-y-auto z-20"
            @click.self="showExamples = false"
          >
            <div class="min-h-full py-6 sm:py-8 px-3 sm:px-4 md:px-6">
              <div class="max-w-7xl mx-auto">
                <!-- 标题栏 -->
                <div class="flex items-center justify-between mb-8">
                  <div>
                    <h2 class="text-2xl sm:text-3xl font-bold text-gradient mb-2">
                      探索示例案例
                    </h2>
                    <p class="text-sm text-muted-foreground">
                      浏览历年数模竞赛优秀案例，快速开始你的建模任务
                    </p>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    @click="showExamples = false"
                    class="shrink-0"
                  >
                    <span class="text-lg">✕</span>
                  </Button>
                </div>

                <!-- 示例卡片 -->
                <ModelingExamples @example-selected="showExamples = false" />
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </SidebarInset>
  </SidebarProvider>
</template>

<style scoped>
/* 示例展示动画 */
.examples-enter-active,
.examples-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.examples-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}

.examples-enter-to {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.examples-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.examples-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}
</style>
