import request from "@/utils/request";

export function getHelloWorld() {
	return request.get<{ message: string }>("/");
}

// 获取论文顺序
export function getWriterSeque() {
	return request.get<{ writer_seque: string[] }>("/writer_seque");
}

export function openFolderAPI(task_id: string) {
	return request.get<{ message: string; work_dir: string }>(`/files/${task_id}/open-folder`);
}

export function exampleAPI(example_id: string, source: string) {
	return request.post<{
		task_id: string;
		status: string;
	}>("/example", {
		example_id,
		source,
	});
}

// 获取服务状态
export function getServiceStatus() {
	return request.get<{
		backend: { status: string; message: string };
		redis: { status: string; message: string };
	}>("/status");
}

// 获取任务状态
export function getTaskStatus(task_id: string) {
	return request.get<{
		task_id: string;
		status: string;
		message: string;
	}>(`/task-status/${task_id}`);
}

// 获取任务日志
export interface TaskLog {
	timestamp: string;
	level: string;
	message: string;
}

export function getTaskLogs(task_id: string) {
	return request.get<{
		task_id: string;
		logs: TaskLog[];
		total: number;
		message?: string;
		error?: string;
	}>(`/logs/${task_id}`);
}

// Token 使用追踪相关类型定义
export interface TokenUsage {
	prompt_tokens: number;
	completion_tokens: number;
	total_tokens: number;
	chat_count: number;
	cost: number;
}

export interface TaskTrackingResponse {
	task_id: string;
	token_usage: Record<string, TokenUsage> | null;
	chat_completion_count: Record<string, number> | null;
	total_cost: number;
	error?: string;
}

// 获取任务 Token 使用统计
export function getTaskTracking(task_id: string) {
	return request.get<TaskTrackingResponse>(`/track?task_id=${task_id}`);
}
