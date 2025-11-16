<script setup lang="ts">
import Toaster from "@/components/ui/toast/Toaster.vue";
import { useTheme } from "@/composables/useTheme";

// Initialize the theme
useTheme();
</script>

<template>
  <Toaster />
  <router-view />
</template>
