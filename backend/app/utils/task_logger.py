import json
from datetime import datetime
from app.services.redis_manager import redis_manager
from app.utils.log_util import logger as global_logger


class TaskLogger:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.log_key = f"task:{self.task_id}:logs"

    async def _log(self, level: str, message: str):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
        }
        try:
            redis_client = await redis_manager.get_client()
            await redis_client.rpush(self.log_key, json.dumps(log_entry))
            # Also log to global logger for backend visibility
            global_logger.log(level.upper(), f"[TASK:{self.task_id}] {message}")
        except Exception as e:
            global_logger.error(
                f"Failed to write task log to Redis for task {self.task_id}: {e}"
            )

    async def info(self, message: str):
        await self._log("info", message)

    async def warning(self, message: str):
        await self._log("warning", message)

    async def error(self, message: str):
        await self._log("error", message)

    async def debug(self, message: str):
        await self._log("debug", message)

    async def success(self, message: str):
        await self._log("success", message)
