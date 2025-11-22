from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from app.utils.common_utils import get_current_files, get_work_dir
import os
import subprocess  # nosec
import base64
from urllib.parse import unquote
from pathlib import Path
from app.utils.log_util import logger
import re
import zipfile
import io

# --- Constants for Security and Validation ---
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    ".txt",
    ".csv",
    ".xlsx",
    ".json",
    ".md",
    ".py",
    ".r",
    ".ipynb",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".docx",
    ".pptx",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
}

# --- Utility Functions ---


def secure_filename(filename: str) -> str:
    """
    Sanitizes a filename to prevent directory traversal and other attacks.
    """
    # Remove dangerous characters
    filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
    # Prevent path traversal
    filename = filename.replace("..", "")
    # Normalize path separators
    filename = os.path.normpath(filename)
    # Take only the basename
    return os.path.basename(filename)


async def verify_task_access(task_id: str):
    """
    Dependency to verify user has access to the task.
    Placeholder for actual user authentication/authorization logic.
    """
    # In a real application, you would get the current user and check
    # if they own this task_id.
    # For now, we'll just log the check.
    logger.debug(f"Verifying access for task_id: {task_id}")
    # if not user_has_access(user, task_id):
    #     raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this task.")
    return task_id


router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{task_id}/download-url")
async def get_download_url(
    request: Request, filename: str, task_id: str = Depends(verify_task_access)
):
    base_url = str(request.base_url).rstrip("/")
    download_url = f"{base_url}/static/{task_id}/{secure_filename(filename)}"
    return {"download_url": download_url}


@router.get("/{task_id}/download-all")
async def download_all_files_as_zip(task_id: str = Depends(verify_task_access)):
    work_dir = get_work_dir(task_id)
    if not os.path.isdir(work_dir):
        raise HTTPException(status_code=404, detail="Task working directory not found.")

    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(work_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, work_dir)
                zf.write(file_path, arcname)

    zip_io.seek(0)

    return StreamingResponse(
        zip_io,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={task_id}_all_files.zip"
        },
    )


@router.get("/{task_id}/files")
async def get_files(task_id: str = Depends(verify_task_access)):
    try:
        work_dir = get_work_dir(task_id)
        files = get_current_files(work_dir, "all")
        file_all = []

        for i in files:
            file_path = os.path.join(work_dir, i)
            if not os.path.exists(file_path):
                continue

            file_type = i.split(".")[-1]

            # 获取文件信息
            file_info = {
                "filename": i,
                "name": i,  # 兼容前端两种命名
                "file_type": file_type,
                "type": file_type,
            }

            # 尝试获取文件大小和修改时间
            try:
                stat_info = os.stat(file_path)
                file_info["size"] = stat_info.st_size
                file_info["modified_time"] = stat_info.st_mtime
            except Exception as e:
                logger.warning(f"获取文件信息失败: {i}, 错误: {e}")
                file_info["size"] = -1
                file_info["modified_time"] = 0

            file_all.append(file_info)

        return file_all
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    except Exception as e:
        logger.error(f"Failed to get files for task {task_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching files."
        )


@router.get("/{task_id}/open-folder")
async def open_folder(task_id: str = Depends(verify_task_access)):
    try:
        work_dir = get_work_dir(task_id)
        folder_path = Path(work_dir).resolve()

        if not folder_path.is_dir():
            raise HTTPException(status_code=404, detail="Work directory not found.")

        # Use appropriate method to open folder based on OS
        if os.name == "nt":  # Windows
            os.startfile(folder_path)  # nosec
        elif os.name == "posix":  # macOS, Linux
            try:
                subprocess.run(["open", folder_path], check=True)  # macOS  # nosec
            except (FileNotFoundError, subprocess.CalledProcessError):
                subprocess.run(["xdg-open", folder_path], check=True)  # Linux  # nosec
        else:
            raise HTTPException(status_code=501, detail=f"Unsupported OS: {os.name}")

        return {"message": "Folder opened successfully", "work_dir": str(folder_path)}
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Task '{task_id}' work directory not found."
        )
    except Exception as e:
        logger.error(f"Failed to open folder for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not open folder.")


