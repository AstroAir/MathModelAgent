<script setup lang="ts">
import { Loader2 } from "lucide-vue-next";
import { computed } from "vue";

const props = withDefaults(
	defineProps<{
		size?: "sm" | "md" | "lg";
		text?: string;
		fullscreen?: boolean;
	}>(),
	{
		size: "md",
		fullscreen: false,
	},
);

const sizeClasses = computed(() => {
	switch (props.size) {
		case "sm":
			return "w-4 h-4";
		case "lg":
			return "w-12 h-12";
		default:
			return "w-8 h-8";
	}
});
</script>

<template>
  <div
    :class="[
      'flex flex-col items-center justify-center gap-3',
      fullscreen ? 'fixed inset-0 bg-background/80 backdrop-blur-sm z-50' : 'p-8'
    ]"
  >
    <Loader2
      :class="[
        'animate-spin text-primary',
        sizeClasses
      ]"
    />
    <p
      v-if="text"
      :class="[
        'text-muted-foreground font-medium',
        size === 'sm' ? 'text-xs' : size === 'lg' ? 'text-base' : 'text-sm'
      ]"
    >
      {{ text }}
    </p>
  </div>
</template>
