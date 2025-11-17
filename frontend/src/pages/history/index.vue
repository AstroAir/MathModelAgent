<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useHistoryStore } from "@/stores/history";
import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Pagination } from "@/components/ui/pagination";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Search,
  FileText,
  AlertCircle,
} from "lucide-vue-next";
import TaskHistoryCard from "@/components/TaskHistoryCard.vue";

const router = useRouter();
const historyStore = useHistoryStore();

// Reactive state
const searchQuery = ref("");
const activeTab = ref("all");
const deleteDialogOpen = ref(false);
const taskToDelete = ref<string | null>(null);

// Computed properties
const displayTasks = computed(() => {
  // Use paginated tasks from the store
  return historyStore.paginatedTasks;
});

const totalFilteredTasks = computed(() => {
  switch (activeTab.value) {
    case "pinned":
      return historyStore.pinnedTasks.length;
    case "custom":
      return historyStore.customTasks.length;
    case "example":
      return historyStore.exampleTasks.length;
    default:
      return historyStore.filteredTasks.length;
  }
});

// Methods
const handleSearch = (value: string | number) => {
  const strValue = String(value);
  searchQuery.value = strValue;
  historyStore.setSearchFilter(strValue);
};

const handleTabChange = async (tab: string | number) => {
  const strTab = String(tab);
  activeTab.value = strTab;

  const filters: any = {};
  if (strTab === "pinned") {
    filters.pinned_only = true;
  } else if (strTab === "custom") {
    filters.task_type = "custom";
  } else if (strTab === "example") {
    filters.task_type = "example";
  }

  await historyStore.loadTasks(filters);
};

const handleTogglePin = async (taskId: string) => {
  try {
    await historyStore.togglePin(taskId);
  } catch (error) {
    console.error("Failed to toggle pin:", error);
  }
};

const handleDeleteTask = async (taskId: string) => {
  taskToDelete.value = taskId;
  deleteDialogOpen.value = true;
};

const confirmDelete = async () => {
  if (taskToDelete.value) {
    try {
      await historyStore.deleteTask(taskToDelete.value);
      deleteDialogOpen.value = false;
      taskToDelete.value = null;
    } catch (error) {
      console.error("Failed to delete task:", error);
    }
  }
};

const navigateToTask = (taskId: string) => {
  router.push(`/task/${taskId}`);
};

const handlePageChange = (page: number) => {
  historyStore.setCurrentPage(page);
};

const handlePageSizeChange = (size: number) => {
  historyStore.setItemsPerPage(size);
};



// Lifecycle
onMounted(async () => {
  await Promise.all([
    historyStore.loadTasks(),
    historyStore.loadTaskCount(),
  ]);
});
</script>

<template>
  <div class="min-h-screen bg-background">
    <div class="container mx-auto px-4 py-8 max-w-7xl">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold tracking-tight mb-2">历史记录</h1>
        <p class="text-muted-foreground">
          查看和管理您的任务历史记录
        </p>
      </div>

      <!-- Search and Filters -->
      <div class="mb-6 flex flex-col sm:flex-row gap-4">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            :model-value="searchQuery"
            @update:model-value="handleSearch"
            placeholder="搜索任务标题或描述..."
            class="pl-10"
          />
        </div>
      </div>

      <!-- Error Alert -->
      <Alert v-if="historyStore.error" class="mb-6" variant="destructive">
        <AlertCircle class="h-4 w-4" />
        <AlertDescription>
          {{ historyStore.error }}
          <Button
            variant="outline"
            size="sm"
            class="ml-2"
            @click="historyStore.clearError"
          >
            关闭
          </Button>
        </AlertDescription>
      </Alert>

      <!-- Tabs -->
      <Tabs :model-value="activeTab" @update:model-value="handleTabChange" class="w-full">
        <TabsList class="grid w-full grid-cols-4">
          <TabsTrigger value="all">
            全部 ({{ historyStore.taskCount.total }})
          </TabsTrigger>
          <TabsTrigger value="pinned">
            收藏 ({{ historyStore.pinnedTasks.length }})
          </TabsTrigger>
          <TabsTrigger value="custom">
            自定义 ({{ historyStore.taskCount.custom }})
          </TabsTrigger>
          <TabsTrigger value="example">
            示例 ({{ historyStore.taskCount.example }})
          </TabsTrigger>
        </TabsList>

        <!-- Loading State -->
        <div v-if="historyStore.loading" class="mt-6 space-y-4">
          <Card v-for="i in 3" :key="i">
            <CardHeader>
              <Skeleton class="h-4 w-3/4" />
              <Skeleton class="h-3 w-1/2" />
            </CardHeader>
            <CardContent>
              <Skeleton class="h-3 w-full mb-2" />
              <Skeleton class="h-3 w-2/3" />
            </CardContent>
          </Card>
        </div>

        <!-- Task List -->
        <TabsContent v-for="tab in ['all', 'pinned', 'custom', 'example']" :key="tab" :value="tab" class="mt-6">
          <div v-if="displayTasks.length === 0 && !historyStore.loading" class="text-center py-12">
            <FileText class="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <h3 class="text-lg font-semibold mb-2">暂无历史记录</h3>
            <p class="text-muted-foreground mb-4">开始创建任务来查看历史记录</p>
            <Button @click="router.push('/chat')">开始对话</Button>
          </div>

          <div v-else class="grid gap-4">
            <TaskHistoryCard
              v-for="task in displayTasks"
              :key="task.task_id"
              :task="task"
              @navigate="navigateToTask"
              @toggle-pin="handleTogglePin"
              @delete="handleDeleteTask"
            />
          </div>

          <!-- Pagination -->
          <div v-if="displayTasks.length > 0" class="mt-6">
            <Pagination
              :current-page="historyStore.pagination.currentPage"
              :total-pages="historyStore.pagination.totalPages"
              :total-items="totalFilteredTasks"
              :items-per-page="historyStore.pagination.itemsPerPage"
              @update:current-page="handlePageChange"
              @update:items-per-page="handlePageSizeChange"
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:open="deleteDialogOpen">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>确认删除</DialogTitle>
          <DialogDescription>
            您确定要删除这个历史记录吗？此操作无法撤销。
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" @click="deleteDialogOpen = false">
            取消
          </Button>
          <Button variant="destructive" @click="confirmDelete">
            删除
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  </div>
</template>
