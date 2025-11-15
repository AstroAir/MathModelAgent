"""
任务历史记录路由
提供历史记录的CRUD操作和收藏功能
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.models.task_history import (
    TaskHistoryItem,
    task_history_manager
)
from app.utils.log_util import logger

router = APIRouter()


class CreateTaskHistoryRequest(BaseModel):
    """创建任务历史记录请求"""
    task_id: str
    title: str = ""
    description: str = ""
    task_type: str = "custom"
    comp_template: Optional[str] = None
    file_count: int = 0


class UpdateTaskHistoryRequest(BaseModel):
    """更新任务历史记录请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TaskHistoryListResponse(BaseModel):
    """任务历史记录列表响应"""
    total: int
    tasks: List[TaskHistoryItem]


@router.post("/history/tasks", response_model=TaskHistoryItem)
async def create_task_history(request: CreateTaskHistoryRequest):
    """
    创建任务历史记录
    """
    try:
        task = TaskHistoryItem(**request.model_dump())
        result = task_history_manager.add_task(task)
        logger.info(f"创建任务历史记录: {result.task_id}")
        return result
    except Exception as e:
        logger.error(f"创建任务历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建任务历史记录失败: {str(e)}")


@router.get("/history/tasks", response_model=TaskHistoryListResponse)
async def get_task_history_list(
    task_type: Optional[str] = None,
    pinned_only: bool = False
):
    """
    获取任务历史记录列表
    :param task_type: 任务类型过滤 (custom, example)
    :param pinned_only: 是否仅返回收藏的任务
    """
    try:
        tasks = task_history_manager.get_all_tasks(
            task_type=task_type,
            pinned_only=pinned_only
        )
        return TaskHistoryListResponse(
            total=len(tasks),
            tasks=tasks
        )
    except Exception as e:
        logger.error(f"获取任务历史记录列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务历史记录列表失败: {str(e)}")


@router.get("/history/tasks/{task_id}", response_model=TaskHistoryItem)
async def get_task_history(task_id: str):
    """
    获取单个任务历史记录
    """
    try:
        task = task_history_manager.get_task(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务历史记录失败: {str(e)}")


@router.patch("/history/tasks/{task_id}", response_model=TaskHistoryItem)
async def update_task_history(task_id: str, request: UpdateTaskHistoryRequest):
    """
    更新任务历史记录
    """
    try:
        # 只更新提供的字段
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        task = task_history_manager.update_task(task_id, **updates)
        
        if task is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        logger.info(f"更新任务历史记录: {task_id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新任务历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新任务历史记录失败: {str(e)}")


@router.post("/history/tasks/{task_id}/toggle-pin", response_model=TaskHistoryItem)
async def toggle_task_pin(task_id: str):
    """
    切换任务的收藏状态
    """
    try:
        task = task_history_manager.toggle_pin(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        action = "收藏" if task.is_pinned else "取消收藏"
        logger.info(f"{action}任务: {task_id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换任务收藏状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"切换任务收藏状态失败: {str(e)}")


@router.delete("/history/tasks/{task_id}")
async def delete_task_history(task_id: str):
    """
    删除任务历史记录
    """
    try:
        success = task_history_manager.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        logger.info(f"删除任务历史记录: {task_id}")
        return {"success": True, "message": "任务已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除任务历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除任务历史记录失败: {str(e)}")


@router.get("/history/tasks/count")
async def get_task_count(task_type: Optional[str] = None):
    """
    获取任务数量统计
    """
    try:
        total = task_history_manager.get_task_count()
        custom_count = task_history_manager.get_task_count("custom")
        example_count = task_history_manager.get_task_count("example")
        
        return {
            "total": total,
            "custom": custom_count,
            "example": example_count
        }
    except Exception as e:
        logger.error(f"获取任务数量统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务数量统计失败: {str(e)}")
