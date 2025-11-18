<script setup lang="ts">
import { computed } from "vue";
import { File as FileIcon, Folder as FolderIcon } from "lucide-vue-next";

const props = defineProps<{
	item: string;
}>();

const emit = defineEmits<{
	(e: "click", item: string): void;
	(e: "download", item: string): void;
}>();

const label = computed(() => {
	if (typeof props.item !== "string") {
		return "";
	}
	const parts = props.item.split(/[/\\]/);
	return parts[parts.length - 1] || props.item;
});

const isDirectory = computed(() => {
	if (typeof props.item !== "string") {
		return false;
	}
	const name = label.value;
	return !name.includes(".");
});

const handleClick = () => {
	emit("click", props.item);
};

const handleDownloadClick = (event: MouseEvent) => {
	event.stopPropagation();
	emit("download", props.item);
};
</script>

<template>
  <div
    class="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-muted cursor-pointer text-sm"
    @click="handleClick"
  >
    <component
      :is="isDirectory ? FolderIcon : FileIcon"
      class="w-4 h-4 text-muted-foreground flex-shrink-0"
    />
    <span class="flex-1 truncate">{{ label }}</span>
    <button
      type="button"
      class="text-xs text-muted-foreground hover:text-foreground"
      @click="handleDownloadClick"
    >
      下载
    </button>
  </div>
</template>
