<script setup lang="ts">
import AgentWorkflowStatus from "@/components/AgentWorkflowStatus.vue";
import {
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Network } from "lucide-vue-next";

interface AgentStatus {
	name: string;
	status: "pending" | "running" | "completed" | "error";
	icon: string;
	description: string;
}

defineProps<{
	open: boolean;
	agents: AgentStatus[];
}>();

defineEmits<(e: "update:open", value: boolean) => void>();
</script>

<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2 text-xl">
          <Network class="w-6 h-6 text-primary" />
          <span class="text-gradient">
            工作流程状态
          </span>
        </DialogTitle>
      </DialogHeader>

      <div class="flex-1 overflow-y-auto px-2 py-4">
        <AgentWorkflowStatus :agents="agents" />

        <!-- 工作流程说明 -->
        <div class="mt-6 p-4 bg-muted/50 rounded-lg border border-border">
          <h4 class="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <span class="w-1.5 h-1.5 bg-primary rounded-full"></span>
            工作流程说明
          </h4>
          <div class="space-y-2 text-xs text-muted-foreground">
            <div class="flex items-start gap-2">
              <span class="text-lg shrink-0">🎯</span>
              <div>
                <span class="font-semibold">Coordinator：</span>
                分析任务需求，制定整体计划
              </div>
            </div>
            <div class="flex items-start gap-2">
              <span class="text-lg shrink-0">🧮</span>
              <div>
                <span class="font-semibold">ModelerAgent：</span>
                设计数学建模方案和算法
              </div>
            </div>
            <div class="flex items-start gap-2">
              <span class="text-lg shrink-0">👨‍💻</span>
              <div>
                <span class="font-semibold">CoderAgent：</span>
                实现代码并执行计算
              </div>
            </div>
            <div class="flex items-start gap-2">
              <span class="text-lg shrink-0">✍️</span>
              <div>
                <span class="font-semibold">WriterAgent：</span>
                撰写完整的研究论文
              </div>
            </div>
          </div>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
