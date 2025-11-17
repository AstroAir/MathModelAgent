<script setup lang="ts">
import AppSidebar from "@/components/AppSidebar.vue";
import ServiceStatus from "@/components/ServiceStatus.vue";
import {
	SidebarInset,
	SidebarProvider,
	SidebarTrigger,
} from "@/components/ui/sidebar";
import FileSheet from "@/pages/task/components/FileSheet.vue";
import { useRoute } from "vue-router";

const route = useRoute();
const taskId = route.params.task_id as string;

defineProps<{
	task_id?: string;
}>();
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header class="flex h-14 sm:h-16 shrink-0 items-center gap-2 px-3 sm:px-4 border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <SidebarTrigger class="-ml-1" />
        <div class="flex justify-between w-full gap-2 items-center">
          <div class="flex items-center gap-2">
            <h1 class="text-lg font-semibold">任务详情</h1>
            <span class="text-sm text-muted-foreground">{{ taskId }}</span>
          </div>
          <ServiceStatus />
        </div>
      </header>

      <main class="flex-1 p-4">
        <div class="max-w-7xl mx-auto">
          <div class="bg-card rounded-lg border p-6">
            <h2 class="text-xl font-semibold mb-4">任务信息</h2>
            <div class="space-y-4">
              <div>
                <label class="text-sm font-medium text-muted-foreground">任务 ID</label>
                <p class="mt-1">{{ taskId }}</p>
              </div>

              <div class="mt-6">
                <FileSheet />
              </div>
            </div>
          </div>
        </div>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
