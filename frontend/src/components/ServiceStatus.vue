<script setup lang="ts">
import { Badge } from "@/components/ui/badge";
import { CheckCircle, XCircle, Loader2 } from "lucide-vue-next";
import { ref, onMounted } from "vue";

const status = ref<"online" | "offline" | "checking">("checking");

const checkStatus = async () => {
	try {
		status.value = "checking";
		// 这里可以添加实际的健康检查 API 调用
		// const response = await fetch('/api/health');
		// if (response.ok) {
		status.value = "online";
		// } else {
		//   status.value = 'offline';
		// }
	} catch (error) {
		status.value = "offline";
	}
};

onMounted(() => {
	checkStatus();
});

const statusConfig = {
	online: {
		icon: CheckCircle,
		text: "服务正常",
		variant: "default" as const,
		class: "bg-green-500/10 text-green-600 border-green-500/20",
	},
	offline: {
		icon: XCircle,
		text: "服务离线",
		variant: "destructive" as const,
		class: "bg-red-500/10 text-red-600 border-red-500/20",
	},
	checking: {
		icon: Loader2,
		text: "检查中",
		variant: "secondary" as const,
		class: "bg-gray-500/10 text-gray-600 border-gray-500/20",
	},
};

const currentStatus = () => statusConfig[status.value];
</script>

<template>
  <Badge :variant="currentStatus().variant" :class="currentStatus().class" class="gap-1">
    <component
      :is="currentStatus().icon"
      class="h-3 w-3"
      :class="{ 'animate-spin': status === 'checking' }"
    />
    <span class="text-xs">{{ currentStatus().text }}</span>
  </Badge>
</template>
