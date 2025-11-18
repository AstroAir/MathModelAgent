import request from "@/utils/request";

export interface UploadProgressCallback {
	(progress: number): void;
}

export function submitModelingTask(
	problem: {
		ques_all: string;
		comp_template?: string;
		format_output?: string;
		language?: string;
	},
	files?: File[],
	onUploadProgress?: UploadProgressCallback,
) {
	const formData = new FormData();
	// 添加问题数据
	formData.append("ques_all", problem.ques_all);
	formData.append("comp_template", problem.comp_template || "CHINA");
	formData.append("format_output", problem.format_output || "Markdown");
	formData.append("language", problem.language || "zh");

	if (files) {
		// file 是文件对象

		// 添加文件
		if (files) {
			for (const file of files) {
				formData.append("files", file);
			}
		}

		return request.post<{
			task_id: string;
			status: string;
		}>("/modeling", formData, {
			headers: {
				"Content-Type": "multipart/form-data",
			},
			timeout: 300000, // 5分钟超时
			onUploadProgress: (progressEvent) => {
				if (onUploadProgress && progressEvent.total) {
					const percentCompleted = Math.round(
						(progressEvent.loaded * 100) / progressEvent.total
					);
					onUploadProgress(percentCompleted);
				}
			},
		});
	}
}
