from app.core.agents.agent import Agent
from app.config.setting import settings
from app.utils.task_logger import TaskLogger
from app.services.redis_manager import redis_manager
from app.schemas.response import SystemMessage, InterpreterMessage
from app.tools.base_interpreter import BaseCodeInterpreter
from app.tools.web_search_tool import WebSearchTool
from app.core.llm.llm import LLM
from app.schemas.A2A import CoderToWriter
from app.core.prompts import get_coder_prompt, get_reflection_prompt
from app.utils.common_utils import get_current_files
import json
from app.core.functions import coder_tools

# CoderAgent：负责代码生成和执行的Agent
# - 支持工具：execute_code, pip_install, list_files, read_file
# - 自动错误重试和反思机制（max_retries控制）
# - 集成Jupyter内核，支持代码执行和结果记录
# 注意：长时间执行可通过timeout参数控制，CUDA支持取决于环境配置


class CoderAgent(Agent):  # 同样继承自Agent类
    def __init__(
        self,
        task_id: str,
        model: LLM,
        task_logger: TaskLogger,  # Added
        work_dir: str,  # 工作目录
        max_chat_turns: int = settings.MAX_CHAT_TURNS,  # 最大聊天次数
        max_retries: int = settings.MAX_RETRIES,  # 最大反思次数
        code_interpreter: BaseCodeInterpreter = None,
        language: str = "zh",
    ) -> None:
        super().__init__(task_id, model, task_logger, max_chat_turns)
        self.work_dir = work_dir
        self.max_retries = max_retries
        self.is_first_run = True
        self.language = language
        self.system_prompt = get_coder_prompt(language)
        self.code_interpreter = code_interpreter
        self.web_search_tool = WebSearchTool()

    async def run(self, prompt: str, subtask_title: str) -> CoderToWriter:
        await self.task_logger.info(
            f"{self.__class__.__name__}: Starting subtask: {subtask_title}"
        )
        self.code_interpreter.add_section(subtask_title)

        # 如果是第一次运行，则添加系统提示
        if self.is_first_run:
            await self.task_logger.info(
                "First run, adding system prompt and dataset file info."
            )
            self.is_first_run = False
            await self.append_chat_history(
                {"role": "system", "content": self.system_prompt}
            )
            # 当前数据集文件
            await self.append_chat_history(
                {
                    "role": "user",
                    "content": f"Current dataset files in the folder: {get_current_files(self.work_dir, 'data')}",
                }
            )

        # 添加 sub_task
        await self.task_logger.info(f"Adding subtask prompt: {prompt}")
        await self.append_chat_history({"role": "user", "content": prompt})

        retry_count = 0
        last_error_message = ""

        while True:
            if retry_count >= self.max_retries:
                error_msg = f"Task failed, exceeded max retries {self.max_retries}, last error: {last_error_message}"
                await self.task_logger.error(
                    f"Exceeded max retries: {self.max_retries}"
                )
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(
                        content="Exceeded max retries, task failed", type="error"
                    ),
                )
                await self.task_logger.warning(error_msg)
                # 抛出异常而不是返回错误对象，让上层处理
                raise Exception(error_msg)

            if self.current_chat_turns >= self.max_chat_turns:
                error_msg = f"Exceeded max chat turns ({self.max_chat_turns}), task not completed"
                await self.task_logger.error(error_msg)
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(
                        content="Exceeded max chat turns, task failed", type="error"
                    ),
                )
                raise Exception(error_msg)

            self.current_chat_turns += 1
            await self.task_logger.info(f"Current chat turn: {self.current_chat_turns}")

            response = await self.model.chat(
                history=self.chat_history,
                tools=coder_tools,
                tool_choice="auto",
                agent_name=self.__class__.__name__,
            )

            # 如果有工具调用
            if (
                hasattr(response.choices[0].message, "tool_calls")
                and response.choices[0].message.tool_calls
            ):
                await self.task_logger.info("Tool call detected.")
                tool_call = response.choices[0].message.tool_calls[0]
                tool_id = tool_call.id

                tool_name = tool_call.function.name
                await self.task_logger.info(f"Calling tool: {tool_name}")
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=f"CoderAgent is calling {tool_name} tool."),
                )

                # 更新对话历史 - 添加助手的响应
                await self.append_chat_history(response.choices[0].message.model_dump())
                await self.task_logger.info(
                    f"Appending tool call to history: {response.choices[0].message.model_dump()}"
                )

                if tool_name == "execute_code":
                    code = json.loads(tool_call.function.arguments)["code"]

                    await redis_manager.publish_message(
                        self.task_id,
                        InterpreterMessage(input={"code": code}),
                    )

                    # 执行工具调用
                    await self.task_logger.info("Executing code.")
                    (
                        text_to_gpt,
                        error_occurred,
                        error_message,
                    ) = await self.code_interpreter.execute_code(code)

                    # 添加工具执行结果
                    if error_occurred:
                        await self.append_chat_history(
                            {
                                "role": "tool",
                                "tool_call_id": tool_id,
                                "name": "execute_code",
                                "content": error_message,
                            }
                        )

                        await self.task_logger.warning(
                            f"Code execution error: {error_message}"
                        )
                        retry_count += 1
                        await self.task_logger.info(
                            f"Current retry attempt: {retry_count} / {self.max_retries}"
                        )
                        last_error_message = error_message
                        reflection_prompt = get_reflection_prompt(
                            error_message, code, self.language
                        )

                        await redis_manager.publish_message(
                            self.task_id,
                            SystemMessage(
                                content="CoderAgent is reflecting on the error.",
                                type="error",
                            ),
                        )

                        await self.append_chat_history(
                            {"role": "user", "content": reflection_prompt}
                        )
                        continue
                    else:
                        await self.append_chat_history(
                            {
                                "role": "tool",
                                "tool_call_id": tool_id,
                                "name": "execute_code",
                                "content": text_to_gpt,
                            }
                        )
                        continue

                elif tool_name == "pip_install":
                    packages = json.loads(tool_call.function.arguments)["packages"]
                    pip_code = f"!pip install {packages}"
                    await self.task_logger.info(f"Installing packages: {packages}")

                    (
                        text_to_gpt,
                        error_occurred,
                        error_message,
                    ) = await self.code_interpreter.execute_code(pip_code)

                    result_msg = (
                        f"Successfully installed: {packages}"
                        if not error_occurred
                        else f"Installation failed: {error_message}"
                    )
                    await self.append_chat_history(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "name": "pip_install",
                            "content": result_msg,
                        }
                    )
                    continue

                elif tool_name == "list_files":
                    import os

                    args = json.loads(tool_call.function.arguments)
                    extension = args.get("extension", "")

                    try:
                        files = os.listdir(self.work_dir)
                        if extension:
                            files = [f for f in files if f.endswith(extension)]
                        files_str = "\n".join(files) if files else "No files found"
                        await self.task_logger.info(f"Listing files: {files_str}")
                    except Exception as e:
                        files_str = f"Error listing files: {str(e)}"
                        await self.task_logger.error(files_str)

                    await self.append_chat_history(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "name": "list_files",
                            "content": files_str,
                        }
                    )
                    continue

                elif tool_name == "read_file":
                    import os

                    filename = json.loads(tool_call.function.arguments)["filename"]
                    filepath = os.path.join(self.work_dir, filename)

                    try:
                        # 尝试以文本模式读取
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()
                            # 限制长度，避免内容过长
                            if len(content) > 5000:
                                content = (
                                    content[:5000]
                                    + f"\n... (truncated, total {len(content)} characters)"
                                )
                        await self.task_logger.info(f"Reading file: {filename}")
                    except UnicodeDecodeError:
                        # 如果是二进制文件
                        file_size = os.path.getsize(filepath)
                        content = f"Binary file: {filename} (size: {file_size} bytes)"
                        await self.task_logger.info(f"Binary file detected: {filename}")
                    except Exception as e:
                        content = f"Error reading file: {str(e)}"
                        await self.task_logger.error(f"Failed to read file: {str(e)}")

                    await self.append_chat_history(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "name": "read_file",
                            "content": content,
                        }
                    )
                    continue

                elif tool_name == "web_search":
                    # 解析参数
                    args = json.loads(tool_call.function.arguments)
                    query = args["query"]
                    search_type = args.get("search_type", "general")
                    provider = args.get("provider")
                    max_results = args.get("max_results", 10)

                    await self.task_logger.info(f"Performing web search: {query}")

                    try:
                        # 调用web搜索工具
                        search_result = await self.web_search_tool.search(
                            query=query,
                            search_type=search_type,
                            provider=provider,
                            max_results=max_results,
                        )

                        if search_result.error:
                            content = f"Search failed: {search_result.error}"
                        else:
                            content = search_result.result

                        await self.task_logger.info(
                            f"Search result: {content[:200]}..."
                        )

                    except Exception as e:
                        content = f"Search failed: {str(e)}"
                        await self.task_logger.error(f"Web search failed: {str(e)}")

                    await self.append_chat_history(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "name": "web_search",
                            "content": content,
                        }
                    )
                    continue
            else:
                # 没有工具调用，表示任务完成
                await self.task_logger.info("No tool call detected, task is complete.")
                return CoderToWriter(
                    coder_response=response.choices[0].message.content,
                    created_images=await self.code_interpreter.get_created_images(
                        subtask_title
                    ),
                )

        await self.task_logger.info(
            f"{self.__class__.__name__}: Finished subtask: {subtask_title}"
        )
