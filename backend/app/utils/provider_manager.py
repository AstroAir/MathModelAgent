"""
LLM 提供商和 API Key 管理器

支持：
- 多 API Key 轮询（Round-robin、Least-used、Random）
- 多提供商故障转移
- 自动跳过超限的 Key 和提供商
- 健康状态追踪
"""

import hashlib
import random
import time
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
from app.utils.rate_limiter import RateLimiter, RateLimitExceeded
from app.utils.log_util import logger


class RotationStrategy(str, Enum):
    """API Key 轮询策略"""

    ROUND_ROBIN = "round-robin"
    LEAST_USED = "least-used"
    RANDOM = "random"


@dataclass
class ProviderConfig:
    """提供商配置"""

    name: str
    api_key: str
    model: str
    base_url: str
    priority: int = 1
    rpm: Optional[int] = None
    tpm: Optional[int] = None
    rpd: Optional[int] = None
    enabled: bool = True

    # 运行时状态
    failure_count: int = field(default=0, init=False)
    last_failure_time: float = field(default=0.0, init=False)
    total_requests: int = field(default=0, init=False)

    def get_identifier(self) -> str:
        """获取唯一标识符（API Key 的哈希值）"""
        return hashlib.sha256(f"{self.name}:{self.api_key}".encode()).hexdigest()[:16]

    def is_healthy(
        self, failure_threshold: int = 5, cooldown_seconds: int = 300
    ) -> bool:
        """检查提供商是否健康"""
        if not self.enabled:
            return False

        # 如果失败次数超过阈值，检查是否已过冷却期
        if self.failure_count >= failure_threshold:
            if time.time() - self.last_failure_time < cooldown_seconds:
                return False
            # 冷却期已过，重置失败计数
            self.failure_count = 0

        return True

    def record_success(self):
        """记录成功请求"""
        self.total_requests += 1
        self.failure_count = max(0, self.failure_count - 1)  # 成功后减少失败计数

    def record_failure(self):
        """记录失败请求"""
        self.total_requests += 1
        self.failure_count += 1
        self.last_failure_time = time.time()


