"""Tests for ModelerAgent."""

import pytest
from app.core.agents.modeler_agent import ModelerAgent
from app.schemas.A2A import CoordinatorToModeler, ModelerToCoder
from unittest.mock import MagicMock
import json


@pytest.mark.asyncio
class TestModelerAgent:
    """Test suite for ModelerAgent."""

    @pytest.fixture
    def modeler_agent(self, sample_task_id, mock_llm, mock_task_logger):
        """Create a ModelerAgent instance for testing."""
        agent = ModelerAgent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
        )
        return agent

    async def test_modeler_agent_initialization(
        self, sample_task_id, mock_llm, mock_task_logger
    ):
        """Test ModelerAgent initialization."""
        agent = ModelerAgent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
        )

        assert agent.task_id == sample_task_id
        assert agent.model == mock_llm
        assert agent.task_logger == mock_task_logger

    async def test_modeler_agent_run(self, modeler_agent):
        """Test ModelerAgent run method."""
        # Mock response with JSON content
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "问题1": {"分析": "这是分析", "方案": "这是方案"},
            }
        )
        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(questions={"问题1": "描述"}, ques_count=1)
        result = await modeler_agent.run(input_data)

        assert result is not None
        assert isinstance(result, ModelerToCoder)
        assert "问题1" in result.questions_solution

    async def test_problem_analysis(self, modeler_agent):
        """Test problem analysis capability."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "公交优化问题": {
                    "分析": "这是一个典型的运筹优化问题",
                    "模型": "整数规划模型",
                    "方法": "启发式算法",
                }
            }
        )
        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(
            questions={"公交优化问题": "某城市需要优化公交线路"},
            ques_count=1,
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)
        assert "公交优化问题" in result.questions_solution

    async def test_model_formulation(self, modeler_agent):
        """Test mathematical model formulation."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "数学模型": {
                    "目标函数": "min Z = Σ c_ij * x_ij",
                    "约束条件": "Σ x_ij = 1",
                    "变量类型": "x_ij ∈ {0, 1}",
                }
            }
        )

        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(
            questions={"数学模型": "构建优化模型"}, ques_count=1
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)
        assert "数学模型" in result.questions_solution

    async def test_solution_approach(self, modeler_agent):
        """Test solution approach recommendation."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "求解方案": {
                    "方法1": "线性规划",
                    "方法2": "单纯形法",
                    "验证": "最优解检验",
                }
            }
        )
        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(
            questions={"求解方案": "推荐求解方法"}, ques_count=1
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)

    async def test_model_validation(self, modeler_agent):
        """Test model validation."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {"模型验证": {"假设检验": "合理", "结果": "有效"}}
        )
        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(
            questions={"模型验证": "验证模型假设"}, ques_count=1
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)

    async def test_sensitivity_analysis(self, modeler_agent):
        """Test sensitivity analysis."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {"敏感性分析": {"参数影响": "显著", "稳健性": "良好"}}
        )
        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(
            questions={"敏感性分析": "执行敏感性分析"}, ques_count=1
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)

    async def test_chinese_problem(self, modeler_agent):
        """Test handling Chinese problem description."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {"工厂生产问题": {"目标": "最大利润", "方法": "线性规划"}}
        )
        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(
            questions={"工厂生产问题": "某工厂生产两种产品，求最大利润"},
            ques_count=1,
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)

    async def test_english_problem(self, modeler_agent):
        """Test handling English problem description."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {"factory_problem": {"objective": "maximize profit", "method": "LP"}}
        )
        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(
            questions={
                "factory_problem": "A factory produces two products. Maximize profit."
            },
            ques_count=1,
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)

    async def test_complex_problem(self, modeler_agent):
        """Test handling complex multi-objective problem."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "多目标优化": {
                    "目标1": "最小化成本",
                    "目标2": "最大化效率",
                    "约束": "环保要求",
                }
            }
        )
        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(
            questions={"多目标优化": "多目标优化问题"}, ques_count=1
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)

    async def test_error_handling(self, modeler_agent):
        """Test error handling in ModelerAgent."""
        modeler_agent.model.chat.side_effect = Exception("LLM error")

        input_data = CoordinatorToModeler(questions={"测试": "测试提示"}, ques_count=1)

        with pytest.raises(Exception, match="LLM error"):
            await modeler_agent.run(input_data)

    async def test_long_problem_description(self, modeler_agent):
        """Test handling very long problem description."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {"长问题": {"分析": "已处理"}}
        )
        modeler_agent.model.chat.return_value = mock_response

        long_problem = "问题描述 " * 100
        input_data = CoordinatorToModeler(
            questions={"长问题": long_problem}, ques_count=1
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)

    async def test_iterative_refinement(self, modeler_agent):
        """Test iterative model refinement."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {"迭代改进": {"版本": "1", "改进": "已完成"}}
        )
        modeler_agent.model.chat.return_value = mock_response

        # First iteration
        input1 = CoordinatorToModeler(questions={"初始模型": "创建模型"}, ques_count=1)
        result1 = await modeler_agent.run(input1)

        # Refinement
        input2 = CoordinatorToModeler(questions={"改进模型": "改进模型"}, ques_count=1)
        result2 = await modeler_agent.run(input2)

        assert isinstance(result1, ModelerToCoder)
        assert isinstance(result2, ModelerToCoder)

    async def test_model_comparison(self, modeler_agent):
        """Test comparing different modeling approaches."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "方案比较": {
                    "线性规划": "简单但可能不够精确",
                    "非线性规划": "更精确但计算复杂",
                    "启发式算法": "快速但不保证最优",
                }
            }
        )
        modeler_agent.model.chat.return_value = mock_response

        input_data = CoordinatorToModeler(
            questions={"方案比较": "比较建模方法"}, ques_count=1
        )
        result = await modeler_agent.run(input_data)

        assert isinstance(result, ModelerToCoder)
