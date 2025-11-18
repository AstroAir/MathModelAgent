from app.core.agents.agent import Agent
from app.core.llm.llm import LLM
from app.core.prompts import get_writer_prompt
from app.schemas.enums import CompTemplate, FormatOutPut
from app.tools.openalex_scholar import OpenAlexScholar
from app.tools.web_search_tool import WebSearchTool
from app.utils.task_logger import TaskLogger
from app.services.redis_manager import redis_manager
from app.schemas.response import SystemMessage, WriterMessage
import json
from app.core.functions import writer_tools
from icecream import ic
from app.schemas.A2A import WriterResponse


# WriterAgent：负责论文写作的Agent
# - 支持文献搜索工具（search_papers）
# - 自动处理图片引用（available_images参数）
# - 分段写作，支持footnotes引用管理
class WriterAgent(Agent):
    def __init__(
        self,
        task_id: str,
        model: LLM,
        task_logger: TaskLogger,
        max_chat_turns: int = 10,  # 添加最大对话轮次限制
        comp_template: CompTemplate = CompTemplate,
        format_output: FormatOutPut = FormatOutPut.Markdown,
        scholar: OpenAlexScholar = None,
        max_memory: int = 25,  # 添加最大记忆轮次
        language: str = "zh",
    ) -> None:
        super().__init__(task_id, model, task_logger, max_chat_turns, max_memory)
        self.format_out_put = format_output
        self.comp_template = comp_template
        self.scholar = scholar
        self.language = language
        self.is_first_run = True
        self.system_prompt = get_writer_prompt(format_output, language)
        self.available_images: list[str] = []
        self.web_search_tool = WebSearchTool()

    async def run(
        self,
        prompt: str,
        available_images: list[str] = None,
        sub_title: str = None,
    ) -> WriterResponse:
        """
        执行写作任务
        Args:
            prompt: 写作提示
            available_images: 可用的图片相对路径列表（如 20250420-173744-9f87792c/编号_分布.png）
            sub_title: 子任务标题
        """
        await self.task_logger.info(f"Subtitle is: {sub_title}")

        if self.is_first_run:
            self.is_first_run = False
            await self.append_chat_history(
                {"role": "system", "content": self.system_prompt}
            )

        if available_images:
            self.available_images = available_images
            # 拼接成完整URL
            image_list = ",".join(available_images)
            image_prompt = f"\nAvailable image URLs:\n{image_list}\nPlease reference these images appropriately in your writing."
            await self.task_logger.info(f"Image prompt is: {image_prompt}")
            prompt = prompt + image_prompt

        await self.task_logger.info(f"{self.__class__.__name__}: Starting execution.")
        self.current_chat_turns += 1  # 重置对话轮次计数器

        await self.append_chat_history({"role": "user", "content": prompt})

        # 获取历史消息用于本次对话
        response = await self.model.chat(
            history=self.chat_history,
            tools=writer_tools,
            tool_choice="auto",
            agent_name=self.__class__.__name__,
            sub_title=sub_title,
        )

        footnotes = []

        if (
            hasattr(response.choices[0].message, "tool_calls")
            and response.choices[0].message.tool_calls
        ):
            await self.task_logger.info("Tool call detected.")
            tool_call = response.choices[0].message.tool_calls[0]
            tool_id = tool_call.id

            if tool_call.function.name == "search_papers":
                await self.task_logger.info("Calling tool: search_papers")
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(
                        content=f"WriterAgent is calling {tool_call.function.name} tool."
                    ),
                )

                query = json.loads(tool_call.function.arguments)["query"]

                await redis_manager.publish_message(
                    self.task_id,
                    WriterMessage(
                        input={"query": query},
                    ),
                )

                # 更新对话历史 - 添加助手的响应
                await self.append_chat_history(response.choices[0].message.model_dump())
                ic(response.choices[0].message.model_dump())

                try:
                    papers = await self.scholar.search_papers(query)
                except Exception as e:
                    error_msg = f"Failed to search papers: {str(e)}"
                    await self.task_logger.error(error_msg)
                    return WriterResponse(
                        response_content=error_msg, footnotes=footnotes
                    )
                # 搜索结果已通过redis发送到前端
                papers_str = self.scholar.papers_to_str(papers)
                await self.task_logger.info(f"Paper search results:\n{papers_str}")
                await self.append_chat_history(
                    {
                        "role": "tool",
                        "content": papers_str,
                        "tool_call_id": tool_id,
                        "name": "search_papers",
                    }
                )
            elif tool_call.function.name == "web_search":
                await self.task_logger.info("Calling tool: web_search")
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(
                        content=f"WriterAgent is calling {tool_call.function.name} tool."
                    ),
                )

                # 解析参数
                args = json.loads(tool_call.function.arguments)
                query = args["query"]
                search_type = args.get("search_type", "general")
                provider = args.get("provider")
                max_results = args.get("max_results", 10)

                await redis_manager.publish_message(
                    self.task_id,
                    WriterMessage(
                        input={"query": query, "search_type": search_type},
                    ),
                )

                # 更新对话历史 - 添加助手的响应
                await self.append_chat_history(response.choices[0].message.model_dump())
                ic(response.choices[0].message.model_dump())

                try:
                    # 调用web搜索工具
                    search_result = await self.web_search_tool.search(
                        query=query,
                        search_type=search_type,
                        provider=provider,
                        max_results=max_results,
                    )

                    if search_result.error:
                        error_msg = f"Web search failed: {search_result.error}"
                        await self.task_logger.error(error_msg)
                        return WriterResponse(
                            response_content=error_msg, footnotes=footnotes
                        )

                    search_content = search_result.result
                    await self.task_logger.info(
                        f"Web search results:\n{search_content}"
                    )
                    await self.append_chat_history(
                        {
                            "role": "tool",
                            "content": search_content,
                            "tool_call_id": tool_id,
                            "name": "web_search",
                        }
                    )
                except Exception as e:
                    error_msg = f"Web search failed: {str(e)}"
                    await self.task_logger.error(error_msg)
                    return WriterResponse(
                        response_content=error_msg, footnotes=footnotes
                    )
                next_response = await self.model.chat(
                    history=self.chat_history,
                    tools=writer_tools,
                    tool_choice="auto",
                    agent_name=self.__class__.__name__,
                    sub_title=sub_title,
                )
                response_content = next_response.choices[0].message.content
        else:
            response_content = response.choices[0].message.content
        self.chat_history.append({"role": "assistant", "content": response_content})
        await self.task_logger.info(f"{self.__class__.__name__}: Finished execution.")
        return WriterResponse(response_content=response_content, footnotes=footnotes)

    async def summarize(self) -> str:
        """
        总结对话内容
        """
        try:
            await self.append_chat_history(
                {"role": "user", "content": "请简单总结以上完成什么任务取得什么结果:"}
            )
            # 获取历史消息用于本次对话
            response = await self.model.chat(
                history=self.chat_history, agent_name=self.__class__.__name__
            )
            await self.append_chat_history(
                {"role": "assistant", "content": response.choices[0].message.content}
            )
            return response.choices[0].message.content
        except Exception as e:
            await self.task_logger.error(f"Summary generation failed: {str(e)}")
            # 返回一个基础总结，避免完全失败
            return "Summary generation failed due to a network issue, but the main task has been completed."
