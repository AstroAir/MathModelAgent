from pydantic import BaseModel
from typing import Any


class CoordinatorToModeler(BaseModel):
    questions: dict
    ques_count: int


class ModelerToCoder(BaseModel):
    # 建模结果可以是字符串或嵌套字典，这里放宽为 Any 以兼容更多结构
    questions_solution: dict[str, Any]


class CoderToWriter(BaseModel):
    code_response: str | None = None
    code_output: str | None = None
    created_images: list[str] | None = None


class WriterResponse(BaseModel):
    response_content: Any
    footnotes: list[tuple[str, str]] | None = None
