import request from "@/utils/request";

export function getFiles(task_id: string) {
  return request.get<{
    files: {
      filename: string;
      file_type: string;
    }[]
  }>("/files", {
    params: { task_id },
  });
}


/**
 * 获取单个文件下载链接
 * @param task_id 任务ID
 * @param filename 文件名
 */
export async function getFileDownloadUrl(task_id: string, filename: string) {
  return await request.get<{ download_url: string }>(`/download_url`, {
    params: {
      task_id,
      filename,
    }
  })
}

/**
 * 获取所有文件压缩包下载链接
 * @param task_id 任务ID
 */
export async function getAllFilesDownloadUrl(task_id: string) {
  return await request.get<{ download_url: string }>(`/download_all_url`, {
    params: {
      task_id,
    }
  })
}

/**
 * 获取文件内容用于预览
 * @param task_id 任务ID
 * @param filename 文件名
 */
export async function getFileContent(task_id: string, filename: string) {
  return await request.get<{
    content: string
    filename: string
    is_image?: boolean
    mime_type?: string
    truncated?: boolean
    encoding?: string
    size?: number
  }>(`/file_content`, {
    params: {
      task_id,
      filename,
    },
    timeout: 30000 // 30秒超时，用于大文件
  })
}