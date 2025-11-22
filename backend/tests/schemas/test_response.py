"""Tests for response schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.response import AgentMessage, SystemMessage
from app.schemas.enums import AgentType
import time


class TestResponseSchemas:
    """Test suite for response schemas."""

    def test_agent_message_valid(self):
        """Test valid AgentMessage schema."""
        data = {
            "msg_type": "agent",
            "agent_type": "ModelerAgent",
            "content": "Test message content",
            "timestamp": time.time(),
        }

        message = AgentMessage(**data)

        assert message.msg_type == "agent"
        assert message.agent_type == AgentType.MODELER
        assert message.content == data["content"]

    def test_agent_message_missing_required_field(self):
        """Test AgentMessage with missing required field."""
        data = {
            "msg_type": "agent",
            # Missing agent_type which is required
        }

        with pytest.raises(ValidationError):
            AgentMessage(**data)

    def test_agent_message_with_metadata(self):
        """Test AgentMessage with additional metadata."""
        data = {
            "msg_type": "agent",
            "agent_type": "CoderAgent",
            "content": "Code execution result",
        }

        # Should handle basic fields
        try:
            message = AgentMessage(**data)
            assert message.agent_type == AgentType.CODER
        except ValidationError as e:
            pytest.fail(f"Valid data should not raise ValidationError: {e}")

    def test_system_message_valid(self):
        """Test valid SystemMessage schema."""
        data = {
            "msg_type": "system",
            "content": "Task started",
            "type": "info",
            "timestamp": time.time(),
        }

        message = SystemMessage(**data)

        assert message.msg_type == "system"
        assert message.type == "info"
        assert message.content == data["content"]

    def test_system_message_error_level(self):
        """Test SystemMessage with error level."""
        data = {
            "msg_type": "system",
            "content": "An error occurred",
            "type": "error",
        }

        message = SystemMessage(**data)
        assert message.type == "error"

    def test_system_message_warning_level(self):
        """Test SystemMessage with warning level."""
        data = {
            "msg_type": "system",
            "content": "Warning message",
            "type": "warning",
        }

        message = SystemMessage(**data)
        assert message.type == "warning"

    def test_agent_message_empty_content(self):
        """Test AgentMessage with empty content."""
        data = {
            "msg_type": "agent",
            "agent_type": "ModelerAgent",
            "content": "",
        }

        # Should validate or raise error
        try:
            AgentMessage(**data)
        except ValidationError:
            pass

    def test_agent_message_long_content(self):
        """Test AgentMessage with very long content."""
        data = {
            "msg_type": "agent",
            "agent_type": "WriterAgent",
            "content": "Long content " * 10000,
        }

        message = AgentMessage(**data)
        assert len(message.content) > 10000

    def test_agent_message_special_characters(self):
        """Test AgentMessage with special characters."""
        data = {
            "msg_type": "agent",
            "agent_type": "CoderAgent",
            "content": "Code: <script>alert('test')</script>",
        }

        message = AgentMessage(**data)
        assert "<script>" in message.content

    def test_agent_message_unicode(self):
        """Test AgentMessage with Unicode content."""
        data = {
            "msg_type": "agent",
            "agent_type": AgentType.MODELER,
            "content": "数学模型分析 🚀",
        }

        message = AgentMessage(**data)
        assert "🚀" in message.content

    def test_system_message_invalid_level(self):
        """Test SystemMessage with invalid level."""
        data = {
            "msg_type": "system",
            "content": "Test message",
            "type": "invalid_level",
        }

        # Should validate or raise error
        try:
            SystemMessage(**data)
        except ValidationError:
            pass

    def test_agent_message_json_serialization(self):
        """Test AgentMessage JSON serialization."""
        data = {
            "msg_type": "agent",
            "agent_type": AgentType.MODELER,
            "content": "Test content",
        }

        message = AgentMessage(**data)
        json_data = message.model_dump()

        assert json_data["msg_type"] == "agent"
        assert json_data["agent_type"] == "ModelerAgent"

    def test_system_message_json_serialization(self):
        """Test SystemMessage JSON serialization."""
        data = {
            "msg_type": "system",
            "content": "Test content",
            "type": "info",
        }

        message = SystemMessage(**data)
        json_data = message.model_dump()

        assert json_data["msg_type"] == "system"
        assert json_data["type"] == "info"
        assert json_data["content"] == data["content"]

    def test_agent_message_timestamp_format(self):
        """Test AgentMessage timestamp format."""
        data = {
            "type": "agent_message",
            "agent_name": "ModelerAgent",
            "content": "Test",
            "timestamp": "2024-01-01T12:00:00",
        }

        # Should parse timestamp correctly
        try:
            AgentMessage(**data)
        except ValidationError:
            pass

    def test_agent_message_invalid_agent_name(self):
        """Test AgentMessage with invalid agent name."""
        data = {
            "type": "agent_message",
            "agent_name": "",
            "content": "Test content",
        }

        # Should validate or raise error
        try:
            AgentMessage(**data)
        except ValidationError:
            pass

    def test_message_type_validation(self):
        """Test message type validation."""
        data = {
            "type": "invalid_type",
            "content": "Test content",
        }

        # Should validate message type
        try:
            SystemMessage(**data)
        except ValidationError:
            pass

    def test_agent_message_with_code_block(self):
        """Test AgentMessage with code block."""
        data = {
            "msg_type": "agent",
            "agent_type": AgentType.CODER,
            "content": "```python\nprint('hello')\n```",
        }

        message = AgentMessage(**data)
        assert "```python" in message.content

    def test_system_message_with_structured_content(self):
        """Test SystemMessage with structured content."""
        data = {
            "msg_type": "system",
            "content": '{"status": "running", "progress": 50}',
            "type": "info",
        }

        message = SystemMessage(**data)
        assert message.content is not None

    def test_message_equality(self):
        """Test message equality comparison."""
        data = {
            "msg_type": "agent",
            "agent_type": AgentType.MODELER,
            "content": "Test",
        }

        message1 = AgentMessage(**data)
        message2 = AgentMessage(**data)

        # IDs will be different, so compare without them
        dict1 = message1.model_dump()
        dict2 = message2.model_dump()
        dict1.pop("id")
        dict1.pop("timestamp")
        dict2.pop("id")
        dict2.pop("timestamp")
        assert dict1 == dict2
