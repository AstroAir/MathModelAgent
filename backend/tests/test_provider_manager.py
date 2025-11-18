"""
提供商管理器单元测试
"""

import pytest
from app.utils.provider_manager import (
    ProviderManager,
    ProviderConfig,
    RotationStrategy,
)


@pytest.fixture
def sample_providers():
    """创建示例提供商配置"""
    return [
        ProviderConfig(
            name="provider1",
            api_key="key1",
            model="model1",
            base_url="https://api1.com",
            priority=1,
            rpm=10,
            tpm=1000,
        ),
        ProviderConfig(
            name="provider2",
            api_key="key2",
            model="model2",
            base_url="https://api2.com",
            priority=2,
            rpm=20,
            tpm=2000,
        ),
        ProviderConfig(
            name="provider3",
            api_key="key3",
            model="model3",
            base_url="https://api3.com",
            priority=3,
            rpm=30,
            tpm=3000,
        ),
    ]


@pytest.mark.asyncio
async def test_round_robin_strategy(sample_providers):
    """测试轮询策略"""
    manager = ProviderManager(
        providers=sample_providers,
        rotation_strategy=RotationStrategy.ROUND_ROBIN,
    )

    # 重置所有速率限制器
    for provider in sample_providers:
        identifier = provider.get_identifier()
        await manager.rate_limiters[identifier].reset()

    # 获取提供商应该按顺序轮询
    provider1 = await manager.get_next_provider()
    assert provider1.name == "provider1"

    provider2 = await manager.get_next_provider()
    assert provider2.name == "provider2"

    provider3 = await manager.get_next_provider()
    assert provider3.name == "provider3"

    # 应该回到第一个
    provider1_again = await manager.get_next_provider()
    assert provider1_again.name == "provider1"


@pytest.mark.asyncio
async def test_least_used_strategy(sample_providers):
    """测试最少使用策略"""
    manager = ProviderManager(
        providers=sample_providers,
        rotation_strategy=RotationStrategy.LEAST_USED,
    )

    # 重置所有速率限制器
    for provider in sample_providers:
        identifier = provider.get_identifier()
        await manager.rate_limiters[identifier].reset()

    # 第一次应该选择第一个（都是 0 次使用）
    provider1 = await manager.get_next_provider()
    assert provider1 is not None

    # 记录使用
    provider1.total_requests = 5
    sample_providers[1].total_requests = 2
    sample_providers[2].total_requests = 3

    # 应该选择使用次数最少的
    provider = await manager.get_next_provider()
    assert provider.name == "provider2"  # 只有 2 次使用


@pytest.mark.asyncio
async def test_provider_health_check(sample_providers):
    """测试提供商健康检查"""
    provider = sample_providers[0]

    # 初始状态应该是健康的
    assert provider.is_healthy() is True

    # 记录多次失败
    for _ in range(5):
        provider.record_failure()

    # 应该变为不健康
    assert provider.is_healthy() is False

    # 记录成功应该减少失败计数
    provider.record_success()
    assert provider.failure_count == 4


@pytest.mark.asyncio
async def test_provider_priority(sample_providers):
    """测试提供商优先级"""
    # 按优先级排序
    sorted_providers = sorted(sample_providers, key=lambda p: p.priority)

    assert sorted_providers[0].name == "provider1"
    assert sorted_providers[1].name == "provider2"
    assert sorted_providers[2].name == "provider3"


@pytest.mark.asyncio
async def test_exclude_providers(sample_providers):
    """测试排除提供商"""
    manager = ProviderManager(
        providers=sample_providers,
        rotation_strategy=RotationStrategy.ROUND_ROBIN,
    )

    # 重置所有速率限制器
    for provider in sample_providers:
        identifier = provider.get_identifier()
        await manager.rate_limiters[identifier].reset()

    # 排除第一个提供商
    exclude_list = [sample_providers[0].get_identifier()]
    provider = await manager.get_next_provider(exclude_providers=exclude_list)

    # 应该跳过第一个
    assert provider.name != "provider1"


@pytest.mark.asyncio
async def test_record_request_result(sample_providers):
    """测试记录请求结果"""
    manager = ProviderManager(
        providers=sample_providers,
        rotation_strategy=RotationStrategy.ROUND_ROBIN,
    )

    provider = sample_providers[0]

    # 记录成功
    await manager.record_request_result(
        provider=provider,
        success=True,
        actual_tokens=500,
        estimated_tokens=400,
    )

    assert provider.total_requests == 1
    assert provider.failure_count == 0

    # 记录失败
    await manager.record_request_result(
        provider=provider,
        success=False,
    )

    assert provider.total_requests == 2
    assert provider.failure_count == 1


@pytest.mark.asyncio
async def test_get_all_stats(sample_providers):
    """测试获取所有统计信息"""
    manager = ProviderManager(
        providers=sample_providers,
        rotation_strategy=RotationStrategy.ROUND_ROBIN,
    )

    # 重置所有速率限制器
    for provider in sample_providers:
        identifier = provider.get_identifier()
        await manager.rate_limiters[identifier].reset()

    # 发送一些请求
    provider = await manager.get_next_provider()
    await manager.record_request_result(provider, success=True)

    # 获取统计信息
    stats = await manager.get_all_stats()

    assert len(stats) == 3
    assert all("name" in stat for stat in stats)
    assert all("rate_limits" in stat for stat in stats)


@pytest.mark.asyncio
async def test_disabled_provider(sample_providers):
    """测试禁用的提供商"""
    # 禁用第一个提供商
    sample_providers[0].enabled = False

    manager = ProviderManager(
        providers=sample_providers,
        rotation_strategy=RotationStrategy.ROUND_ROBIN,
    )

    # 重置所有速率限制器
    for provider in sample_providers:
        identifier = provider.get_identifier()
        await manager.rate_limiters[identifier].reset()

    # 获取提供商应该跳过禁用的
    provider = await manager.get_next_provider()
    assert provider.name != "provider1"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
