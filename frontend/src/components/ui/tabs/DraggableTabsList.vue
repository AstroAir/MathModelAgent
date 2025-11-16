<script setup lang="ts">
import { TabsList } from "@/components/ui/tabs";
import { type TabItem, useDraggableTabs } from "@/composables/useDraggableTabs";
import { cn } from "@/lib/utils";
import { ref } from "vue";
import type { HTMLAttributes } from "vue";

const props = withDefaults(
	defineProps<{
		tabs: TabItem[];
		modelValue?: string;
		class?: HTMLAttributes["class"];
		enableDrag?: boolean;
		orientation?: "horizontal" | "vertical";
	}>(),
	{
		enableDrag: true,
		orientation: "horizontal",
	},
);

const emit = defineEmits<{
	"update:modelValue": [value: string];
	reorder: [tabs: TabItem[]];
}>();

const containerRef = ref<HTMLElement | null>(null);
const localTabs = ref<TabItem[]>([...props.tabs]);

const { isDragging } = useDraggableTabs(containerRef, localTabs, (newOrder) => {
	emit("reorder", newOrder);
});

const handleTabClick = (value: string, disabled?: boolean) => {
	if (!disabled && !isDragging.value) {
		emit("update:modelValue", value);
	}
};
</script>

<template>
  <TabsList
    ref="containerRef"
    :class="cn(
      'flex gap-0',
      orientation === 'horizontal' ? 'flex-row' : 'flex-col',
      props.class
    )"
  >
    <div
      v-for="tab in localTabs"
      :key="tab.value"
      :data-draggable="enableDrag && !tab.disabled ? 'true' : 'false'"
      :data-drag-handle="enableDrag && !tab.disabled ? 'true' : 'false'"
      :data-tab-value="tab.value"
      @click="handleTabClick(tab.value, tab.disabled)"
      :class="cn(
        'cursor-pointer transition-all',
        enableDrag && !tab.disabled && 'hover:opacity-80',
        tab.disabled && 'opacity-50 cursor-not-allowed'
      )"
    >
      <slot name="tab" :tab="tab" :is-dragging="isDragging">
        <div class="flex items-center gap-2 px-3 py-2">
          <component v-if="tab.icon" :is="tab.icon" class="w-4 h-4" />
          <span>{{ tab.label }}</span>
        </div>
      </slot>
    </div>
  </TabsList>
</template>

<style scoped>
.sortable-ghost {
  opacity: 0.4;
  background-color: hsl(var(--primary) / 0.1);
}

.sortable-chosen {
  cursor: grabbing !important;
}

.sortable-drag {
  opacity: 0.8;
  transform: rotate(2deg);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

[data-drag-handle="true"] {
  cursor: grab;
}

[data-drag-handle="true"]:active {
  cursor: grabbing;
}
</style>
