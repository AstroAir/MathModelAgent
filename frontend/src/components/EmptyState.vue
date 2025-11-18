<script setup lang="ts">
import { Button } from "@/components/ui/button";
import {
	AlertCircle,
	FolderOpen,
	Inbox,
	type LucideIcon,
	Search,
} from "lucide-vue-next";
import { computed } from "vue";

interface Props {
	icon?: LucideIcon;
	title?: string;
	description?: string;
	actionText?: string;
	actionIcon?: LucideIcon;
	variant?: "default" | "search" | "error" | "empty";
}

const props = withDefaults(defineProps<Props>(), {
	variant: "default",
});

const emit = defineEmits<{
	action: [];
}>();

// 根据变体选择默认图标和文本
const defaultConfig = computed(() => {
	switch (props.variant) {
		case "search":
			return {
				icon: Search,
				title: "未找到结果",
				description: "尝试调整搜索条件或使用其他关键词",
			};
		case "error":
			return {
				icon: AlertCircle,
				title: "出错了",
				description: "加载数据时遇到问题，请稍后重试",
			};
		case "empty":
			return {
				icon: Inbox,
				title: "暂无数据",
				description: "这里还没有任何内容",
			};
		default:
			return {
				icon: FolderOpen,
				title: "暂无内容",
				description: "开始创建您的第一个项目",
			};
	}
});

const displayIcon = computed(() => props.icon || defaultConfig.value.icon);
const displayTitle = computed(() => props.title || defaultConfig.value.title);
const displayDescription = computed(
	() => props.description || defaultConfig.value.description,
);
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div class="relative mb-6">
      <div class="absolute inset-0 bg-primary/5 rounded-full blur-2xl" />
      <div class="relative bg-muted rounded-full p-6">
        <component
          :is="displayIcon"
          class="h-12 w-12 text-muted-foreground"
        />
      </div>
    </div>

    <h3 class="text-lg font-semibold mb-2">{{ displayTitle }}</h3>
    <p class="text-sm text-muted-foreground max-w-md mb-6">
      {{ displayDescription }}
    </p>

    <Button
      v-if="actionText"
      @click="emit('action')"
      class="gap-2"
    >
      <component
        v-if="actionIcon"
        :is="actionIcon"
        class="h-4 w-4"
      />
      {{ actionText }}
    </Button>

    <slot name="action" />
  </div>
</template>
