<template>
  <div class="bubble-container">
    <!-- User Message -->
    <div v-if="type === 'user'" class="user-bubble">
      <div class="flex justify-end mb-2">
        <div class="max-w-[80%] bg-primary text-primary-foreground rounded-lg px-4 py-2 shadow-sm">
          <div class="text-sm whitespace-pre-wrap">{{ content }}</div>
        </div>
      </div>
    </div>

    <!-- Agent Message -->
    <div v-else-if="type === 'agent'" class="agent-bubble">
      <div class="flex justify-start mb-2">
        <div class="max-w-[80%] bg-muted border rounded-lg px-4 py-3 shadow-sm">
          <div class="flex items-center space-x-2 mb-2" v-if="agentType">
            <Badge variant="secondary" class="text-xs">{{ agentType }}</Badge>
          </div>
          <div class="text-sm whitespace-pre-wrap text-foreground">{{ content }}</div>
        </div>
      </div>
    </div>

    <!-- Tool Message -->
    <div v-else-if="type === 'tool'" class="tool-bubble">
      <!-- Check if this is a web search tool message -->
      <SearchBubble
        v-if="isWebSearchTool"
        :content="content"
        :message="message"
      />

      <!-- Regular tool message -->
      <div v-else class="flex justify-start mb-2">
        <div class="max-w-[85%] bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg px-4 py-3 shadow-sm">
          <div class="flex items-center space-x-2 mb-2">
            <Wrench class="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span class="text-sm font-medium text-blue-900 dark:text-blue-100">Tool Call</span>
          </div>
          <div class="text-sm text-blue-800 dark:text-blue-200 whitespace-pre-wrap">{{ content }}</div>
        </div>
      </div>
    </div>

    <!-- System Message (fallback) -->
    <div v-else class="system-bubble">
      <div class="flex justify-center mb-2">
        <div class="max-w-[70%] bg-yellow-50 dark:bg-yellow-950/30 border border-yellow-200 dark:border-yellow-800 rounded-lg px-3 py-2 text-center">
          <div class="text-xs text-yellow-800 dark:text-yellow-200">{{ content }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import type { Message } from "@/utils/response";
import { Wrench } from "lucide-vue-next";
import { computed } from "vue";
import SearchBubble from "./WebSearch/SearchBubble.vue";

// Props
interface Props {
	type: "user" | "agent" | "tool" | "system";
	content: string;
	agentType?: string;
	message?: Message;
}

const props = defineProps<Props>();

// Computed properties
const isWebSearchTool = computed(() => {
	return (
		props.type === "tool" &&
		(props.content.includes("web_search") ||
			props.content.includes("Web Search") ||
			props.content.includes("Search successful") ||
			(props.content.includes("Found") && props.content.includes("results")) ||
			props.message?.tool_name === "web_search")
	);
});
</script>

<style scoped>
.bubble-container {
  @apply w-full;
}

.user-bubble .max-w-\[80\%\] {
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.agent-bubble .max-w-\[80\%\],
.tool-bubble .max-w-\[85\%\] {
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.system-bubble .max-w-\[70\%\] {
  word-wrap: break-word;
  overflow-wrap: break-word;
}
</style>
