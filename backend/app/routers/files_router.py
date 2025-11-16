from fastapi import APIRouter
from app.utils.common_utils import get_current_files, get_work_dir
import os
import subprocess
import base64
from urllib.parse import unquote
from icecream import ic
from fastapi import HTTPException

router = APIRouter()


@router.get("/download_url")
async def get_download_url(task_id: str, filename: str):
    return {"download_url": f"http://localhost:8000/static/{task_id}/{filename}"}


@router.get("/download_all_url")
async def get_download_all_url(task_id: str):
    return {"download_url": f"http://localhost:8000/static/{task_id}/all.zip"}


@router.get("/files")
async def get_files(task_id: str):
    work_dir = get_work_dir(task_id)
    files = get_current_files(work_dir, "all")
    file_all = []

    for i in files:
        file_type = i.split(".")[-1]
        file_path = os.path.join(work_dir, i)
        
        # 获取文件信息
        file_info = {
            "filename": i,
            "name": i,  # 兼容前端两种命名
            "file_type": file_type,
            "type": file_type
        }
        
        # 尝试获取文件大小和修改时间
        try:
            if os.path.exists(file_path):
                stat_info = os.stat(file_path)
                file_info["size"] = stat_info.st_size
                file_info["modified_time"] = stat_info.st_mtime
        except Exception as e:
            ic(f"获取文件信息失败: {i}, 错误: {e}")
        
        file_all.append(file_info)

    return file_all


@router.get("/open_folder")
async def open_folder(task_id: str):
    ic(task_id)
    # 打开工作目录
    work_dir = get_work_dir(task_id)

    # 打开工作目录
    if os.name == "nt":
        subprocess.run(["explorer", work_dir])
    elif os.name == "posix":
        subprocess.run(["open", work_dir])
    else:
        raise HTTPException(status_code=500, detail=f"不支持的操作系统: {os.name}")

    return {"message": "打开工作目录成功", "work_dir": work_dir}


@router.get("/file_content")
async def get_file_content(task_id: str, filename: str):
    """
    获取文件内容用于预览
    支持文本文件类型: txt, md, json, csv, xml, yml, yaml, py, js, ts, vue, html, css, log
    支持图片类型: png, jpg, jpeg, gif, bmp, webp, svg
    """
    try:
        work_dir = get_work_dir(task_id)
    except FileNotFoundError as e:
        ic(f"工作目录不存在: task_id={task_id}")
        raise HTTPException(status_code=404, detail=str(e))
    
    # FastAPI通常会自动解码URL参数，但为了处理可能的编码问题，我们尝试解码
    # 先使用原始文件名，如果文件不存在，再尝试URL解码后的文件名
    decoded_filename = unquote(filename)
    ic(f"接收到的文件名: original={filename}, decoded={decoded_filename}")
    
    # 首先尝试原始文件名（已经被FastAPI解码）
    file_path = os.path.join(work_dir, filename)
    
    # 如果文件不存在且原始文件名与解码后不同，尝试解码后的文件名
    if not os.path.exists(file_path) and decoded_filename != filename:
        file_path = os.path.join(work_dir, decoded_filename)
        ic(f"尝试解码后的文件名: {decoded_filename}")
    
    ic(f"最终文件路径: work_dir={work_dir}, file_path={file_path}")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        # 列出目录中的所有文件，帮助调试
        try:
            files_in_dir = os.listdir(work_dir) if os.path.exists(work_dir) else []
            ic(f"目录中的文件: {files_in_dir}")
        except Exception:
            pass
        raise HTTPException(status_code=404, detail=f"文件不存在: {filename}，路径：{file_path}")
    
    # 检查是否为文件
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=400, detail=f"不是一个文件: {filename}")
    
    # 支持的文件扩展名
    text_extensions = {'.txt', '.md', '.json', '.csv', '.xml', '.yml', '.yaml', 
                      '.py', '.js', '.ts', '.vue', '.html', '.css', '.log'}
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}
    file_ext = os.path.splitext(filename)[1].lower()
    
    # 检查文件类型
    is_text = file_ext in text_extensions
    is_image = file_ext in image_extensions
    
    if not is_text and not is_image:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_ext}")
    
    try:
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        MAX_SIZE = 10 * 1024 * 1024  # 10MB 限制
        
        if file_size > MAX_SIZE:
            raise HTTPException(status_code=400, detail=f"文件过大 ({file_size / 1024 / 1024:.1f}MB)，超过10MB限制")
        
        # 如果是图片，返回base64编码
        if is_image:
            with open(file_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 确定MIME类型
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml'
            }
            mime_type = mime_types.get(file_ext, 'image/png')
            
            ic(f"图片预览: {filename}, 大小: {file_size}, 类型: {mime_type}")
            
            return {
                "content": image_base64,
                "filename": filename,
                "is_image": True,
                "mime_type": mime_type,
                "size": file_size
            }
        
        # 文本文件处理
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'iso-8859-1']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                    content = f.read()
                used_encoding = encoding
                break
            except (UnicodeDecodeError, LookupError):
                continue
        
        if content is None:
            # 如果所有编码都失败，尝试用二进制模式读取并转换
            try:
                with open(file_path, 'rb') as f:
                    raw_content = f.read()
                content = raw_content.decode('utf-8', errors='replace')
                used_encoding = 'utf-8 (with errors replaced)'
            except Exception:
                raise HTTPException(status_code=500, detail="无法解码文件内容，可能是二进制文件")
        
        # 限制预览内容大小
        truncated = False
        MAX_PREVIEW_CHARS = 1024 * 1024  # 1MB 字符
        
        if len(content) > MAX_PREVIEW_CHARS:
            content = content[:MAX_PREVIEW_CHARS]
            truncated = True
        
        ic(f"文件预览: {filename}, 大小: {file_size}, 编码: {used_encoding}, 截断: {truncated}")
        
        return {
            "content": content,
            "filename": filename,
            "is_image": False,
            "truncated": truncated,
            "encoding": used_encoding,
            "size": file_size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        ic(f"读取文件失败: {filename}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")
