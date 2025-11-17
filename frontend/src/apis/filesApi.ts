import request from "@/utils/request";
import type { FileContentResponse } from "@/utils/response";

// Types
export interface FileInfo {
	name: string;
	path: string;
	size: number;
	type: string;
	modified_time?: string;
	is_directory?: boolean;
}

// API Functions

// 获取任务文件列表
export function getFiles(taskId: string) {
	return request.get<FileInfo[]>(`/files/${taskId}`);
}

// 获取文件内容
export function getFileContent(taskId: string, filePath: string) {
	return request.get<FileContentResponse>(`/files/${taskId}/content`, {
		params: {
			file_path: filePath,
		},
	});
}

// 获取文件下载链接
export function getFileDownloadUrl(taskId: string, filePath: string) {
	return request.get<{ download_url: string }>(`/files/${taskId}/download`, {
		params: {
			file_path: filePath,
		},
	});
}

// 获取所有文件的打包下载链接
export function getAllFilesDownloadUrl(taskId: string) {
	return request.get<{ download_url: string }>(`/files/${taskId}/download-all`);
}

// 上传文件
export function uploadFile(taskId: string, file: File) {
	const formData = new FormData();
	formData.append("file", file);
	return request.post<{ message: string; file_path: string }>(
		`/files/${taskId}/upload`,
		formData,
		{
			headers: {
				"Content-Type": "multipart/form-data",
			},
		}
	);
}

// 删除文件
export function deleteFile(taskId: string, filePath: string) {
	return request.delete<{ message: string }>(`/files/${taskId}`, {
		params: {
			file_path: filePath,
		},
	});
}
