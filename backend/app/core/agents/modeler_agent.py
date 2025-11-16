from app.core.agents.agent import Agent
from app.core.llm.llm import LLM
from app.core.prompts import get_modeler_prompt
from app.schemas.A2A import CoordinatorToModeler, ModelerToCoder
from app.utils.log_util import logger
import json
from icecream import ic

# ModelerAgent：负责数学建模方案设计的Agent
# 当前实现：通过LLM生成建模思路和求解方案


class ModelerAgent(Agent):  # 继承自Agent类
    def __init__(
        self,
        task_id: str,
        model: LLM,
        max_chat_turns: int = 30,
        language: str = "zh",
    ) -> None:
        super().__init__(task_id, model, max_chat_turns)
        self.system_prompt = get_modeler_prompt(language)

    async def run(self, coordinator_to_modeler: CoordinatorToModeler) -> ModelerToCoder:
        await self.append_chat_history(
            {"role": "system", "content": self.system_prompt}
        )
        await self.append_chat_history(
            {
                "role": "user",
                "content": json.dumps(coordinator_to_modeler.questions),
            }
        )

        response = await self.model.chat(
            history=self.chat_history,
            agent_name=self.__class__.__name__,
        )

        json_str = response.choices[0].message.content

        json_str = json_str.replace("```json", "").replace("```", "").strip()

        if not json_str:
            raise ValueError("返回的 JSON 字符串为空，请检查输入内容。")
        try:
            questions_solution = json.loads(json_str)
            ic(questions_solution)
            return ModelerToCoder(questions_solution=questions_solution)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析错误: {e}")