@router.get("/{task_id}/files/content")
async def get_file_content(filename: str, task_id: str = Depends(verify_task_access)):
    """
    获取文件内容用于预览
    支持文本文件类型: txt, md, json, csv, xml, yml, yaml, py, js, ts, vue, html, css, log
    支持图片类型: png, jpg, jpeg, gif, bmp, webp, svg
    """
    safe_filename = secure_filename(unquote(filename))
    try:
        work_dir = get_work_dir(task_id)
        file_path = os.path.join(work_dir, safe_filename)

        # Security check: Ensure the final path is within the working directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(work_dir)):
            raise HTTPException(status_code=403, detail="Forbidden: Access denied.")

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logger.warning(f"File not found: {file_path}")
            raise HTTPException(
                status_code=404, detail=f"File not found: {safe_filename}"
            )

        file_ext = os.path.splitext(safe_filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, detail=f"File type not allowed: {file_ext}"
            )

        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"}
        is_image = file_ext in image_extensions

        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({file_size / 1024 / 1024:.1f}MB). Limit is {MAX_FILE_SIZE / 1024 / 1024:.1f}MB.",
            )

        if is_image:
            with open(file_path, "rb") as f:
                image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            mime_types = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".bmp": "image/bmp",
                ".webp": "image/webp",
                ".svg": "image/svg+xml",
            }
            return {
                "content": image_base64,
                "filename": safe_filename,
                "is_image": True,
                "mime_type": mime_types.get(file_ext, "application/octet-stream"),
                "size": file_size,
            }
        else:
            encodings = ["utf-8", "gbk", "gb2312", "latin-1"]
            content = None
            used_encoding = "unknown"
            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        content = f.read()
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                raise HTTPException(
                    status_code=400, detail="Cannot decode file content."
                )

            return {
                "content": content,
                "filename": safe_filename,
                "is_image": False,
                "encoding": used_encoding,
                "size": file_size,
            }
    except FileNotFoundError:
        # 工作目录不存在时返回 404，而不是 500
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    except HTTPException:
        # 已构造好的 HTTP 异常直接抛出（如 400/403/404）
        raise
    except Exception as e:
        logger.error(f"Error reading file {safe_filename} for task {task_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Could not read file: {safe_filename}"
        )


@router.get("/{task_id}/file-content")
async def get_file_content_compat(
    filename: str, task_id: str = Depends(verify_task_access)
):
    """兼容旧路径 /file-content，内部复用 get_file_content 逻辑。"""
    return await get_file_content(filename=filename, task_id=task_id)


@router.post("/{task_id}/files")
async def upload_file(
    task_id: str = Depends(verify_task_access), file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")

    safe_filename = secure_filename(file.filename)
    file_ext = os.path.splitext(safe_filename)[1].lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail=f"File type not allowed: {file_ext}"
        )

    try:
        work_dir = get_work_dir(task_id)
        file_path = os.path.join(work_dir, safe_filename)

        if os.path.exists(file_path):
            raise HTTPException(
                status_code=409, detail=f"File already exists: {safe_filename}"
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, detail="File size exceeds the 100MB limit."
            )

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"File uploaded successfully: {safe_filename} to task {task_id}")
        return {
            "message": "File uploaded successfully",
            "filename": safe_filename,
            "size": len(content),
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    except Exception as e:
        logger.error(f"File upload failed for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="File upload failed.")


@router.post("/{task_id}/upload")
async def upload_file_compat(
    task_id: str = Depends(verify_task_access),
    files: list[UploadFile] = File(...),
):
    """兼容旧路径 /upload，支持单个或多个文件上传。

    参数名为 files，以兼容现有前端和测试用例：
    - 单文件：files={"files": (filename, BytesIO(...), content_type)}
    - 多文件：files=[("files", (filename1, ...)), ("files", (filename2, ...))]
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    try:
        work_dir = get_work_dir(task_id)
        saved_files: list[str] = []
        total_size = 0

        for upload in files:
            if not upload.filename:
                continue

            safe_filename = secure_filename(upload.filename)
            file_ext = os.path.splitext(safe_filename)[1].lower()

            if file_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, detail=f"File type not allowed: {file_ext}"
                )

            file_path = os.path.join(work_dir, safe_filename)

            content = await upload.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413, detail="File size exceeds the 100MB limit."
                )

            with open(file_path, "wb") as f:
                f.write(content)

            saved_files.append(safe_filename)
            total_size += len(content)

        if not saved_files:
            raise HTTPException(status_code=400, detail="No valid files uploaded.")

        logger.info(
            f"Files uploaded successfully: {saved_files} to task {task_id}, total_size={total_size}"
        )
        return {
            "message": "Files uploaded successfully",
            "filenames": saved_files,
            "total_size": total_size,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="File upload failed.")


@router.delete("/{task_id}/files")
async def delete_file(filename: str, task_id: str = Depends(verify_task_access)):
    try:
        work_dir = get_work_dir(task_id)
        safe_filename = secure_filename(unquote(filename))
        file_path = os.path.join(work_dir, safe_filename)

        if not os.path.abspath(file_path).startswith(os.path.abspath(work_dir)):
            raise HTTPException(status_code=403, detail="Forbidden: Access denied.")

        if not os.path.isfile(file_path):
            raise HTTPException(
                status_code=404, detail=f"File not found: {safe_filename}"
            )

        os.remove(file_path)
        logger.info(f"File deleted successfully: {safe_filename} from task {task_id}")
        return {"message": "File deleted successfully", "filename": safe_filename}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    except HTTPException:
        # 已经构造好的 HTTP 异常（如 404/403），直接抛出
        raise
    except Exception as e:
        logger.error(f"File deletion failed for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="File deletion failed.")


@router.delete("/{task_id}/file")
async def delete_file_compat(filename: str, task_id: str = Depends(verify_task_access)):
    """兼容旧路径 /file，内部复用 delete_file 逻辑。"""
    return await delete_file(filename=filename, task_id=task_id)
