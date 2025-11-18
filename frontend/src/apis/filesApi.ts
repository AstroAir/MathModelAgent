import request from "@/utils/request";
import type { FileContentResponse } from "@/utils/response";

// Types
export interface FileInfo {
	name: string;
	path?: string;
	size?: number;
	type?: string;
	modified_time?: string | number;
	is_directory?: boolean;
	filename?: string;
	file_type?: string;
}

// API Functions

// 获取任务文件列表
export function getFiles(taskId: string) {
	return request.get<FileInfo[]>(`/files/${taskId}/files`);
}

// 获取文件内容
export function getFileContent(taskId: string, filename: string) {
	return request.get<FileContentResponse>(`/files/${taskId}/files/content`, {
		params: {
			filename,
		},
	});
}

// 获取文件下载链接
export function getFileDownloadUrl(taskId: string, filename: string) {
	return request.get<{ download_url: string }>(`/files/${taskId}/download-url`, {
		params: {
			filename,
		},
	});
}

// 获取所有文件的打包下载链接
export function getAllFilesDownloadUrl(taskId: string) {
	// This now directly triggers a download, the URL is the endpoint itself.
	const baseUrl = import.meta.env.VITE_API_URL;
	return `${baseUrl}/files/${taskId}/download-all`;
}

// 上传文件
export function uploadFile(taskId: string, file: File) {
	const formData = new FormData();
	formData.append("file", file);
	return request.post<{ message: string; filename: string; size: number }>(
		`/files/${taskId}/files`,
		formData,
		{
			headers: {
				"Content-Type": "multipart/form-data",
			},
		}
	);
}

// 删除文件
export function deleteFile(taskId: string, filename: string) {
	return request.delete<{ message: string }>(`/files/${taskId}/files`, {
		params: {
			filename,
		},
	});
}
