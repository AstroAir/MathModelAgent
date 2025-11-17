/**
 * 历史记录 API 服务
 */

import request from "@/utils/request";
import type {
  TaskHistoryItem,
  TaskHistoryListResponse,
  CreateTaskHistoryRequest,
  UpdateTaskHistoryRequest,
} from "@/types/history";

/**
 * 获取任务历史记录列表
 */
export const getTaskHistoryList = async (params?: {
  task_type?: string;
  pinned_only?: boolean;
}): Promise<TaskHistoryListResponse> => {
  const searchParams = new URLSearchParams();
  if (params?.task_type) {
    searchParams.append("task_type", params.task_type);
  }
  if (params?.pinned_only) {
    searchParams.append("pinned_only", params.pinned_only.toString());
  }

  const url = `/history/tasks${searchParams.toString() ? `?${searchParams.toString()}` : ""}`;
  return request.get(url);
};

/**
 * 获取单个任务历史记录
 */
export const getTaskHistory = async (taskId: string): Promise<TaskHistoryItem> => {
  return request.get(`/history/tasks/${taskId}`);
};

/**
 * 创建任务历史记录
 */
export const createTaskHistory = async (
  data: CreateTaskHistoryRequest
): Promise<TaskHistoryItem> => {
  return request.post("/history/tasks", data);
};

/**
 * 更新任务历史记录
 */
export const updateTaskHistory = async (
  taskId: string,
  data: UpdateTaskHistoryRequest
): Promise<TaskHistoryItem> => {
  return request.patch(`/history/tasks/${taskId}`, data);
};

/**
 * 切换任务收藏状态
 */
export const toggleTaskPin = async (taskId: string): Promise<TaskHistoryItem> => {
  return request.post(`/history/tasks/${taskId}/toggle-pin`);
};

/**
 * 删除任务历史记录
 */
export const deleteTaskHistory = async (taskId: string): Promise<{ success: boolean; message: string }> => {
  return request.delete(`/history/tasks/${taskId}`);
};

/**
 * 获取任务数量统计
 */
export const getTaskCount = async (): Promise<{
  total: number;
  custom: number;
  example: number;
}> => {
  return request.get("/history/tasks/count");
};
