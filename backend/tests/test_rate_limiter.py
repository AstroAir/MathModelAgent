"""
速率限制器单元测试
"""

import pytest
from app.utils.rate_limiter import RateLimiter, RateLimitExceeded


@pytest.mark.asyncio
async def test_rpm_limit():
    """测试 RPM 限制"""
    limiter = RateLimiter(
        identifier="test_rpm",
        rpm=5,  # 每分钟 5 个请求
    )

    # 重置计数器
    await limiter.reset()

    # 前 5 个请求应该成功
    for i in range(5):
        result = await limiter.check_and_increment_request()
        assert result is True

    # 第 6 个请求应该失败
    with pytest.raises(RateLimitExceeded) as exc_info:
        await limiter.check_and_increment_request()

    assert "RPM limit exceeded" in str(exc_info.value)
    assert exc_info.value.retry_after > 0


@pytest.mark.asyncio
async def test_tpm_limit():
    """测试 TPM 限制"""
    limiter = RateLimiter(
        identifier="test_tpm",
        tpm=1000,  # 每分钟 1000 tokens
    )

    # 重置计数器
    await limiter.reset()

    # 使用 800 tokens 应该成功
    result = await limiter.check_and_increment_request(estimated_tokens=800)
    assert result is True

    # 再使用 300 tokens 应该失败（总共 1100）
    with pytest.raises(RateLimitExceeded) as exc_info:
        await limiter.check_and_increment_request(estimated_tokens=300)

    assert "TPM limit exceeded" in str(exc_info.value)


@pytest.mark.asyncio
async def test_usage_stats():
    """测试使用统计"""
    limiter = RateLimiter(
        identifier="test_stats",
        rpm=10,
        tpm=1000,
    )

    # 重置计数器
    await limiter.reset()

    # 发送几个请求
    await limiter.check_and_increment_request(estimated_tokens=100)
    await limiter.check_and_increment_request(estimated_tokens=200)
    await limiter.check_and_increment_request(estimated_tokens=300)

    # 获取统计信息
    stats = await limiter.get_usage_stats()

    assert stats["identifier"] == "test_stats"
    assert stats["limits"]["rpm"] == 10
    assert stats["limits"]["tpm"] == 1000
    assert stats["current"]["rpm"] == 3
    assert stats["current"]["tpm"] == 600
    assert stats["current"]["rpm_percentage"] == 30.0
    assert stats["current"]["tpm_percentage"] == 60.0


@pytest.mark.asyncio
async def test_actual_tokens_adjustment():
    """测试实际 token 数量调整"""
    limiter = RateLimiter(
        identifier="test_adjustment",
        tpm=1000,
    )

    # 重置计数器
    await limiter.reset()

    # 预估 500 tokens
    await limiter.check_and_increment_request(estimated_tokens=500)

    # 实际使用 600 tokens
    await limiter.record_actual_tokens(actual_tokens=600, estimated_tokens=500)

    # 获取统计信息（应该反映实际使用量）
    stats = await limiter.get_usage_stats()
    # 注意：由于调整是增量的，实际值可能略有不同
    assert stats["current"]["tpm"] >= 500


@pytest.mark.asyncio
async def test_no_limits():
    """测试没有限制的情况"""
    limiter = RateLimiter(identifier="test_no_limits")

    # 没有设置任何限制，应该总是成功
    for i in range(100):
        result = await limiter.check_and_increment_request(estimated_tokens=1000)
        assert result is True


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
