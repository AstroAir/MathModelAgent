"""
任务历史记录模型
用于管理用户的任务历史记录，支持分类和收藏功能
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.enums import CompTemplate
from app.utils.log_util import logger


class TaskHistoryItem(BaseModel):
    """任务历史记录项"""

    task_id: str
    title: str = ""  # 任务标题，从问题描述中提取的简短标题
    description: str = ""  # 任务描述
    task_type: str = "custom"  # 任务类型: custom(自定义), example(示例)
    comp_template: Optional[CompTemplate] = None  # 比赛模板类型
    is_pinned: bool = False  # 是否收藏
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = "completed"  # 任务状态: processing, completed, failed
    file_count: int = 0  # 上传文件数量

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class TaskHistoryManager:
    """任务历史记录管理器"""

    def __init__(self, storage_path: str = "logs/task_history.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_storage_file()

    def _ensure_storage_file(self):
        """确保存储文件存在"""
        if not self.storage_path.exists():
            self._save_tasks([])

    def _load_tasks(self) -> List[TaskHistoryItem]:
        """从文件加载任务历史"""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [TaskHistoryItem(**item) for item in data]
        except Exception as e:
            logger.error(f"加载任务历史失败: {str(e)}")
            return []

    def _save_tasks(self, tasks: List[TaskHistoryItem]):
        """保存任务历史到文件"""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(
                    [task.model_dump() for task in tasks],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            logger.error(f"保存任务历史失败: {str(e)}")
            raise

    def add_task(self, task: TaskHistoryItem) -> TaskHistoryItem:
        """添加任务到历史记录"""
        tasks = self._load_tasks()
        # 检查是否已存在
        existing_index = next(
            (i for i, t in enumerate(tasks) if t.task_id == task.task_id), None
        )
        if existing_index is not None:
            # 更新现有任务
            tasks[existing_index] = task
        else:
            # 添加新任务
            tasks.insert(0, task)  # 新任务放在最前面
        self._save_tasks(tasks)
        return task

    def get_task(self, task_id: str) -> Optional[TaskHistoryItem]:
        """获取单个任务"""
        tasks = self._load_tasks()
        return next((task for task in tasks if task.task_id == task_id), None)

    def get_all_tasks(
        self, task_type: Optional[str] = None, pinned_only: bool = False
    ) -> List[TaskHistoryItem]:
        """
        获取所有任务
        :param task_type: 任务类型过滤 (custom, example)
        :param pinned_only: 是否仅返回收藏的任务
        """
        tasks = self._load_tasks()

        # 按类型过滤
        if task_type:
            tasks = [task for task in tasks if task.task_type == task_type]

        # 按收藏状态过滤
        if pinned_only:
            tasks = [task for task in tasks if task.is_pinned]

        # 排序：收藏的在前，然后按更新时间倒序
        tasks.sort(key=lambda x: (not x.is_pinned, x.updated_at), reverse=True)

        return tasks

    def update_task(self, task_id: str, **updates) -> Optional[TaskHistoryItem]:
        """更新任务信息"""
        tasks = self._load_tasks()
        task_index = next(
            (i for i, t in enumerate(tasks) if t.task_id == task_id), None
        )

        if task_index is None:
            return None

        # 更新字段
        task = tasks[task_index]
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        # 更新时间戳
        task.updated_at = datetime.now().isoformat()

        self._save_tasks(tasks)
        return task

    def toggle_pin(self, task_id: str) -> Optional[TaskHistoryItem]:
        """切换任务的收藏状态"""
        tasks = self._load_tasks()
        task_index = next(
            (i for i, t in enumerate(tasks) if t.task_id == task_id), None
        )

        if task_index is None:
            return None

        tasks[task_index].is_pinned = not tasks[task_index].is_pinned
        tasks[task_index].updated_at = datetime.now().isoformat()

        self._save_tasks(tasks)
        return tasks[task_index]

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        tasks = self._load_tasks()
        original_length = len(tasks)
        tasks = [task for task in tasks if task.task_id != task_id]

        if len(tasks) < original_length:
            self._save_tasks(tasks)
            return True
        return False

    def get_task_count(self, task_type: Optional[str] = None) -> int:
        """获取任务数量"""
        tasks = self._load_tasks()
        if task_type:
            tasks = [task for task in tasks if task.task_type == task_type]
        return len(tasks)


# 全局实例
task_history_manager = TaskHistoryManager()
