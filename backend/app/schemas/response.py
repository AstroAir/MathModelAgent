from typing import Literal, Union
from app.schemas.enums import AgentType
from pydantic import BaseModel, Field
from uuid import uuid4


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    msg_type: Literal[
        "system", "agent", "user", "tool", "step"
    ]  # system msg | agent message | user message | tool message | step message
    content: str | None = None
    timestamp: float = Field(default_factory=lambda: __import__('time').time())


class ToolMessage(Message):
    msg_type: str = "tool"
    tool_name: Literal["execute_code", "search_scholar"]
    input: dict
    output: list


class SystemMessage(Message):
    msg_type: str = "system"
    type: Literal["info", "warning", "success", "error"] = "info"


class StepMessage(Message):
    """Agent执行步骤消息，用于调试模式下追踪执行流程"""
    msg_type: str = "step"
    step_name: str  # 步骤名称，如"代码手求解成功ques5"
    step_type: Literal["agent", "tool", "task", "processing"]  # 步骤类型
    status: Literal["processing", "completed", "failed"] = "processing"  # 步骤状态
    agent_type: str | None = None  # 关联的agent类型
    details: dict | None = None  # 额外的步骤详情


class UserMessage(Message):
    msg_type: str = "user"


class AgentMessage(Message):
    msg_type: str = "agent"
    agent_type: AgentType  # CoordinatorAgent | ModelerAgent | CoderAgent | WriterAgent


class ModelerMessage(AgentMessage):
    agent_type: AgentType = AgentType.MODELER


class CoordinatorMessage(AgentMessage):
    agent_type: AgentType = AgentType.COORDINATOR


class CodeExecution(BaseModel):
    res_type: Literal["stdout", "stderr", "result", "error"]
    msg: str | None = None


class StdOutModel(CodeExecution):
    res_type: str = "stdout"


class StdErrModel(CodeExecution):
    res_type: str = "stderr"


class ResultModel(CodeExecution):
    res_type: str = "result"
    format: Literal[
        "text",
        "html",
        "markdown",
        "png",
        "jpeg",
        "svg",
        "pdf",
        "latex",
        "json",
        "javascript",
    ]


class ErrorModel(CodeExecution):
    res_type: str = "error"
    name: str
    value: str
    traceback: str


# 代码执行结果类型
OutputItem = Union[StdOutModel, StdErrModel, ResultModel, ErrorModel]


class ScholarMessage(ToolMessage):
    tool_name: str = "search_scholar"
    input: dict | None = None  # query
    output: list[str] | None = None  # cites


class InterpreterMessage(ToolMessage):
    tool_name: str = "execute_code"
    input: dict | None = None  # code
    output: list[OutputItem] | None = None  # code_results


# 1. 只带 code
# 2. 只带 code result
class CoderMessage(AgentMessage):
    agent_type: AgentType = AgentType.CODER


class WriterMessage(AgentMessage):
    agent_type: AgentType = AgentType.WRITER
    sub_title: str | None = None


# 所有可能的消息类型
MessageType = Union[
    SystemMessage,
    StepMessage,
    UserMessage,
    ModelerMessage,
    CoderMessage,
    WriterMessage,
    CoordinatorMessage,
]
