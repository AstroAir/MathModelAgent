/**
 * 任务历史记录API
 */
import axios from 'axios'
import type {
  TaskHistoryItem,
  TaskHistoryListResponse,
  CreateTaskHistoryRequest,
  UpdateTaskHistoryRequest
} from '@/types/history'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * 获取任务历史记录列表
 * @param taskType 任务类型 ('custom' | 'example')
 * @param pinnedOnly 是否只显示收藏的
 */
export const getTaskHistoryList = async (
  taskType?: string,
  pinnedOnly?: boolean
): Promise<TaskHistoryListResponse> => {
  const params: Record<string, any> = {}
  if (taskType) params.task_type = taskType
  if (pinnedOnly) params.pinned_only = pinnedOnly

  const response = await axios.get<TaskHistoryListResponse>(
    `${BASE_URL}/history/tasks`,
    { params }
  )
  return response.data
}

/**
 * 获取单个任务历史记录
 */
export const getTaskHistory = async (taskId: string): Promise<TaskHistoryItem> => {
  const response = await axios.get<TaskHistoryItem>(
    `${BASE_URL}/history/tasks/${taskId}`
  )
  return response.data
}

/**
 * 创建任务历史记录
 */
export const createTaskHistory = async (
  data: CreateTaskHistoryRequest
): Promise<TaskHistoryItem> => {
  const response = await axios.post<TaskHistoryItem>(
    `${BASE_URL}/history/tasks`,
    data
  )
  return response.data
}

/**
 * 更新任务历史记录
 */
export const updateTaskHistory = async (
  taskId: string,
  data: UpdateTaskHistoryRequest
): Promise<TaskHistoryItem> => {
  const response = await axios.patch<TaskHistoryItem>(
    `${BASE_URL}/history/tasks/${taskId}`,
    data
  )
  return response.data
}

/**
 * 切换任务收藏状态
 */
export const toggleTaskPin = async (taskId: string): Promise<TaskHistoryItem> => {
  const response = await axios.post<TaskHistoryItem>(
    `${BASE_URL}/history/tasks/${taskId}/toggle-pin`
  )
  return response.data
}

/**
 * 删除任务历史记录
 */
export const deleteTaskHistory = async (taskId: string): Promise<{ success: boolean; message: string }> => {
  const response = await axios.delete<{ success: boolean; message: string }>(
    `${BASE_URL}/history/tasks/${taskId}`
  )
  return response.data
}

/**
 * 获取任务数量统计
 */
export const getTaskCount = async (): Promise<{
  total: number
  custom: number
  example: number
}> => {
  const response = await axios.get<{
    total: number
    custom: number
    example: number
  }>(`${BASE_URL}/history/tasks/count`)
  return response.data
}
