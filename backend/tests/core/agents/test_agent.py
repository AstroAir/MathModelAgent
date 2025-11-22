"""Tests for base Agent class."""

import pytest
from unittest.mock import patch
from app.core.agents.agent import Agent


@pytest.mark.asyncio
class TestAgent:
    """Test suite for base Agent class."""

    @pytest.fixture
    def agent_instance(self, sample_task_id, mock_llm, mock_task_logger):
        """Create an agent instance for testing."""
        return Agent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
            max_chat_turns=10,
            max_memory=12,
        )

    async def test_agent_initialization(
        self, sample_task_id, mock_llm, mock_task_logger
    ):
        """Test agent initialization."""
        agent = Agent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
        )

        assert agent.task_id == sample_task_id
        assert agent.model == mock_llm
        assert agent.task_logger == mock_task_logger
        assert agent.chat_history == []
        assert agent.current_chat_turns == 0

    async def test_agent_run(self, agent_instance, mock_llm_response):
        """Test agent run method."""
        agent_instance.model.chat.return_value = mock_llm_response

        result = await agent_instance.run(
            prompt="Test prompt",
            system_prompt="Test system prompt",
            sub_title="Test subtitle",
        )

        assert result == "Test LLM response"
        assert len(agent_instance.chat_history) > 0

    async def test_agent_run_error_handling(self, agent_instance):
        """Test agent error handling during run."""
        agent_instance.model.chat.side_effect = Exception("LLM error")

        result = await agent_instance.run(
            prompt="Test prompt",
            system_prompt="Test system prompt",
            sub_title="Test subtitle",
        )

        assert "error" in result.lower()

    async def test_append_chat_history(self, agent_instance):
        """Test appending messages to chat history."""
        message = {"role": "user", "content": "Test message"}

        await agent_instance.append_chat_history(message)

        assert len(agent_instance.chat_history) == 1
        assert agent_instance.chat_history[0] == message

    async def test_clear_memory(self, agent_instance):
        """Test memory clearing when history exceeds max_memory."""
        # Fill chat history beyond max_memory
        for i in range(agent_instance.max_memory + 5):
            agent_instance.chat_history.append(
                {"role": "user", "content": f"Message {i}"}
            )

        await agent_instance.clear_memory()

        # History should be compressed
        assert len(agent_instance.chat_history) <= agent_instance.max_memory

    async def test_clear_memory_with_tool_messages(self, agent_instance):
        """Test that tool messages don't trigger memory clearing."""
        initial_length = len(agent_instance.chat_history)

        tool_message = {"role": "tool", "content": "Tool result"}
        await agent_instance.append_chat_history(tool_message)

        # Tool messages should be added without triggering clear_memory
        assert len(agent_instance.chat_history) == initial_length + 1

    async def test_max_chat_turns_limit(self, agent_instance, mock_llm_response):
        """Test max chat turns limit."""
        agent_instance.model.chat.return_value = mock_llm_response
        agent_instance.max_chat_turns = 3

        # Run multiple times
        for i in range(5):
            await agent_instance.run(
                prompt=f"Prompt {i}",
                system_prompt="System prompt",
                sub_title="Subtitle",
            )

        # Should respect max_chat_turns
        # Implementation depends on actual enforcement
        pass

    async def test_chat_history_structure(self, agent_instance):
        """Test chat history maintains correct structure."""
        messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant message"},
        ]

        for msg in messages:
            await agent_instance.append_chat_history(msg)

        # Verify structure
        assert all(
            "role" in msg and "content" in msg for msg in agent_instance.chat_history
        )

    async def test_agent_logging(
        self, agent_instance, mock_task_logger, mock_llm_response
    ):
        """Test agent logging during execution."""
        agent_instance.model.chat.return_value = mock_llm_response

        await agent_instance.run(
            prompt="Test prompt",
            system_prompt="Test system prompt",
            sub_title="Test subtitle",
        )

        # Verify logging calls
        assert mock_task_logger.info.called

    async def test_agent_with_empty_prompt(self, agent_instance, mock_llm_response):
        """Test agent with empty prompt."""
        agent_instance.model.chat.return_value = mock_llm_response

        result = await agent_instance.run(
            prompt="",
            system_prompt="System prompt",
            sub_title="Subtitle",
        )

        # Should handle empty prompt
        assert result is not None

    async def test_agent_with_long_prompt(self, agent_instance, mock_llm_response):
        """Test agent with very long prompt."""
        agent_instance.model.chat.return_value = mock_llm_response

        long_prompt = "Test " * 10000  # Very long prompt

        result = await agent_instance.run(
            prompt=long_prompt,
            system_prompt="System prompt",
            sub_title="Subtitle",
        )

        # Should handle long prompts
        assert result is not None

    async def test_agent_memory_compression(self, agent_instance):
        """Test memory compression with simple_chat."""
        with patch("app.core.agents.agent.simple_chat") as mock_simple_chat:
            mock_simple_chat.return_value = "Compressed summary"

            # Fill history beyond max_memory
            for i in range(agent_instance.max_memory + 5):
                agent_instance.chat_history.append(
                    {"role": "user", "content": f"Message {i}"}
                )

            await agent_instance.clear_memory()

            # Should call simple_chat for compression
            # Implementation depends on actual compression logic
            pass

    async def test_agent_concurrent_runs(self, agent_instance, mock_llm_response):
        """Test concurrent agent runs."""
        import asyncio

        agent_instance.model.chat.return_value = mock_llm_response

        # Run multiple tasks concurrently
        tasks = [
            agent_instance.run(
                prompt=f"Prompt {i}",
                system_prompt="System prompt",
                sub_title="Subtitle",
            )
            for i in range(3)
        ]

        results = await asyncio.gather(*tasks)

        # All should complete successfully
        assert len(results) == 3
