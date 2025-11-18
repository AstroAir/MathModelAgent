# e2b_interpreter.py
# 兼容性占位实现：当前开发环境默认使用 LocalCodeInterpreter，
# 只要 E2B_API_KEY 未配置，interpreter_factory 会强制选择本地解释器。
# 该文件仅用于满足 `from app.tools.e2b_interpreter import E2BCodeInterpreter` 导入，
# 实际不会在本地环境中走到远程解释器分支。

from __future__ import annotations

from typing import TYPE_CHECKING

from app.tools.base_interpreter import BaseCodeInterpreter
from app.tools.notebook_serializer import NotebookSerializer
from app.utils.log_util import logger

if TYPE_CHECKING:  # 仅类型检查使用，运行时无额外开销
    pass


class E2BCodeInterpreter(BaseCodeInterpreter):
    """占位远程解释器实现。

    在本地开发环境（未设置 E2B_API_KEY）下不会被实际使用，
    仅用于避免导入错误。如果真的被调用，会显式抛出异常，
    提示需要正确配置 E2B 集成。
    """

    def __init__(
        self,
        task_id: str,
        work_dir: str,
        notebook_serializer: NotebookSerializer,
    ) -> None:
        super().__init__(
            task_id=task_id, work_dir=work_dir, notebook_serializer=notebook_serializer
        )

    @classmethod
    async def create(
        cls,
        *,
        task_id: str,
        work_dir: str,
        notebook_serializer: NotebookSerializer,
    ) -> "E2BCodeInterpreter":
        logger.warning(
            "E2BCodeInterpreter.create 被调用：当前仅为占位实现，如需使用远程解释器，请实现真实的 E2B 集成。"
        )
        return cls(
            task_id=task_id, work_dir=work_dir, notebook_serializer=notebook_serializer
        )

    async def initialize(self, timeout: int = 3000) -> None:  # type: ignore[override]
        logger.error("E2BCodeInterpreter.initialize 被调用，但当前仅为占位实现。")
        raise RuntimeError(
            "E2B 远程解释器未实现，请在生产环境中提供真实实现或避免使用 remote 模式。"
        )

    async def _pre_execute_code(self) -> None:  # type: ignore[override]
        raise RuntimeError("E2B 远程解释器未实现。")

    async def execute_code(self, code: str) -> tuple[str, bool, str]:  # type: ignore[override]
        raise RuntimeError("E2B 远程解释器未实现，无法执行代码。")

    async def cleanup(self) -> None:  # type: ignore[override]
        # 占位实现：无实际资源需要清理
        logger.info("E2BCodeInterpreter.cleanup 调用（占位实现）。")

    async def get_created_images(self, section: str) -> list[str]:  # type: ignore[override]
        # 占位实现：远程解释器暂不支持图片收集
        logger.info("E2BCodeInterpreter.get_created_images 调用（占位实现）。")
        return []
