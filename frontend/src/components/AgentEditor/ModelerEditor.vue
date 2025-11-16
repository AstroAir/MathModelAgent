<script setup lang="ts">
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useTaskStore } from "@/stores/task";
import { computed } from "vue";

const taskStore = useTaskStore();

// 获取最新的CoordinatorMessage
const latestCoordinatorMessage = computed(() => {
	const messages = taskStore.coordinatorMessages;
	return messages.length > 0 ? messages[messages.length - 1] : null;
});

// 解析CoordinatorMessage的JSON内容
const coordinatorData = computed(() => {
	if (!latestCoordinatorMessage.value?.content) return null;

	try {
		const content = latestCoordinatorMessage.value.content;
		// 移除可能的```json标记
		const cleanContent = content
			.replace(/```json\n?/, "")
			.replace(/```$/, "")
			.trim();
		return JSON.parse(cleanContent);
	} catch (error) {
		console.error("解析CoordinatorMessage失败:", error);
		return null;
	}
});

// 获取最新的ModelerMessage
const latestModelerMessage = computed(() => {
	const messages = taskStore.modelerMessages;
	return messages.length > 0 ? messages[messages.length - 1] : null;
});

// 解析ModelerMessage的JSON内容
const modelerData = computed(() => {
	if (!latestModelerMessage.value?.content) return null;

	try {
		const content = latestModelerMessage.value.content;
		// 移除可能的```json标记
		const cleanContent = content
			.replace(/```json\n?/, "")
			.replace(/```$/, "")
			.trim();
		return JSON.parse(cleanContent);
	} catch (error) {
		console.error("解析ModelerMessage失败:", error);
		return null;
	}
});

// 生成问题列表
const questionsList = computed(() => {
	if (!coordinatorData.value) return [];

	const questions = [];
	for (let i = 1; i <= coordinatorData.value.ques_count; i++) {
		const quesKey = `ques${i}`;
		if (coordinatorData.value[quesKey]) {
			questions.push({
				number: i,
				content: coordinatorData.value[quesKey],
			});
		}
	}
	return questions;
});
</script>

<template>
  <div class="h-full flex flex-col bg-background">
    <!-- 上半部分：CoordinatorMessage 结构化信息 -->
    <div class="h-1/2 border-b border-border">
      <div class="border-b border-border bg-primary/10 px-3 py-2">
        <h2 class="text-sm font-semibold text-foreground flex items-center gap-2">
          📋 题目信息
        </h2>
      </div>
      <div class="h-full pb-10">
        <ScrollArea class="h-full">
          <div class="p-3 space-y-3">
            <div v-if="coordinatorData">
              <!-- 题目标题 -->
              <div class="space-y-1">
                <h3 class="text-sm font-medium text-muted-foreground">题目标题</h3>
                <div class="text-base font-semibold text-foreground">
                  {{ coordinatorData.title }}
                </div>
              </div>

              <Separator />

              <!-- 题目背景 -->
              <div class="space-y-1">
                <h3 class="text-sm font-medium text-muted-foreground">题目背景</h3>
                <div class="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                  {{ coordinatorData.background }}
                </div>
              </div>

              <Separator />

              <!-- 问题数量和问题列表 -->
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <h3 class="text-sm font-medium text-muted-foreground">问题列表</h3>
                  <span class="px-1.5 py-0.5 text-xs bg-muted rounded">{{ coordinatorData.ques_count }} 个</span>
                </div>

                <div class="space-y-2">
                  <div v-for="question in questionsList" :key="question.number"
                    class="border-l-2 border-primary pl-3 py-2 bg-primary/10">
                    <div class="flex items-center gap-1.5 mb-0.5">
                      <span class="px-1.5 py-0.5 text-xs font-bold bg-primary text-primary-foreground rounded">Q{{ question.number }}</span>
                      <span class="text-xs font-medium text-primary">问题 {{ question.number }}</span>
                    </div>
                    <div class="text-sm text-foreground leading-relaxed">
                      {{ question.content }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="flex items-center justify-center h-32 text-muted-foreground">
              暂无题目信息
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>

    <!-- 下半部分：ModelerMessage 建模手册 -->
    <div class="h-1/2">
      <div class="border-b border-border bg-green-500/10 px-3 py-2">
        <h2 class="text-sm font-semibold text-foreground flex items-center gap-2">
          📚 建模手册
        </h2>
      </div>
      <div class="h-full pb-10">
        <ScrollArea class="h-full">
          <div class="p-3">
            <div v-if="modelerData" class="space-y-4">
              <!-- EDA部分 -->
              <div v-if="modelerData.eda" class="space-y-1">
                <h3 class="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <span class="px-1.5 py-0.5 text-xs bg-muted rounded">EDA</span>
                  探索性数据分析
                </h3>
                <div class="text-xs text-foreground leading-relaxed whitespace-pre-wrap bg-muted/50 p-2">
                  {{ modelerData.eda }}
                </div>
              </div>

              <!-- 问题解决方案 -->
              <div v-for="question in questionsList" :key="`solution-${question.number}`" class="space-y-1">
                <div v-if="modelerData[`ques${question.number}`]">
                  <h3 class="text-sm font-medium text-muted-foreground flex items-center gap-2 mb-1">
                    <span class="px-1.5 py-0.5 text-xs font-bold bg-green-500 text-white rounded">Q{{ question.number }}</span>
                    <span>解决方案</span>
                  </h3>
                  <div
                    class="text-xs text-foreground leading-relaxed whitespace-pre-wrap bg-green-500/10 p-2 border-l-2 border-green-500">
                    {{ modelerData[`ques${question.number}`] }}
                  </div>
                </div>
              </div>

              <!-- 敏感性分析 -->
              <div v-if="modelerData.sensitivity_analysis" class="space-y-1">
                <h3 class="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <span class="px-1.5 py-0.5 text-xs bg-muted rounded">敏感性分析</span>
                </h3>
                <div
                  class="text-xs text-foreground leading-relaxed whitespace-pre-wrap bg-orange-500/10 p-2 border-l-2 border-orange-500">
                  {{ modelerData.sensitivity_analysis }}
                </div>
              </div>
            </div>

            <div v-else class="flex items-center justify-center h-32 text-muted-foreground">
              暂无建模手册信息
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
