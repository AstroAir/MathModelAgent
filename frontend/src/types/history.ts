/**
 * 任务历史记录相关类型定义
 */

export interface TaskHistoryItem {
  task_id: string
  title: string
  description: string
  task_type: 'custom' | 'example'
  comp_template?: string
  is_pinned: boolean
  created_at: string
  updated_at: string
  status: 'processing' | 'completed' | 'failed'
  file_count: number
}

export interface TaskHistoryListResponse {
  total: number
  tasks: TaskHistoryItem[]
}

export interface CreateTaskHistoryRequest {
  task_id: string
  title: string
  description: string
  task_type: 'custom' | 'example'
  comp_template?: string
  file_count: number
}

export interface UpdateTaskHistoryRequest {
  title?: string
  description?: string
  status?: 'processing' | 'completed' | 'failed'
}