class ProviderManager:
    """提供商管理器"""

    def __init__(
        self,
        providers: List[ProviderConfig],
        rotation_strategy: RotationStrategy = RotationStrategy.ROUND_ROBIN,
        auto_retry: bool = True,
        max_retries: int = 3,
    ):
        self.providers = sorted(providers, key=lambda p: p.priority)
        self.rotation_strategy = rotation_strategy
        self.auto_retry = auto_retry
        self.max_retries = max_retries

        # 为每个提供商创建速率限制器
        self.rate_limiters: Dict[str, RateLimiter] = {}
        for provider in self.providers:
            identifier = provider.get_identifier()
            self.rate_limiters[identifier] = RateLimiter(
                identifier=identifier,
                rpm=provider.rpm,
                tpm=provider.tpm,
                rpd=provider.rpd,
            )

        # 轮询索引（用于 round-robin 策略）
        self.current_index = 0

    async def get_next_provider(
        self,
        estimated_tokens: int = 0,
        exclude_providers: Optional[List[str]] = None,
    ) -> Optional[ProviderConfig]:
        """
        获取下一个可用的提供商

        Args:
            estimated_tokens: 预估的 token 使用量
            exclude_providers: 要排除的提供商标识符列表

        Returns:
            ProviderConfig: 可用的提供商配置，如果没有可用的则返回 None
        """
        exclude_providers = exclude_providers or []

        # 过滤健康的提供商
        healthy_providers = [
            p
            for p in self.providers
            if p.is_healthy() and p.get_identifier() not in exclude_providers
        ]

        if not healthy_providers:
            logger.error("No healthy providers available")
            return None

        # 根据策略选择提供商
        if self.rotation_strategy == RotationStrategy.ROUND_ROBIN:
            provider = await self._select_round_robin(
                healthy_providers, estimated_tokens
            )
        elif self.rotation_strategy == RotationStrategy.LEAST_USED:
            provider = await self._select_least_used(
                healthy_providers, estimated_tokens
            )
        elif self.rotation_strategy == RotationStrategy.RANDOM:
            provider = await self._select_random(healthy_providers, estimated_tokens)
        else:
            provider = healthy_providers[0]

        return provider

    async def _select_round_robin(
        self,
        providers: List[ProviderConfig],
        estimated_tokens: int,
    ) -> Optional[ProviderConfig]:
        """Round-robin 选择策略"""
        attempts = 0
        max_attempts = len(providers)

        while attempts < max_attempts:
            provider = providers[self.current_index % len(providers)]
            self.current_index = (self.current_index + 1) % len(providers)

            # 检查速率限制
            identifier = provider.get_identifier()
            rate_limiter = self.rate_limiters[identifier]

            try:
                await rate_limiter.check_and_increment_request(estimated_tokens)
                return provider
            except RateLimitExceeded:
                logger.warning(
                    f"Provider {provider.name} rate limit exceeded, trying next"
                )
                attempts += 1
                continue

        return None

    async def _select_least_used(
        self,
        providers: List[ProviderConfig],
        estimated_tokens: int,
    ) -> Optional[ProviderConfig]:
        """Least-used 选择策略"""
        # 按使用次数排序
        sorted_providers = sorted(providers, key=lambda p: p.total_requests)

        for provider in sorted_providers:
            identifier = provider.get_identifier()
            rate_limiter = self.rate_limiters[identifier]

            try:
                await rate_limiter.check_and_increment_request(estimated_tokens)
                return provider
            except RateLimitExceeded:
                logger.warning(
                    f"Provider {provider.name} rate limit exceeded, trying next"
                )
                continue

        return None

    async def _select_random(
        self,
        providers: List[ProviderConfig],
        estimated_tokens: int,
    ) -> Optional[ProviderConfig]:
        """Random 选择策略"""
        # 随机打乱顺序
        shuffled = providers.copy()
        random.shuffle(shuffled)

        for provider in shuffled:
            identifier = provider.get_identifier()
            rate_limiter = self.rate_limiters[identifier]

            try:
                await rate_limiter.check_and_increment_request(estimated_tokens)
                return provider
            except RateLimitExceeded:
                logger.warning(
                    f"Provider {provider.name} rate limit exceeded, trying next"
                )
                continue

        return None

    async def record_request_result(
        self,
        provider: ProviderConfig,
        success: bool,
        actual_tokens: int = 0,
        estimated_tokens: int = 0,
    ):
        """
        记录请求结果

        Args:
            provider: 提供商配置
            success: 请求是否成功
            actual_tokens: 实际使用的 token 数
            estimated_tokens: 预估的 token 数
        """
        if success:
            provider.record_success()
        else:
            provider.record_failure()

        # 更新实际 token 使用量
        if actual_tokens > 0:
            identifier = provider.get_identifier()
            rate_limiter = self.rate_limiters[identifier]
            await rate_limiter.record_actual_tokens(actual_tokens, estimated_tokens)

    async def get_all_stats(self) -> List[Dict[str, Any]]:
        """获取所有提供商的统计信息"""
        stats = []
        for provider in self.providers:
            identifier = provider.get_identifier()
            rate_limiter = self.rate_limiters[identifier]

            provider_stats = {
                "name": provider.name,
                "model": provider.model,
                "priority": provider.priority,
                "enabled": provider.enabled,
                "healthy": provider.is_healthy(),
                "total_requests": provider.total_requests,
                "failure_count": provider.failure_count,
                "rate_limits": await rate_limiter.get_usage_stats(),
            }
            stats.append(provider_stats)

        return stats

    def get_provider_by_identifier(self, identifier: str) -> Optional[ProviderConfig]:
        """根据标识符获取提供商"""
        for provider in self.providers:
            if provider.get_identifier() == identifier:
                return provider
        return None
