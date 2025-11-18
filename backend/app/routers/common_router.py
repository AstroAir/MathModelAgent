from fastapi import APIRouter
from app.config.setting import settings
from app.utils.common_utils import get_config_template
from app.schemas.enums import CompTemplate
from app.services.redis_manager import redis_manager
from app.utils.log_util import logger
import os
import json

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.get("/config")
async def config():
    return {
        "environment": settings.ENV,
        "deepseek_model": settings.DEEPSEEK_MODEL,
        "deepseek_base_url": settings.DEEPSEEK_BASE_URL,
        "max_chat_turns": settings.MAX_CHAT_TURNS,
        "max_retries": settings.MAX_RETRIES,
        "CORS_ALLOW_ORIGINS": settings.CORS_ALLOW_ORIGINS,
    }


@router.get("/writer_seque")
async def get_writer_seque():
    # 返回论文顺序
    config_template: dict = get_config_template(CompTemplate.CHINA)
    return {"writer_seque": list(config_template.keys())}


@router.get("/track")
async def track(task_id: str):
    """获取任务的token使用情况"""
    try:
        from app.utils.common_utils import get_work_dir

        # 获取工作目录
        work_dir = get_work_dir(task_id)

        # 读取token使用情况
        token_usage_path = os.path.join(work_dir, "token_usage.json")
        chat_completion_path = os.path.join(work_dir, "chat_completion.json")

        result = {
            "task_id": task_id,
            "token_usage": None,
            "chat_completion_count": None,
            "total_cost": 0.0,
        }

        # 读取token使用统计
        if os.path.exists(token_usage_path):
            with open(token_usage_path, "r", encoding="utf-8") as f:
                token_usage = json.load(f)
                result["token_usage"] = token_usage
                # 计算总费用
                result["total_cost"] = sum(
                    agent_data.get("cost", 0.0) for agent_data in token_usage.values()
                )

        # 读取聊天完成记录数
        if os.path.exists(chat_completion_path):
            with open(chat_completion_path, "r", encoding="utf-8") as f:
                chat_completion = json.load(f)
                result["chat_completion_count"] = {
                    agent: len(completions)
                    for agent, completions in chat_completion.items()
                }

        return result

    except FileNotFoundError as e:
        logger.warning(f"任务 {task_id} 的统计文件不存在: {str(e)}")
        return {
            "task_id": task_id,
            "error": "Task not found or no statistics available",
            "token_usage": None,
            "chat_completion_count": None,
            "total_cost": 0.0,
        }
    except Exception as e:
        logger.error(f"获取任务统计信息失败: {str(e)}")
        return {
            "task_id": task_id,
            "error": str(e),
            "token_usage": None,
            "chat_completion_count": None,
            "total_cost": 0.0,
        }


@router.get("/status")
async def get_service_status():
    """获取各个服务的状态"""
    status = {
        "backend": {"status": "running", "message": "Backend service is running"},
        "redis": {"status": "unknown", "message": "Redis connection status unknown"},
    }

    # 检查Redis连接状态
    try:
        redis_client = await redis_manager.get_client()
        await redis_client.ping()
        status["redis"] = {
            "status": "running",
            "message": "Redis connection is healthy",
        }
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}")
        status["redis"] = {
            "status": "error",
            "message": f"Redis connection failed: {str(e)}",
        }

    return status


@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        redis_client = await redis_manager.get_client()

        # 检查任务是否存在
        task_exists = await redis_client.exists(f"task_id:{task_id}")
        if not task_exists:
            return {
                "task_id": task_id,
                "status": "not_found",
                "message": "Task not found",
            }

        # 获取任务状态
        status = await redis_client.get(f"task:{task_id}:status")
        status_str = (
            status.decode() if isinstance(status, bytes) else (status or "unknown")
        )

        return {
            "task_id": task_id,
            "status": status_str,
            "message": f"Task is {status_str}",
        }
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        return {"task_id": task_id, "status": "error", "message": str(e)}


@router.get("/logs/{task_id}")
async def get_task_logs(task_id: str):
    """获取任务执行日志"""
    try:
        from app.utils.common_utils import get_work_dir

        # 获取工作目录
        work_dir = get_work_dir(task_id)

        # 尝试从Redis获取实时日志
        redis_client = await redis_manager.get_client()
        log_key = f"task:{task_id}:logs"

        # 获取Redis中的日志（如果存在）
        redis_logs = await redis_client.lrange(log_key, 0, -1)

        logs = []
        if redis_logs:
            # 解析Redis日志
            for log_entry in redis_logs:
                try:
                    log_data = json.loads(log_entry)
                    logs.append(log_data)
                except json.JSONDecodeError:
                    # 如果不是JSON格式，作为普通文本处理
                    logs.append(
                        {
                            "timestamp": "",
                            "level": "INFO",
                            "message": log_entry.decode()
                            if isinstance(log_entry, bytes)
                            else log_entry,
                        }
                    )

        # 如果Redis中没有日志，尝试从文件读取
        if not logs:
            log_file_path = os.path.join(work_dir, "execution.log")
            if os.path.exists(log_file_path):
                with open(log_file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            # 尝试解析日志格式 [timestamp] level: message
                            import re

                            match = re.match(r"\[([^\]]+)\]\s+(\w+):\s+(.+)", line)
                            if match:
                                logs.append(
                                    {
                                        "timestamp": match.group(1),
                                        "level": match.group(2),
                                        "message": match.group(3),
                                    }
                                )
                            else:
                                logs.append(
                                    {"timestamp": "", "level": "INFO", "message": line}
                                )

        return {"task_id": task_id, "logs": logs, "total": len(logs)}

    except FileNotFoundError:
        logger.warning(f"任务 {task_id} 的日志文件不存在")
        return {
            "task_id": task_id,
            "logs": [],
            "total": 0,
            "message": "No logs available yet",
        }
    except Exception as e:
        logger.error(f"获取任务日志失败: {str(e)}")
        return {"task_id": task_id, "error": str(e), "logs": [], "total": 0}
