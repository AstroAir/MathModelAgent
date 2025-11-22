"""Tests for local Jupyter interpreter."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.tools.local_interpreter import LocalCodeInterpreter
from app.tools.notebook_serializer import NotebookSerializer
import os


@pytest.mark.asyncio
class TestLocalInterpreter:
    """Test suite for LocalCodeInterpreter."""

    @pytest.fixture
    async def interpreter(self, sample_task_id, temp_work_dir):
        """Create LocalCodeInterpreter instance."""
        with patch("jupyter_client.manager.start_new_kernel") as mock_kernel:
            mock_km = MagicMock()
            mock_kc = MagicMock()
            mock_kernel.return_value = (mock_km, mock_kc)

            notebook_serializer = NotebookSerializer(work_dir=temp_work_dir)
            interpreter = LocalCodeInterpreter(
                task_id=sample_task_id,
                work_dir=temp_work_dir,
                notebook_serializer=notebook_serializer,
            )
            interpreter.km = mock_km
            interpreter.kc = mock_kc
            return interpreter

    async def test_interpreter_initialization(self, sample_task_id, temp_work_dir):
        """Test interpreter initialization."""
        with patch("jupyter_client.manager.start_new_kernel"):
            notebook_serializer = NotebookSerializer(work_dir=temp_work_dir)
            interpreter = LocalCodeInterpreter(
                task_id=sample_task_id,
                work_dir=temp_work_dir,
                notebook_serializer=notebook_serializer,
            )

            assert interpreter.task_id == sample_task_id
            assert interpreter.work_dir == temp_work_dir

    async def test_execute_code_success(self, interpreter):
        """Test successful code execution."""
        code = "print('Hello, World!')"

        # Mock kernel client behavior
        interpreter.kc.execute.return_value = "msg_id"
        interpreter.kc.get_iopub_msg.side_effect = [
            {
                "msg_type": "stream",
                "content": {"name": "stdout", "text": "Hello, World!\n"},
            },
            {"msg_type": "status", "content": {"execution_state": "idle"}},
        ]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            result = await interpreter.execute_code(code)

        # Should return success result
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert "Hello, World!" in result[0]
        assert result[1] is False  # no error

    async def test_execute_code_error(self, interpreter):
        """Test code execution with error."""
        code = "print('Hello"  # Syntax error

        interpreter.kc.execute.return_value = "msg_id"
        interpreter.kc.get_iopub_msg.side_effect = [
            {
                "msg_type": "error",
                "content": {
                    "ename": "SyntaxError",
                    "evalue": "invalid syntax",
                    "traceback": ["Traceback..."],
                },
            },
            {"msg_type": "status", "content": {"execution_state": "idle"}},
        ]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            result = await interpreter.execute_code(code)

        # Should return error result
        assert result[1] is True  # error occurred

    async def test_execute_code_with_output(self, interpreter):
        """Test code execution with output."""
        code = "x = 10\nprint(x)"

        interpreter.kc.execute.return_value = "msg_id"
        interpreter.kc.get_iopub_msg.side_effect = [
            {"msg_type": "execute_input", "content": {}},
            {"msg_type": "stream", "content": {"name": "stdout", "text": "10\n"}},
            {"msg_type": "status", "content": {"execution_state": "idle"}},
        ]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            result = await interpreter.execute_code(code)

        # Should capture output
        assert "10" in result[0]

    async def test_execute_code_with_plots(self, interpreter, temp_work_dir):
        """Test code execution that generates plots."""
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.savefig('plot.png')
"""

        interpreter.kc.execute.return_value = "msg_id"
        interpreter.kc.get_iopub_msg.side_effect = [
            {
                "msg_type": "display_data",
                "content": {"data": {"image/png": "base64_image_data"}},
            },
            {"msg_type": "status", "content": {"execution_state": "idle"}},
        ]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            result = await interpreter.execute_code(code)

        # Should handle plot generation
        assert "图片已生成" in result[0]

    async def test_execute_code_timeout(self, interpreter):
        """Test code execution timeout."""
        code = "import time\ntime.sleep(1000)"

        interpreter.kc.execute.return_value = "msg_id"
        import queue

        interpreter.kc.get_iopub_msg.side_effect = queue.Empty

        # Should handle timeout - the execute_code handles queue.Empty internally
        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            # Set a short max_wait_time for testing - we'll mock this
            with patch.object(interpreter, "interrupt_signal", True):
                result = await interpreter.execute_code(code)

        # Should complete without raising exception
        assert isinstance(result, tuple)

    async def test_execute_multiple_cells(self, interpreter):
        """Test executing multiple code cells."""
        codes = [
            "x = 10",
            "y = 20",
            "print(x + y)",
        ]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            for code in codes:
                interpreter.kc.execute.return_value = "msg_id"
                interpreter.kc.get_iopub_msg.side_effect = [
                    {
                        "msg_type": "stream",
                        "content": {"name": "stdout", "text": "30\n"},
                    },
                    {"msg_type": "status", "content": {"execution_state": "idle"}},
                ]

                result = await interpreter.execute_code(code)
                # Each cell should execute
                assert isinstance(result, tuple)

    def test_kernel_restart(self, interpreter):
        """Test kernel restart."""
        with patch("jupyter_client.manager.start_new_kernel") as mock_kernel:
            mock_km = MagicMock()
            mock_kc = MagicMock()
            mock_kc.shutdown = MagicMock()
            mock_kernel.return_value = (mock_km, mock_kc)

            interpreter.restart_jupyter_kernel()

            # Verify the kernel was restarted
            mock_kernel.assert_called_once_with(kernel_name="python3")
            assert interpreter.interrupt_signal is False

    async def test_close_interpreter(self, interpreter):
        """Test closing interpreter."""
        await interpreter.cleanup()

        # Should cleanup resources
        interpreter.kc.shutdown.assert_called()
        interpreter.km.shutdown_kernel.assert_called()

    async def test_execute_code_with_imports(self, interpreter):
        """Test code with various imports."""
        code = """
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

print("All imports successful")
"""

        interpreter.kc.execute.return_value = "msg_id"
        interpreter.kc.get_iopub_msg.side_effect = [
            {
                "msg_type": "stream",
                "content": {"name": "stdout", "text": "All imports successful\n"},
            },
            {"msg_type": "status", "content": {"execution_state": "idle"}},
        ]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            result = await interpreter.execute_code(code)

        # Should handle imports
        assert "All imports successful" in result[0]

    async def test_execute_code_with_data_files(self, interpreter, temp_work_dir):
        """Test code execution with data files."""
        # Create test data file
        data_file = os.path.join(temp_work_dir, "data.csv")
        with open(data_file, "w") as f:
            f.write("col1,col2\n1,2\n3,4")

        code = """
import pandas as pd
df = pd.read_csv('data.csv')
print(df.head())
"""

        interpreter.kc.execute.return_value = "msg_id"
        interpreter.kc.get_iopub_msg.side_effect = [
            {
                "msg_type": "stream",
                "content": {"name": "stdout", "text": "DataFrame output\n"},
            },
            {"msg_type": "status", "content": {"execution_state": "idle"}},
        ]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            result = await interpreter.execute_code(code)

        # Should access data files
        assert "DataFrame output" in result[0]

    async def test_execute_code_memory_usage(self, interpreter):
        """Test code execution memory usage."""
        code = """
import numpy as np
large_array = np.zeros((1000, 1000))
print("Array created")
"""

        interpreter.kc.execute.return_value = "msg_id"
        interpreter.kc.get_iopub_msg.side_effect = [
            {
                "msg_type": "stream",
                "content": {"name": "stdout", "text": "Array created\n"},
            },
            {"msg_type": "status", "content": {"execution_state": "idle"}},
        ]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            result = await interpreter.execute_code(code)

        # Should handle memory allocation
        assert "Array created" in result[0]

    async def test_execute_code_exception_handling(self, interpreter):
        """Test exception handling in code execution."""
        code = """
try:
    x = 1 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
"""

        interpreter.kc.execute.return_value = "msg_id"
        interpreter.kc.get_iopub_msg.side_effect = [
            {
                "msg_type": "stream",
                "content": {"name": "stdout", "text": "Error: division by zero\n"},
            },
            {"msg_type": "status", "content": {"execution_state": "idle"}},
        ]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            result = await interpreter.execute_code(code)

        # Should handle exceptions
        assert "division by zero" in result[0]

    async def test_notebook_serialization(self, interpreter, temp_work_dir):
        """Test notebook serialization."""
        # Execute some code
        codes = ["x = 10", "y = 20", "print(x + y)"]

        with patch(
            "app.services.redis_manager.redis_manager.publish_message",
            new_callable=AsyncMock,
        ):
            for code in codes:
                interpreter.kc.execute.return_value = "msg_id"
                interpreter.kc.get_iopub_msg.side_effect = [
                    {
                        "msg_type": "stream",
                        "content": {"name": "stdout", "text": "30\n"},
                    },
                    {"msg_type": "status", "content": {"execution_state": "idle"}},
                ]
                await interpreter.execute_code(code)

        # Should save as notebook - notebook serializer is tested separately
        assert interpreter.notebook_serializer is not None

    async def test_concurrent_execution(self, interpreter):
        """Test concurrent code execution."""
        # Should handle or prevent concurrent execution
        pass
