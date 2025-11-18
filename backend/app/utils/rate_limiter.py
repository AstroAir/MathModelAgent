"""
速率限制器模块

实现基于 Redis 的滑动窗口速率限制，支持：
- RPM (Requests Per Minute) 限制
- TPM (Tokens Per Minute) 限制
- RPD (Requests Per Day) 限制
- 自动延迟和重试机制
"""

import time
from typing import Optional
from app.services.redis_manager import redis_manager
from app.utils.log_util import logger


class RateLimitExceeded(Exception):
    """速率限制超出异常"""

    def __init__(self, message: str, retry_after: float = 0):
        super().__init__(message)
        self.retry_after = retry_after


class RateLimiter:
    """基于 Redis 的速率限制器"""

    def __init__(
        self,
        identifier: str,  # 唯一标识符（如 API Key 的哈希值或提供商名称）
        rpm: Optional[int] = None,  # 每分钟请求数限制
        tpm: Optional[int] = None,  # 每分钟 token 数限制
        rpd: Optional[int] = None,  # 每日请求数限制
    ):
        self.identifier = identifier
        self.rpm = rpm
        self.tpm = tpm
        self.rpd = rpd

        # Redis key 前缀
        self.rpm_key = f"rate_limit:{identifier}:rpm"
        self.tpm_key = f"rate_limit:{identifier}:tpm"
        self.rpd_key = f"rate_limit:{identifier}:rpd"
        self.tokens_key = f"rate_limit:{identifier}:tokens"

    async def check_and_increment_request(self, estimated_tokens: int = 0) -> bool:
        """
        检查是否可以发起请求，如果可以则增加计数

        Args:
            estimated_tokens: 预估的 token 使用量

        Returns:
            bool: 是否允许请求

        Raises:
            RateLimitExceeded: 当超出速率限制时
        """
        # 检查 RPM 限制
        if self.rpm:
            rpm_count = await self._get_count(self.rpm_key, 60)
            if rpm_count >= self.rpm:
                retry_after = await self._get_retry_after(self.rpm_key, 60)
                logger.warning(
                    f"RPM limit exceeded for {self.identifier}: "
                    f"{rpm_count}/{self.rpm}, retry after {retry_after:.2f}s"
                )
                raise RateLimitExceeded(
                    f"RPM limit exceeded: {rpm_count}/{self.rpm}",
                    retry_after=retry_after,
                )

        # 检查 TPM 限制
        if self.tpm and estimated_tokens > 0:
            tpm_count = await self._get_token_count(60)
            if tpm_count + estimated_tokens > self.tpm:
                retry_after = await self._get_retry_after(self.tokens_key, 60)
                logger.warning(
                    f"TPM limit exceeded for {self.identifier}: "
                    f"{tpm_count + estimated_tokens}/{self.tpm}, retry after {retry_after:.2f}s"
                )
                raise RateLimitExceeded(
                    f"TPM limit exceeded: {tpm_count + estimated_tokens}/{self.tpm}",
                    retry_after=retry_after,
                )

        # 检查 RPD 限制
        if self.rpd:
            rpd_count = await self._get_count(self.rpd_key, 86400)
            if rpd_count >= self.rpd:
                retry_after = await self._get_retry_after(self.rpd_key, 86400)
                logger.warning(
                    f"RPD limit exceeded for {self.identifier}: "
                    f"{rpd_count}/{self.rpd}, retry after {retry_after:.2f}s"
                )
                raise RateLimitExceeded(
                    f"RPD limit exceeded: {rpd_count}/{self.rpd}",
                    retry_after=retry_after,
                )

        # 所有检查通过，增加计数
        await self._increment_request(estimated_tokens)
        return True

    async def record_actual_tokens(self, actual_tokens: int, estimated_tokens: int = 0):
        """
        记录实际使用的 token 数量（在请求完成后调用）

        Args:
            actual_tokens: 实际使用的 token 数
            estimated_tokens: 之前预估的 token 数
        """
        if not self.tpm:
            return

        # 如果实际使用量与预估不同，调整计数
        if actual_tokens != estimated_tokens:
            adjustment = actual_tokens - estimated_tokens
            await self._adjust_token_count(adjustment, 60)

    async def _increment_request(self, estimated_tokens: int = 0):
        """增加请求计数和 token 计数"""
        redis = redis_manager.redis
        current_time = time.time()

        # 增加 RPM 计数
        if self.rpm:
            await redis.zadd(self.rpm_key, {str(current_time): current_time})
            await redis.expire(self.rpm_key, 60)

        # 增加 RPD 计数
        if self.rpd:
            await redis.zadd(self.rpd_key, {str(current_time): current_time})
            await redis.expire(self.rpd_key, 86400)

        # 增加 TPM 计数
        if self.tpm and estimated_tokens > 0:
            await redis.zadd(
                self.tokens_key, {f"{current_time}:{estimated_tokens}": current_time}
            )
            await redis.expire(self.tokens_key, 60)

    async def _get_count(self, key: str, window_seconds: int) -> int:
        """获取指定时间窗口内的请求计数"""
        redis = redis_manager.redis
        current_time = time.time()
        window_start = current_time - window_seconds

        # 清理过期数据
        await redis.zremrangebyscore(key, 0, window_start)

        # 获取当前窗口内的计数
        count = await redis.zcard(key)
        return count

    async def _get_token_count(self, window_seconds: int) -> int:
        """获取指定时间窗口内的 token 使用量"""
        redis = redis_manager.redis
        current_time = time.time()
        window_start = current_time - window_seconds

        # 清理过期数据
        await redis.zremrangebyscore(self.tokens_key, 0, window_start)

        # 获取所有记录并累加 token 数
        records = await redis.zrange(self.tokens_key, 0, -1)
        total_tokens = 0
        for record in records:
            try:
                # 记录格式: "timestamp:token_count"
                _, token_count = record.decode().split(":")
                total_tokens += int(token_count)
            except (ValueError, AttributeError):
                continue

        return total_tokens

    async def _adjust_token_count(self, adjustment: int, window_seconds: int):
        """调整 token 计数（用于修正预估值）"""
        redis = redis_manager.redis
        current_time = time.time()

        # 添加调整记录
        await redis.zadd(
            self.tokens_key, {f"{current_time}:adj:{adjustment}": current_time}
        )
        await redis.expire(self.tokens_key, window_seconds)

    async def _get_retry_after(self, key: str, window_seconds: int) -> float:
        """计算需要等待多久才能重试"""
        redis = redis_manager.redis
        current_time = time.time()

        # 获取最早的记录
        oldest_records = await redis.zrange(key, 0, 0, withscores=True)
        if not oldest_records:
            return 0.0

        oldest_time = oldest_records[0][1]
        retry_after = (oldest_time + window_seconds) - current_time
        return max(0.0, retry_after)

    async def get_usage_stats(self) -> dict:
        """获取当前使用统计"""
        stats = {
            "identifier": self.identifier,
            "limits": {
                "rpm": self.rpm,
                "tpm": self.tpm,
                "rpd": self.rpd,
            },
            "current": {},
        }

        if self.rpm:
            rpm_count = await self._get_count(self.rpm_key, 60)
            stats["current"]["rpm"] = rpm_count
            stats["current"]["rpm_percentage"] = (
                (rpm_count / self.rpm * 100) if self.rpm else 0
            )

        if self.tpm:
            tpm_count = await self._get_token_count(60)
            stats["current"]["tpm"] = tpm_count
            stats["current"]["tpm_percentage"] = (
                (tpm_count / self.tpm * 100) if self.tpm else 0
            )

        if self.rpd:
            rpd_count = await self._get_count(self.rpd_key, 86400)
            stats["current"]["rpd"] = rpd_count
            stats["current"]["rpd_percentage"] = (
                (rpd_count / self.rpd * 100) if self.rpd else 0
            )

        return stats

    async def reset(self):
        """重置所有计数器"""
        redis = redis_manager.redis
        await redis.delete(self.rpm_key, self.tpm_key, self.rpd_key, self.tokens_key)
        logger.info(f"Rate limiter reset for {self.identifier}")
