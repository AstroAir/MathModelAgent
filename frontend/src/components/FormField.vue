<script setup lang="ts">
import { Label } from "@/components/ui/label";
import { AlertCircle } from "lucide-vue-next";
import { computed } from "vue";

interface Props {
	label?: string;
	error?: string;
	required?: boolean;
	description?: string;
	htmlFor?: string;
}

const props = defineProps<Props>();

const hasError = computed(() => !!props.error);
</script>

<template>
  <div class="space-y-2">
    <div v-if="label" class="flex items-center justify-between">
      <Label
        :for="htmlFor"
        :class="[
          'text-sm font-medium',
          hasError ? 'text-destructive' : 'text-foreground'
        ]"
      >
        {{ label }}
        <span v-if="required" class="text-destructive ml-1">*</span>
      </Label>
      <slot name="label-extra" />
    </div>

    <div class="relative">
      <slot />
    </div>

    <div v-if="description && !hasError" class="text-sm text-muted-foreground">
      {{ description }}
    </div>

    <div
      v-if="hasError"
      class="flex items-start gap-2 text-sm text-destructive"
    >
      <AlertCircle class="h-4 w-4 mt-0.5 flex-shrink-0" />
      <span>{{ error }}</span>
    </div>
  </div>
</template>
