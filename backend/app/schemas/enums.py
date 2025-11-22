from enum import Enum


class CompTemplate(str, Enum):
    CHINA: str = "CHINA"
    AMERICAN: str = "AMERICAN"
    # 兼容旧枚举名称（测试与部分代码中使用 GUOSAI/MEISAI）
    GUOSAI: str = "CHINA"
    MEISAI: str = "AMERICAN"


class FormatOutPut(str, Enum):
    Markdown: str = "Markdown"
    LaTeX: str = "LaTeX"
    # 兼容全大写枚举名称（测试中使用 MARKDOWN/LATEX）
    MARKDOWN: str = "Markdown"
    LATEX: str = "LaTeX"


class AgentType(str, Enum):
    COORDINATOR = "CoordinatorAgent"
    MODELER = "ModelerAgent"
    CODER = "CoderAgent"
    WRITER = "WriterAgent"
    SYSTEM = "SystemAgent"


class AgentStatus(str, Enum):
    START = "start"
    WORKING = "working"
    DONE = "done"
    ERROR = "error"
    SUCCESS = "success"
