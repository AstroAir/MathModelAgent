/**
 * 历史记录状态管理
 */

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { TaskHistoryItem } from "@/types/history";
import {
  getTaskHistoryList,
  createTaskHistory,
  updateTaskHistory,
  toggleTaskPin,
  deleteTaskHistory,
  getTaskCount,
} from "@/apis/historyApi";

export const useHistoryStore = defineStore("history", () => {
  // State
  const tasks = ref<TaskHistoryItem[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const total = ref(0);
  const taskCount = ref({
    total: 0,
    custom: 0,
    example: 0,
  });

  // Filters and Pagination
  const currentFilter = ref<{
    task_type?: string;
    pinned_only?: boolean;
    search?: string;
  }>({});

  const pagination = ref({
    currentPage: 1,
    itemsPerPage: 20,
    totalPages: 1,
  });

  // Computed
  const filteredTasks = computed(() => {
    let filtered = [...tasks.value];

    // Apply search filter
    if (currentFilter.value.search) {
      const searchTerm = currentFilter.value.search.toLowerCase();
      filtered = filtered.filter(
        (task) =>
          task.title.toLowerCase().includes(searchTerm) ||
          task.description.toLowerCase().includes(searchTerm)
      );
    }

    return filtered;
  });

  const paginatedTasks = computed(() => {
    const filtered = filteredTasks.value;
    const start = (pagination.value.currentPage - 1) * pagination.value.itemsPerPage;
    const end = start + pagination.value.itemsPerPage;

    // Update total pages
    pagination.value.totalPages = Math.ceil(filtered.length / pagination.value.itemsPerPage);

    return filtered.slice(start, end);
  });

  const pinnedTasks = computed(() => tasks.value.filter((task) => task.is_pinned));
  const customTasks = computed(() => tasks.value.filter((task) => task.task_type === "custom"));
  const exampleTasks = computed(() => tasks.value.filter((task) => task.task_type === "example"));

  // Actions
  const loadTasks = async (filters?: {
    task_type?: string;
    pinned_only?: boolean;
  }) => {
    try {
      loading.value = true;
      error.value = null;
      currentFilter.value = { ...currentFilter.value, ...filters };

      const response = await getTaskHistoryList(filters);
      tasks.value = response.tasks;
      total.value = response.total;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "加载历史记录失败";
      console.error("Failed to load tasks:", err);
    } finally {
      loading.value = false;
    }
  };

  const loadTaskCount = async () => {
    try {
      taskCount.value = await getTaskCount();
    } catch (err) {
      console.error("Failed to load task count:", err);
    }
  };

  const addTask = async (taskData: {
    task_id: string;
    title: string;
    description: string;
    task_type?: string;
    comp_template?: string;
    file_count?: number;
  }) => {
    try {
      const newTask = await createTaskHistory({
        task_id: taskData.task_id,
        title: taskData.title,
        description: taskData.description,
        task_type: (taskData.task_type as 'custom' | 'example') || "custom",
        comp_template: taskData.comp_template,
        file_count: taskData.file_count || 0,
      });

      // Add to the beginning of the list
      tasks.value.unshift(newTask);
      total.value += 1;

      // Update count
      await loadTaskCount();

      return newTask;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "创建历史记录失败";
      throw err;
    }
  };

  const updateTask = async (
    taskId: string,
    updates: {
      title?: string;
      description?: string;
      status?: "processing" | "completed" | "failed";
    }
  ) => {
    try {
      const updatedTask = await updateTaskHistory(taskId, updates);
      const index = tasks.value.findIndex((task) => task.task_id === taskId);
      if (index !== -1) {
        tasks.value[index] = updatedTask;
      }
      return updatedTask;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "更新历史记录失败";
      throw err;
    }
  };

  const togglePin = async (taskId: string) => {
    try {
      const updatedTask = await toggleTaskPin(taskId);
      const index = tasks.value.findIndex((task) => task.task_id === taskId);
      if (index !== -1) {
        tasks.value[index] = updatedTask;
      }
      return updatedTask;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "切换收藏状态失败";
      throw err;
    }
  };

  const deleteTask = async (taskId: string) => {
    try {
      await deleteTaskHistory(taskId);
      tasks.value = tasks.value.filter((task) => task.task_id !== taskId);
      total.value -= 1;

      // Update count
      await loadTaskCount();

      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "删除历史记录失败";
      throw err;
    }
  };

  const setSearchFilter = (search: string) => {
    currentFilter.value.search = search;
    // Reset to first page when searching
    pagination.value.currentPage = 1;
  };

  const setCurrentPage = (page: number) => {
    pagination.value.currentPage = page;
  };

  const setItemsPerPage = (itemsPerPage: number) => {
    pagination.value.itemsPerPage = itemsPerPage;
    pagination.value.currentPage = 1; // Reset to first page
  };

  const clearError = () => {
    error.value = null;
  };

  const reset = () => {
    tasks.value = [];
    loading.value = false;
    error.value = null;
    total.value = 0;
    currentFilter.value = {};
    pagination.value = {
      currentPage: 1,
      itemsPerPage: 20,
      totalPages: 1,
    };
  };

  return {
    // State
    tasks,
    loading,
    error,
    total,
    taskCount,
    currentFilter,
    pagination,

    // Computed
    filteredTasks,
    paginatedTasks,
    pinnedTasks,
    customTasks,
    exampleTasks,

    // Actions
    loadTasks,
    loadTaskCount,
    addTask,
    updateTask,
    togglePin,
    deleteTask,
    setSearchFilter,
    setCurrentPage,
    setItemsPerPage,
    clearError,
    reset,
  };
});
