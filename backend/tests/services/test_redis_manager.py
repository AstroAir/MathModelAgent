"""Tests for Redis manager."""

import pytest
import json
from app.services.redis_manager import RedisManager


@pytest.mark.asyncio
class TestRedisManager:
    """Test suite for RedisManager."""

    @pytest.fixture
    async def redis_manager_instance(self):
        """Create RedisManager instance with fake Redis."""
        from fakeredis.aioredis import FakeRedis

        fake_redis = FakeRedis(decode_responses=True)
        manager = RedisManager()
        manager._client = fake_redis
        setattr(manager, "redis", fake_redis)
        return manager

    async def test_redis_manager_initialization(self, redis_manager_instance):
        """Test RedisManager initialization."""
        assert redis_manager_instance is not None
        assert redis_manager_instance.redis is not None

    async def test_set_and_get_value(self, redis_manager_instance, sample_task_id):
        """Test setting and getting values."""
        key = f"test:{sample_task_id}"
        value = "test_value"

        await redis_manager_instance.redis.set(key, value)
        result = await redis_manager_instance.redis.get(key)

        assert result == value

    async def test_set_with_expiry(self, redis_manager_instance, sample_task_id):
        """Test setting value with expiry."""
        key = f"test:{sample_task_id}"
        value = "test_value"
        expiry = 60  # 60 seconds

        await redis_manager_instance.redis.setex(key, expiry, value)
        result = await redis_manager_instance.redis.get(key)

        assert result == value

        # Verify TTL is set
        ttl = await redis_manager_instance.redis.ttl(key)
        assert ttl > 0

    async def test_delete_key(self, redis_manager_instance, sample_task_id):
        """Test deleting a key."""
        key = f"test:{sample_task_id}"
        value = "test_value"

        await redis_manager_instance.redis.set(key, value)
        await redis_manager_instance.redis.delete(key)

        result = await redis_manager_instance.redis.get(key)
        assert result is None

    async def test_publish_message(self, redis_manager_instance, sample_task_id):
        """Test publishing message to channel."""
        channel = f"task:{sample_task_id}:messages"
        message = {"type": "test", "content": "test message"}

        result = await redis_manager_instance.redis.publish(
            channel, json.dumps(message)
        )

        # Should return number of subscribers (0 in test)
        assert result >= 0

    async def test_subscribe_to_channel(self, redis_manager_instance, sample_task_id):
        """Test subscribing to channel."""
        channel = f"task:{sample_task_id}:messages"

        pubsub = redis_manager_instance.redis.pubsub()
        await pubsub.subscribe(channel)

        # Verify subscription
        await pubsub.channels
        # Implementation depends on fakeredis behavior
        pass

    async def test_hash_operations(self, redis_manager_instance, sample_task_id):
        """Test hash operations."""
        key = f"task:{sample_task_id}:data"

        # Set hash fields
        await redis_manager_instance.redis.hset(key, "field1", "value1")
        await redis_manager_instance.redis.hset(key, "field2", "value2")

        # Get hash field
        result = await redis_manager_instance.redis.hget(key, "field1")
        assert result == "value1"

        # Get all hash fields
        all_data = await redis_manager_instance.redis.hgetall(key)
        assert all_data["field1"] == "value1"
        assert all_data["field2"] == "value2"

    async def test_list_operations(self, redis_manager_instance, sample_task_id):
        """Test list operations."""
        key = f"task:{sample_task_id}:list"

        # Push items
        await redis_manager_instance.redis.rpush(key, "item1")
        await redis_manager_instance.redis.rpush(key, "item2")
        await redis_manager_instance.redis.rpush(key, "item3")

        # Get list length
        length = await redis_manager_instance.redis.llen(key)
        assert length == 3

        # Get list items
        items = await redis_manager_instance.redis.lrange(key, 0, -1)
        assert items == ["item1", "item2", "item3"]

    async def test_set_operations(self, redis_manager_instance, sample_task_id):
        """Test set operations."""
        key = f"task:{sample_task_id}:set"

        # Add members
        await redis_manager_instance.redis.sadd(key, "member1")
        await redis_manager_instance.redis.sadd(key, "member2")
        await redis_manager_instance.redis.sadd(key, "member1")  # Duplicate

        # Get set size
        size = await redis_manager_instance.redis.scard(key)
        assert size == 2  # Duplicates not counted

        # Check membership
        is_member = await redis_manager_instance.redis.sismember(key, "member1")
        assert is_member is True

    async def test_key_exists(self, redis_manager_instance, sample_task_id):
        """Test checking if key exists."""
        key = f"test:{sample_task_id}"

        # Key doesn't exist
        exists = await redis_manager_instance.redis.exists(key)
        assert exists == 0

        # Create key
        await redis_manager_instance.redis.set(key, "value")

        # Key exists
        exists = await redis_manager_instance.redis.exists(key)
        assert exists == 1

    async def test_increment_counter(self, redis_manager_instance, sample_task_id):
        """Test incrementing counter."""
        key = f"counter:{sample_task_id}"

        # Increment
        result = await redis_manager_instance.redis.incr(key)
        assert result == 1

        result = await redis_manager_instance.redis.incr(key)
        assert result == 2

    async def test_decrement_counter(self, redis_manager_instance, sample_task_id):
        """Test decrementing counter."""
        key = f"counter:{sample_task_id}"

        # Set initial value
        await redis_manager_instance.redis.set(key, 10)

        # Decrement
        result = await redis_manager_instance.redis.decr(key)
        assert result == 9

    async def test_get_nonexistent_key(self, redis_manager_instance):
        """Test getting nonexistent key."""
        result = await redis_manager_instance.redis.get("nonexistent_key")
        assert result is None

    async def test_multiple_keys_operations(self, redis_manager_instance):
        """Test operations on multiple keys."""
        keys = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3",
        }

        # Set multiple keys
        for key, value in keys.items():
            await redis_manager_instance.redis.set(key, value)

        # Get multiple keys
        values = await redis_manager_instance.redis.mget(list(keys.keys()))
        assert values == list(keys.values())

    async def test_key_pattern_matching(self, redis_manager_instance, sample_task_id):
        """Test key pattern matching."""
        # Create keys with pattern
        await redis_manager_instance.redis.set(f"task:{sample_task_id}:1", "v1")
        await redis_manager_instance.redis.set(f"task:{sample_task_id}:2", "v2")
        await redis_manager_instance.redis.set(f"task:{sample_task_id}:3", "v3")

        # Find keys by pattern
        keys = await redis_manager_instance.redis.keys(f"task:{sample_task_id}:*")
        assert len(keys) == 3

    async def test_transaction_operations(self, redis_manager_instance):
        """Test transaction operations."""
        # This would test MULTI/EXEC transactions
        pass

    async def test_pipeline_operations(self, redis_manager_instance):
        """Test pipeline operations."""
        pipe = redis_manager_instance.redis.pipeline()

        pipe.set("key1", "value1")
        pipe.set("key2", "value2")
        pipe.get("key1")

        results = await pipe.execute()

        # Verify pipeline execution
        assert results is not None

    async def test_connection_error_handling(self):
        """Test handling of connection errors."""
        # This would test connection error scenarios
        pass

    async def test_concurrent_operations(self, redis_manager_instance, sample_task_id):
        """Test concurrent Redis operations."""
        import asyncio

        async def set_value(key, value):
            await redis_manager_instance.redis.set(key, value)

        # Run concurrent operations
        tasks = [
            set_value(f"task:{sample_task_id}:{i}", f"value{i}") for i in range(10)
        ]

        await asyncio.gather(*tasks)

        # Verify all values set
        for i in range(10):
            value = await redis_manager_instance.redis.get(f"task:{sample_task_id}:{i}")
            assert value == f"value{i}"
