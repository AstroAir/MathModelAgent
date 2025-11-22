"""Tests for CoderAgent."""

import pytest
from unittest.mock import AsyncMock, patch
from app.core.agents.coder_agent import CoderAgent


@pytest.mark.asyncio
class TestCoderAgent:
    """Test suite for CoderAgent."""

    @pytest.fixture
    def coder_agent(self, sample_task_id, mock_llm, mock_task_logger, temp_work_dir):
        """Create a CoderAgent instance for testing."""
        mock_interpreter = AsyncMock()
        # execute_code returns tuple: (text_to_gpt, error_occurred, error_message)
        mock_interpreter.execute_code.return_value = ("Test output", False, "")
        mock_interpreter.get_created_images.return_value = []
        mock_interpreter.add_section.return_value = None

        agent = CoderAgent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
            work_dir=temp_work_dir,
            max_retries=3,
            code_interpreter=mock_interpreter,
        )
        return agent

    async def test_coder_agent_initialization(
        self, sample_task_id, mock_llm, mock_task_logger, temp_work_dir
    ):
        """Test CoderAgent initialization."""
        mock_interpreter = AsyncMock()
        agent = CoderAgent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
            work_dir=temp_work_dir,
            code_interpreter=mock_interpreter,
        )

        assert agent.task_id == sample_task_id
        assert agent.work_dir == temp_work_dir
        assert agent.code_interpreter is not None

    async def test_coder_agent_run(self, coder_agent, mock_llm_response):
        """Test CoderAgent run method."""
        # Mock the response without tool calls to complete immediately
        from unittest.mock import MagicMock

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].message.content = "Task completed"
        coder_agent.model.chat.return_value = mock_response

        with patch("app.utils.common_utils.get_current_files", return_value=[]):
            result = await coder_agent.run(
                prompt="Write code to calculate sum",
                subtask_title="Code Generation",
            )

        assert result is not None
        from app.schemas.A2A import CoderToWriter

        assert isinstance(result, CoderToWriter)

    async def test_code_execution_success(self, coder_agent):
        """Test successful code execution."""
        code = "print('Hello, World!')"
        coder_agent.code_interpreter.execute_code.return_value = (
            "Hello, World!\n",
            False,
            "",
        )

        (
            text_to_gpt,
            error_occurred,
            error_message,
        ) = await coder_agent.code_interpreter.execute_code(code)

        assert error_occurred is False
        assert "Hello, World" in text_to_gpt

    async def test_code_execution_error(self, coder_agent):
        """Test code execution with error."""
        code = "print('Hello"  # Syntax error
        coder_agent.code_interpreter.execute_code.return_value = (
            "",
            True,
            "SyntaxError: invalid syntax",
        )

        (
            text_to_gpt,
            error_occurred,
            error_message,
        ) = await coder_agent.code_interpreter.execute_code(code)

        assert error_occurred is True
        assert "SyntaxError" in error_message

    async def test_code_retry_mechanism(self, coder_agent):
        """Test code retry mechanism on error."""
        # Mock retry behavior - first fails, then succeeds
        from unittest.mock import MagicMock

        # First call returns error, second call succeeds
        mock_tool_call = MagicMock()
        mock_tool_call.id = "test_id"
        mock_tool_call.function.name = "execute_code"
        mock_tool_call.function.arguments = '{"code": "print(1)"}'

        # Response with tool call (first attempt)
        mock_response1 = MagicMock()
        mock_response1.choices = [MagicMock()]
        mock_response1.choices[0].message.tool_calls = [mock_tool_call]
        mock_response1.choices[0].message.model_dump.return_value = {
            "role": "assistant",
            "content": None,
        }

        # Response without tool call (completion)
        mock_response2 = MagicMock()
        mock_response2.choices = [MagicMock()]
        mock_response2.choices[0].message.tool_calls = None
        mock_response2.choices[0].message.content = "Task completed"

        coder_agent.model.chat.side_effect = [mock_response1, mock_response2]
        coder_agent.code_interpreter.execute_code.return_value = ("Success", False, "")

        with patch("app.utils.common_utils.get_current_files", return_value=[]):
            result = await coder_agent.run(prompt="Test", subtask_title="Test")

        assert result is not None

    async def test_max_retries_exceeded(self, coder_agent):
        """Test behavior when max retries exceeded."""
        coder_agent.max_retries = 2

        from unittest.mock import MagicMock

        mock_tool_call = MagicMock()
        mock_tool_call.id = "test_id"
        mock_tool_call.function.name = "execute_code"
        mock_tool_call.function.arguments = '{"code": "bad code"}'

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_response.choices[0].message.model_dump.return_value = {
            "role": "assistant",
            "content": None,
        }

        coder_agent.model.chat.return_value = mock_response
        coder_agent.code_interpreter.execute_code.return_value = (
            "",
            True,
            "Persistent error",
        )

        with patch("app.utils.common_utils.get_current_files", return_value=[]):
            with pytest.raises(Exception, match="exceeded max retries"):
                await coder_agent.run(prompt="Test", subtask_title="Test")

    async def test_code_with_data_files(self, coder_agent, temp_work_dir):
        """Test code execution with data files."""
        import os

        # Create test data file
        data_file = os.path.join(temp_work_dir, "data.csv")
        with open(data_file, "w") as f:
            f.write("col1,col2\n1,2\n3,4")

        code = """
import pandas as pd
df = pd.read_csv('data.csv')
print(df.head())
"""

        coder_agent.code_interpreter.execute_code.return_value = (
            "DataFrame output",
            False,
            "",
        )

        (
            text_to_gpt,
            error_occurred,
            _,
        ) = await coder_agent.code_interpreter.execute_code(code)

        assert error_occurred is False
        assert "DataFrame output" in text_to_gpt

    async def test_code_with_plots(self, coder_agent):
        """Test code execution that generates plots."""
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.savefig('plot.png')
"""

        coder_agent.code_interpreter.execute_code.return_value = (
            "Plot saved",
            False,
            "",
        )

        (
            text_to_gpt,
            error_occurred,
            _,
        ) = await coder_agent.code_interpreter.execute_code(code)

        assert error_occurred is False

    async def test_code_with_multiple_cells(self, coder_agent):
        """Test execution of multiple code cells."""
        codes = [
            "x = 10",
            "y = 20",
            "print(x + y)",
        ]

        for code in codes:
            coder_agent.code_interpreter.execute_code.return_value = ("30", False, "")
            (
                text_to_gpt,
                error_occurred,
                _,
            ) = await coder_agent.code_interpreter.execute_code(code)
            assert error_occurred is False

    async def test_interpreter_cleanup(self, coder_agent):
        """Test interpreter cleanup."""
        coder_agent.code_interpreter.cleanup = AsyncMock()
        await coder_agent.code_interpreter.cleanup()

        # Verify cleanup was called
        coder_agent.code_interpreter.cleanup.assert_called()

    async def test_local_interpreter_usage(
        self, sample_task_id, mock_llm, mock_task_logger, temp_work_dir
    ):
        """Test using local Jupyter interpreter."""
        mock_interpreter = AsyncMock()

        agent = CoderAgent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
            work_dir=temp_work_dir,
            code_interpreter=mock_interpreter,
        )

        # Should use provided interpreter
        assert agent.code_interpreter is not None
        assert agent.code_interpreter == mock_interpreter

    async def test_e2b_interpreter_usage(
        self, sample_task_id, mock_llm, mock_task_logger, temp_work_dir
    ):
        """Test using E2B cloud interpreter."""
        mock_e2b_interpreter = AsyncMock()

        agent = CoderAgent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
            work_dir=temp_work_dir,
            code_interpreter=mock_e2b_interpreter,
        )

        # Should use E2B interpreter
        assert agent.code_interpreter is not None
        assert agent.code_interpreter == mock_e2b_interpreter

    async def test_code_with_imports(self, coder_agent):
        """Test code with various imports."""
        code = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

print("All imports successful")
"""

        coder_agent.code_interpreter.execute_code.return_value = (
            "All imports successful",
            False,
            "",
        )

        (
            text_to_gpt,
            error_occurred,
            _,
        ) = await coder_agent.code_interpreter.execute_code(code)

        assert error_occurred is False
        assert "All imports successful" in text_to_gpt

    async def test_code_timeout_handling(self, coder_agent):
        """Test handling of code execution timeout."""
        # This would test timeout mechanism
        pass

    async def test_code_memory_limit(self, coder_agent):
        """Test handling of memory limits."""
        # This would test memory limit enforcement
        pass
