from app.core.agents.agent import Agent
from app.config.setting import settings
from app.utils.log_util import logger
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
        work_dir: str,  # 工作目录
        max_chat_turns: int = settings.MAX_CHAT_TURNS,  # 最大聊天次数
        max_retries: int = settings.MAX_RETRIES,  # 最大反思次数
        code_interpreter: BaseCodeInterpreter = None,
        language: str = "zh",
    ) -> None:
        super().__init__(task_id, model, max_chat_turns)
        self.work_dir = work_dir
        self.max_retries = max_retries
        self.is_first_run = True
        self.language = language
        self.system_prompt = get_coder_prompt(language)
        self.code_interpreter = code_interpreter
        self.web_search_tool = WebSearchTool()

    async def run(self, prompt: str, subtask_title: str) -> CoderToWriter:
        logger.info(f"{self.__class__.__name__}:开始:执行子任务: {subtask_title}")
        self.code_interpreter.add_section(subtask_title)

        # 如果是第一次运行，则添加系统提示
        if self.is_first_run:
            logger.info("首次运行，添加系统提示和数据集文件信息")
            self.is_first_run = False
            await self.append_chat_history(
                {"role": "system", "content": self.system_prompt}
            )
            # 当前数据集文件
            await self.append_chat_history(
                {
                    "role": "user",
                    "content": f"当前文件夹下的数据集文件{get_current_files(self.work_dir, 'data')}",
                }
            )

        # 添加 sub_task
        logger.info(f"添加子任务提示: {prompt}")
        await self.append_chat_history({"role": "user", "content": prompt})

        retry_count = 0
        last_error_message = ""

        while True:
            if retry_count >= self.max_retries:
                error_msg = f"任务失败，超过最大尝试次数{self.max_retries}, 最后错误信息: {last_error_message}"
                logger.error(f"超过最大尝试次数: {self.max_retries}")
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content="超过最大尝试次数，任务失败", type="error"),
                )
                logger.warning(error_msg)
                # 抛出异常而不是返回错误对象，让上层处理
                raise Exception(error_msg)

            if self.current_chat_turns >= self.max_chat_turns:
                error_msg = f"超过最大聊天次数 ({self.max_chat_turns})，任务未完成"
                logger.error(error_msg)
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content="超过最大聊天次数，任务失败", type="error"),
                )
                raise Exception(error_msg)

            self.current_chat_turns += 1
            logger.info(f"当前对话轮次: {self.current_chat_turns}")

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
                logger.info("检测到工具调用")
                tool_call = response.choices[0].message.tool_calls[0]
                tool_id = tool_call.id

                tool_name = tool_call.function.name
                logger.info(f"调用工具: {tool_name}")
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=f"代码手调用{tool_name}工具"),
                )

                # 更新对话历史 - 添加助手的响应
                await self.append_chat_history(response.choices[0].message.model_dump())
                logger.info(response.choices[0].message.model_dump())

                if tool_name == "execute_code":
                    code = json.loads(tool_call.function.arguments)["code"]

                    await redis_manager.publish_message(
                        self.task_id,
                        InterpreterMessage(input={"code": code}),
                    )

                    # 执行工具调用
                    logger.info("执行代码")
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

                        logger.warning(f"代码执行错误: {error_message}")
                        retry_count += 1
                        logger.info(f"当前尝试次:{retry_count} / {self.max_retries}")
                        last_error_message = error_message
                        reflection_prompt = get_reflection_prompt(
                            error_message, code, self.language
                        )

                        await redis_manager.publish_message(
                            self.task_id,
                            SystemMessage(content="代码手反思纠正错误", type="error"),
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
                    logger.info(f"安装包: {packages}")

                    (
                        text_to_gpt,
                        error_occurred,
                        error_message,
                    ) = await self.code_interpreter.execute_code(pip_code)

                    result_msg = (
                        f"成功安装: {packages}"
                        if not error_occurred
                        else f"安装失败: {error_message}"
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
                        logger.info(f"列出文件: {files_str}")
                    except Exception as e:
                        files_str = f"Error listing files: {str(e)}"
                        logger.error(files_str)

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
                        logger.info(f"读取文件: {filename}")
                    except UnicodeDecodeError:
                        # 如果是二进制文件
                        file_size = os.path.getsize(filepath)
                        content = f"Binary file: {filename} (size: {file_size} bytes)"
                        logger.info(f"二进制文件: {filename}")
                    except Exception as e:
                        content = f"Error reading file: {str(e)}"
                        logger.error(f"读取文件失败: {str(e)}")

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

                    logger.info(f"网络搜索: {query}")

                    try:
                        # 调用web搜索工具
                        search_result = await self.web_search_tool.search(
                            query=query,
                            search_type=search_type,
                            provider=provider,
                            max_results=max_results,
                        )

                        if search_result.error:
                            content = f"搜索失败: {search_result.error}"
                        else:
                            content = search_result.result

                        logger.info(f"搜索结果: {content[:200]}...")

                    except Exception as e:
                        content = f"搜索失败: {str(e)}"
                        logger.error(f"网络搜索失败: {str(e)}")

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
                logger.info("没有工具调用，任务完成")
                return CoderToWriter(
                    coder_response=response.choices[0].message.content,
                    created_images=await self.code_interpreter.get_created_images(
                        subtask_title
                    ),
                )

        logger.info(f"{self.__class__.__name__}:完成:执行子任务: {subtask_title}")
