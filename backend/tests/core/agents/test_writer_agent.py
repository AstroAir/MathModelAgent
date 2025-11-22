"""Tests for WriterAgent."""

import pytest
from app.core.agents.writer_agent import WriterAgent
from app.schemas.A2A import WriterResponse


@pytest.mark.asyncio
class TestWriterAgent:
    """Test suite for WriterAgent."""

    @pytest.fixture
    def writer_agent(self, sample_task_id, mock_llm, mock_task_logger):
        """Create a WriterAgent instance for testing."""
        agent = WriterAgent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
        )
        return agent

    async def test_writer_agent_initialization(
        self, sample_task_id, mock_llm, mock_task_logger
    ):
        """Test WriterAgent initialization."""
        agent = WriterAgent(
            task_id=sample_task_id,
            model=mock_llm,
            task_logger=mock_task_logger,
        )

        assert agent.task_id == sample_task_id
        assert hasattr(agent, "language")
        assert hasattr(agent, "system_prompt")

    async def test_writer_agent_run(self, writer_agent, mock_llm_response):
        """Test WriterAgent run method."""
        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write introduction section",
            sub_title="Introduction",
        )

        assert isinstance(result, WriterResponse)
        assert result.response_content is not None

    async def test_write_introduction(self, writer_agent, mock_llm_response):
        """Test writing introduction section."""
        mock_llm_response.choices[0].message.content = """
        # 摘要

        本文研究了城市公交线路优化问题，建立了整数规划模型，
        并使用启发式算法求解，得到了满意的结果。
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write introduction",
            sub_title="Introduction",
        )

        content = result.response_content
        assert "摘要" in content or "introduction" in content.lower()

    async def test_write_methodology(self, writer_agent, mock_llm_response):
        """Test writing methodology section."""
        mock_llm_response.choices[0].message.content = """
        ## 模型建立

        ### 问题分析
        本问题可以抽象为...

        ### 数学模型
        目标函数：min Z = ...
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write methodology",
            sub_title="Methodology",
        )

        assert isinstance(result, WriterResponse)
        assert result.response_content is not None

    async def test_write_results(self, writer_agent, mock_llm_response):
        """Test writing results section."""
        mock_llm_response.choices[0].message.content = """
        ## 结果分析

        通过求解得到最优解为...
        结果表明该方案可以降低成本20%。
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write results",
            sub_title="Results",
        )

        assert isinstance(result, WriterResponse)
        assert result.response_content is not None

    async def test_write_conclusion(self, writer_agent, mock_llm_response):
        """Test writing conclusion section."""
        mock_llm_response.choices[0].message.content = """
        ## 结论

        本文建立了有效的优化模型，求解结果合理，
        为实际应用提供了参考。
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write conclusion",
            sub_title="Conclusion",
        )

        assert isinstance(result, WriterResponse)
        assert result.response_content is not None

    async def test_markdown_formatting(self, writer_agent, mock_llm_response):
        """Test Markdown formatting."""
        mock_llm_response.choices[0].message.content = """
        # 标题

        ## 二级标题

        - 列表项 1
        - 列表项 2

        **粗体文本**

        ```python
        code_block = True
        ```
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write with formatting",
            sub_title="Formatting",
        )

        content = result.response_content
        assert "#" in content or "**" in content

    async def test_latex_formatting(self, writer_agent, mock_llm_response):
        """Test LaTeX formatting."""
        mock_llm_response.choices[0].message.content = r"""
        \section{Introduction}

        The objective function is:
        \begin{equation}
        \min Z = \sum_{i=1}^{n} c_i x_i
        \end{equation}
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write with LaTeX",
            sub_title="LaTeX",
        )

        assert isinstance(result, WriterResponse)
        assert result.response_content is not None

    async def test_include_figures(
        self, writer_agent, mock_llm_response, temp_work_dir
    ):
        """Test including figures in paper."""
        import os

        # Create dummy figure
        fig_path = os.path.join(temp_work_dir, "figure1.png")
        with open(fig_path, "wb") as f:
            f.write(b"fake image data")

        mock_llm_response.choices[0].message.content = """
        ![Figure 1](figure1.png)

        图1显示了优化结果。
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Include figures",
            sub_title="Figures",
        )

        content = result.response_content
        assert "figure" in content.lower() or "图" in content

    async def test_include_tables(self, writer_agent, mock_llm_response):
        """Test including tables in paper."""
        mock_llm_response.choices[0].message.content = """
        | 参数 | 值 |
        |------|-----|
        | α    | 0.5 |
        | β    | 0.3 |
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Include tables",
            sub_title="Tables",
        )

        assert "|" in result.response_content

    async def test_citations(self, writer_agent, mock_llm_response):
        """Test adding citations."""
        mock_llm_response.choices[0].message.content = """
        根据文献[1]的研究，该方法已被证明有效。

        ## 参考文献
        [1] Zhang et al. (2023). Optimization Methods.
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Add citations",
            sub_title="Citations",
        )

        content = result.response_content
        assert "[1]" in content or "参考" in content

    async def test_chinese_paper(self, writer_agent, mock_llm_response):
        """Test writing Chinese paper."""
        mock_llm_response.choices[0].message.content = """
        # 数学建模论文

        ## 摘要
        本文研究了...
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write Chinese paper",
            sub_title="中文论文",
        )

        # Should contain Chinese characters
        content = result.response_content
        assert any("\u4e00" <= char <= "\u9fff" for char in content)

    async def test_english_paper(self, writer_agent, mock_llm_response):
        """Test writing English paper."""
        mock_llm_response.choices[0].message.content = """
        # Mathematical Modeling Paper

        ## Abstract
        This paper investigates...
        """

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write English paper",
            sub_title="English Paper",
        )

        assert isinstance(result, WriterResponse)
        assert result.response_content is not None

    async def test_section_by_section_writing(self, writer_agent, mock_llm_response):
        """Test writing paper section by section."""
        sections = [
            "Introduction",
            "Methodology",
            "Results",
            "Conclusion",
        ]

        writer_agent.model.chat.return_value = mock_llm_response

        for section in sections:
            result = await writer_agent.run(
                prompt=f"Write {section}",
                sub_title=section,
            )
            assert isinstance(result, WriterResponse)
            assert result.response_content is not None

    async def test_error_handling(self, writer_agent):
        """Test error handling in WriterAgent."""
        writer_agent.model.chat.side_effect = Exception("LLM error")

        with pytest.raises(Exception, match="LLM error"):
            await writer_agent.run(
                prompt="Write section",
                sub_title="Section",
            )

    async def test_long_content_generation(self, writer_agent, mock_llm_response):
        """Test generating long content."""
        mock_llm_response.choices[0].message.content = "Long content " * 1000

        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Write long paper",
            sub_title="Long Paper",
        )

        assert len(result.response_content) > 1000

    async def test_template_usage(self, writer_agent, mock_llm_response):
        """Test using paper templates."""
        # Test with different templates (国赛, 美赛)
        writer_agent.model.chat.return_value = mock_llm_response

        result = await writer_agent.run(
            prompt="Use template",
            sub_title="Template",
        )

        assert isinstance(result, WriterResponse)
        assert result.response_content is not None
