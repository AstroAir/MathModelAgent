<script setup lang="ts">
import { AlertCircle, CheckCircle2, Clock, Loader2 } from "lucide-vue-next";

interface AgentStatus {
	name: string;
	status: "pending" | "running" | "completed" | "error";
	icon: string;
	description: string;
}

defineProps<{
	agents: AgentStatus[];
}>();

const getStatusColor = (status: string) => {
	switch (status) {
		case "completed":
			return "bg-green-500/10 border-green-500/20 text-green-600";
		case "running":
			return "bg-primary/10 border-primary/20 text-primary animate-pulse";
		case "error":
			return "bg-destructive/10 border-destructive/20 text-destructive";
		default:
			return "bg-muted border-border text-muted-foreground";
	}
};

const getStatusIcon = (status: string) => {
	switch (status) {
		case "completed":
			return CheckCircle2;
		case "running":
			return Loader2;
		case "error":
			return AlertCircle;
		default:
			return Clock;
	}
};
</script>

<template>
  <div class="space-y-3">
    <div
      v-for="(agent, index) in agents"
      :key="index"
      :class="[
        'relative flex items-center gap-4 p-4 rounded-lg border-2 transition-all duration-300',
        getStatusColor(agent.status)
      ]"
    >
      <!-- 图标和状态指示器 -->
      <div class="relative flex-shrink-0">
        <div class="w-12 h-12 rounded-full bg-background shadow-sm flex items-center justify-center text-2xl">
          {{ agent.icon }}
        </div>
        <div class="absolute -bottom-1 -right-1">
          <component
            :is="getStatusIcon(agent.status)"
            :class="[
              'w-5 h-5',
              agent.status === 'running' && 'animate-spin'
            ]"
          />
        </div>
      </div>

      <!-- Agent信息 -->
      <div class="flex-1 min-w-0">
        <h3 class="font-semibold text-sm mb-1 text-foreground">{{ agent.name }}</h3>
        <p class="text-xs opacity-75 line-clamp-1">{{ agent.description }}</p>
      </div>

      <!-- 连接线 -->
      <div
        v-if="index < agents.length - 1"
        class="absolute left-8 top-full w-0.5 h-3 bg-border"
      />
    </div>
  </div>
</template>
