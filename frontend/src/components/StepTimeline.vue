<script setup lang="ts">
import type { StepMessage } from "@/utils/response";
import {
	CheckCircle2,
	Code2,
	Info,
	Loader2,
	Wrench,
	XCircle,
} from "lucide-vue-next";
import { computed } from "vue";

interface Props {
	steps: StepMessage[];
}

const props = defineProps<Props>();

// 按时间戳排序步骤
const sortedSteps = computed(() => {
	return [...props.steps].sort((a, b) => {
		const timeA = a.timestamp || 0;
		const timeB = b.timestamp || 0;
		return timeA - timeB;
	});
});

// 获取步骤图标
const getStepIcon = (step: StepMessage) => {
	if (step.status === "completed") return CheckCircle2;
	if (step.status === "failed") return XCircle;
	if (step.status === "processing") return Loader2;
	return Info;
};

// 获取步骤颜色类
const getStepColor = (step: StepMessage) => {
	const colors = {
		completed: "text-green-600 bg-green-500/10 border-green-500/20",
		failed: "text-destructive bg-destructive/10 border-destructive/20",
		processing: "text-primary bg-primary/10 border-primary/20",
	};
	return colors[step.status] || "text-muted-foreground bg-muted border-border";
};

// 获取Agent类型颜色
const getAgentColor = (agentType?: string) => {
	const colors: Record<string, string> = {
		CoderAgent: "text-green-600 bg-green-500/10",
		WriterAgent: "text-purple-600 bg-purple-500/10",
		ModelerAgent: "text-blue-600 bg-blue-500/10",
		CoordinatorAgent: "text-orange-600 bg-orange-500/10",
	};
	return colors[agentType || ""] || "text-muted-foreground bg-muted";
};

// 格式化时间
const formatTime = (timestamp?: number) => {
	if (!timestamp) return "";
	const date = new Date(timestamp * 1000); // 后端时间戳是秒
	return date.toLocaleTimeString("zh-CN", {
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
	});
};
</script>

<template>
  <div class="step-timeline space-y-2 px-2 py-2">
    <div v-for="(step, index) in sortedSteps" :key="step.id" class="step-item relative">
      <!-- 连接线 -->
      <div
        v-if="index < sortedSteps.length - 1"
        class="absolute left-[11px] top-6 w-0.5 h-[calc(100%+8px)] bg-border"
      ></div>

      <div class="flex items-start gap-2">
        <!-- 步骤图标 -->
        <div :class="['flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center border-2 relative z-10', getStepColor(step)]">
          <component
            :is="getStepIcon(step)"
            :class="['w-3 h-3', step.status === 'processing' ? 'animate-spin' : '']"
          />
        </div>

        <!-- 步骤内容 -->
        <div class="flex-1 min-w-0 pb-2">
          <div class="flex items-center gap-2 flex-wrap">
            <!-- 步骤名称 -->
            <span class="text-xs font-medium text-foreground">{{ step.step_name }}</span>

            <!-- Agent类型标签 -->
            <span
              v-if="step.agent_type"
              :class="['text-[8px] px-1.5 py-0.5 rounded font-semibold', getAgentColor(step.agent_type)]"
            >
              {{ step.agent_type }}
            </span>

            <!-- 步骤类型标签 -->
            <span
              v-if="step.step_type === 'tool'"
              class="text-[8px] px-1.5 py-0.5 rounded bg-orange-500/10 text-orange-600 font-semibold flex items-center gap-0.5"
            >
              <Wrench class="w-2.5 h-2.5" />
              工具调用
            </span>
            <span
              v-else-if="step.step_type === 'agent'"
              class="text-[8px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-600 font-semibold flex items-center gap-0.5"
            >
              <Code2 class="w-2.5 h-2.5" />
              Agent
            </span>

            <!-- 时间戳 -->
            <span class="text-[9px] text-muted-foreground font-mono ml-auto">
              {{ formatTime(step.timestamp) }}
            </span>
          </div>

          <!-- 步骤详情（如果有） -->
          <div v-if="step.details" class="mt-1 text-[9px] text-muted-foreground bg-muted rounded px-2 py-1 font-mono">
            {{ JSON.stringify(step.details) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="sortedSteps.length === 0" class="text-center py-4 text-muted-foreground text-xs">
      暂无执行步骤
    </div>
  </div>
</template>
