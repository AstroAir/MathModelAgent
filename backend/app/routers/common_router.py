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
    return list(config_template.keys())


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
            "total_cost": 0.0
        }
        
        # 读取token使用统计
        if os.path.exists(token_usage_path):
            with open(token_usage_path, "r", encoding="utf-8") as f:
                token_usage = json.load(f)
                result["token_usage"] = token_usage
                # 计算总费用
                result["total_cost"] = sum(
                    agent_data.get("cost", 0.0) 
                    for agent_data in token_usage.values()
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
            "total_cost": 0.0
        }
    except Exception as e:
        logger.error(f"获取任务统计信息失败: {str(e)}")
        return {
            "task_id": task_id,
            "error": str(e),
            "token_usage": None,
            "chat_completion_count": None,
            "total_cost": 0.0
        }


@router.get("/status")
async def get_service_status():
    """获取各个服务的状态"""
    status = {
        "backend": {"status": "running", "message": "Backend service is running"},
        "redis": {"status": "unknown", "message": "Redis connection status unknown"}
    }

    # 检查Redis连接状态
    try:
        redis_client = await redis_manager.get_client()
        await redis_client.ping()
        status["redis"] = {"status": "running", "message": "Redis connection is healthy"}
    except Exception as e:
        logger.error(f"Redis connection failed: {str(e)}")
        status["redis"] = {"status": "error", "message": f"Redis connection failed: {str(e)}"}

    return status
