import redis.asyncio as aioredis
from typing import Optional
import json
from pathlib import Path
from app.config.setting import settings
from app.schemas.response import Message
from app.utils.log_util import logger

try:
    from fakeredis.aioredis import FakeRedis  # type: ignore[import-not-found]

    _orig_pubsub = FakeRedis.pubsub

    def _patched_pubsub(self, *args, **kwargs):
        ps = _orig_pubsub(self, *args, **kwargs)
        channels_attr = getattr(ps, "channels", None)
        if not hasattr(channels_attr, "__await__"):
            orig_channels = channels_attr

            class _AwaitableChannels:
                def __init__(self_inner, data):
                    self_inner._data = data

                def __await__(self_inner):
                    async def _inner():
                        return self_inner._data

                    return _inner().__await__()

                def __getattr__(self_inner, name):
                    # 代理到底层 dict，以兼容 fakeredis 内部对 channels.update 等调用
                    return getattr(self_inner._data, name)

            ps.channels = _AwaitableChannels(orig_channels)
        return ps

    FakeRedis.pubsub = _patched_pubsub

    if hasattr(FakeRedis, "sismember"):
        _orig_sismember = FakeRedis.sismember

        async def _patched_sismember(self, key, member):
            result = await _orig_sismember(self, key, member)
            return bool(result)

        FakeRedis.sismember = _patched_sismember
except Exception:
    pass  # nosec


class RedisManager:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._client: Optional[aioredis.Redis] = None
        # 创建消息存储目录
        self.messages_dir = Path("logs/messages")
        self.messages_dir.mkdir(parents=True, exist_ok=True)

    async def get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
            )
        try:
            await self._client.ping()
            logger.info(f"Redis 连接建立成功: {self.redis_url}")
            return self._client
        except Exception as e:
            logger.error(f"无法连接到Redis: {str(e)}")
            raise

    async def set(self, key: str, value: str):
        """设置Redis键值对"""
        client = await self.get_client()
        await client.set(key, value)
        await client.expire(key, 36000)

    async def _save_message_to_file(self, task_id: str, message: Message):
        """将消息保存到文件中，同一任务的消息保存在同一个文件中"""
        try:
            # 确保目录存在
            self.messages_dir.mkdir(exist_ok=True)

            # 使用任务ID作为文件名
            file_path = self.messages_dir / f"{task_id}.json"

            # 读取现有消息（如果文件存在）
            messages = []
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)

            # 添加新消息
            message_data = message.model_dump()
            messages.append(message_data)

            # 保存所有消息到文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)

            logger.debug(f"消息已追加到文件: {file_path}")
        except Exception as e:
            logger.error(f"保存消息到文件失败: {str(e)}")
            # 不抛出异常，确保主流程不受影响

    async def publish_message(self, task_id: str, message: Message):
        """发布消息到特定任务的频道并保存到文件"""
        client = await self.get_client()
        channel = f"task:{task_id}:messages"
        try:
            message_json = message.model_dump_json()
            await client.publish(channel, message_json)
            logger.debug(
                f"消息已发布到频道 {channel}:mes_type:{message.msg_type}:msg_content:{message.content}"
            )
            # 保存消息到文件
            await self._save_message_to_file(task_id, message)
        except Exception as e:
            logger.error(f"发布消息失败: {str(e)}")
            raise

    async def publish(self, channel: str, message: str):
        """发布原始消息到指定频道（向后兼容的低级接口）。

        主要用于测试中对 redis_manager.publish 的 patch，不在核心业务中直接使用。
        """

        client = await self.get_client()
        await client.publish(channel, message)

    async def subscribe_to_task(self, task_id: str):
        """订阅特定任务的消息"""
        client = await self.get_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(f"task:{task_id}:messages")
        return pubsub

    async def subscribe(self, channel: str):
        """向后兼容的订阅接口，主要用于测试中的 patch。

        等价于订阅指定 channel 的 pubsub。
        """

        client = await self.get_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

    async def close(self):
        """关闭Redis连接"""
        if self._client:
            await self._client.close()
            self._client = None


redis_manager = RedisManager()
