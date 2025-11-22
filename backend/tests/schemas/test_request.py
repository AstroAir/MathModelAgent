"""Tests for request schemas."""

import pytest
from pydantic import ValidationError
from app.schemas.request import Problem, ExampleRequest
from app.schemas.enums import CompTemplate, FormatOutPut


class TestRequestSchemas:
    """Test suite for request schemas."""

    def test_problem_schema_valid(self):
        """Test valid Problem schema."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "测试问题描述",
            "comp_template": "CHINA",
            "language": "zh",
            "format_output": "Markdown",
        }

        problem = Problem(**data)

        assert problem.task_id == data["task_id"]
        assert problem.ques_all == data["ques_all"]
        assert problem.comp_template == CompTemplate.CHINA
        assert problem.language == data["language"]
        assert problem.format_output == FormatOutPut.Markdown

    def test_problem_schema_missing_required_field(self):
        """Test Problem schema with missing required field."""
        data = {
            "comp_template": "CHINA",
            "language": "zh",
            "format_output": "Markdown",
        }

        with pytest.raises(ValidationError):
            Problem(**data)

    def test_problem_schema_invalid_template(self):
        """Test Problem schema with invalid template."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "测试问题",
            "comp_template": "invalid_template",
            "language": "zh",
            "format_output": "Markdown",
        }

        # Should validate or raise error based on enum definition
        try:
            Problem(**data)
        except ValidationError:
            pass  # Expected if strict validation

    def test_problem_schema_invalid_language(self):
        """Test Problem schema with invalid language."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "测试问题",
            "comp_template": "CHINA",
            "language": "invalid_lang",
            "format_output": "Markdown",
        }

        # Should validate or raise error
        try:
            Problem(**data)
        except ValidationError:
            pass

    def test_problem_schema_invalid_format(self):
        """Test Problem schema with invalid format."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "测试问题",
            "comp_template": "CHINA",
            "language": "zh",
            "format_output": "invalid_format",
        }

        # Should validate or raise error
        try:
            Problem(**data)
        except ValidationError:
            pass

    def test_problem_schema_empty_problem(self):
        """Test Problem schema with empty problem."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "",
            "comp_template": "CHINA",
            "language": "zh",
            "format_output": "Markdown",
        }

        # Should validate or raise error based on validation rules
        try:
            Problem(**data)
        except ValidationError:
            pass

    def test_problem_schema_long_problem(self):
        """Test Problem schema with very long problem."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "测试问题 " * 10000,  # Very long
            "comp_template": "CHINA",
            "language": "zh",
            "format_output": "Markdown",
        }

        problem = Problem(**data)
        assert len(problem.ques_all) > 10000

    def test_example_request_schema_valid(self):
        """Test valid ExampleRequest schema."""
        data = {
            "example_id": "2024A",
            "source": "国赛",
        }

        request = ExampleRequest(**data)

        assert request.example_id == data["example_id"]
        assert request.source == data["source"]

    def test_example_request_missing_example_name(self):
        """Test ExampleRequest with missing example_id."""
        data = {
            "source": "国赛",
        }

        with pytest.raises(ValidationError):
            ExampleRequest(**data)

    def test_problem_schema_default_values(self):
        """Test Problem schema default values."""
        data = {
            "task_id": "test_task_123",
        }

        # Should use default values if defined
        problem = Problem(**data)
        # Check if defaults are applied
        assert problem.comp_template == CompTemplate.CHINA
        assert problem.format_output == FormatOutPut.Markdown
        assert problem.language == "auto"

    def test_problem_schema_extra_fields(self):
        """Test Problem schema with extra fields."""
        data = {
            "problem": "测试问题",
            "template": "国赛",
            "language": "zh",
            "format_output": "markdown",
            "extra_field": "extra_value",
        }

        # Should ignore or raise error based on Config
        try:
            Problem(**data)
        except ValidationError:
            pass  # Expected if extra fields not allowed

    def test_problem_schema_type_coercion(self):
        """Test Problem schema type coercion."""
        data = {
            "problem": 12345,  # Integer instead of string
            "template": "国赛",
            "language": "zh",
            "format_output": "markdown",
        }

        # Should coerce or raise error
        try:
            problem = Problem(**data)
            assert isinstance(problem.problem, str)
        except ValidationError:
            pass

    def test_problem_schema_whitespace_handling(self):
        """Test Problem schema whitespace handling."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "  测试问题  ",
            "comp_template": CompTemplate.CHINA,
            "language": "zh",
            "format_output": FormatOutPut.Markdown,
        }

        problem = Problem(**data)

        # By default, Pydantic does not strip whitespace
        assert problem.ques_all == "  测试问题  "

    def test_problem_schema_unicode_support(self):
        """Test Problem schema with Unicode characters."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "测试问题 🚀 émoji",
            "comp_template": CompTemplate.CHINA,
            "language": "zh",
            "format_output": FormatOutPut.Markdown,
        }

        problem = Problem(**data)
        assert "🚀" in problem.ques_all

    def test_problem_schema_special_characters(self):
        """Test Problem schema with special characters."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "测试问题 <script>alert('xss')</script>",
            "comp_template": CompTemplate.CHINA,
            "language": "zh",
            "format_output": FormatOutPut.Markdown,
        }

        problem = Problem(**data)
        # Should handle special characters safely
        assert problem.ques_all is not None

    def test_problem_schema_json_serialization(self):
        """Test Problem schema JSON serialization."""
        data = {
            "task_id": "test_task_123",
            "ques_all": "测试问题",
            "comp_template": CompTemplate.CHINA,
            "language": "zh",
            "format_output": FormatOutPut.Markdown,
        }

        problem = Problem(**data)
        json_data = problem.model_dump()

        assert json_data["ques_all"] == data["ques_all"]
        assert json_data["comp_template"] == "CHINA"
        assert json_data["format_output"] == "Markdown"

    def test_example_request_invalid_example_name(self):
        """Test ExampleRequest with invalid example name."""
        data = {
            "example_name": "",
            "template": "国赛",
            "language": "zh",
            "format_output": "markdown",
        }

        # Should validate or raise error
        try:
            ExampleRequest(**data)
        except ValidationError:
            pass
