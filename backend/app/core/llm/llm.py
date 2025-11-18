from app.utils.common_utils import transform_link, split_footnotes
from app.utils.log_util import logger
import asyncio
from app.schemas.response import (
    CoderMessage,
    WriterMessage,
    ModelerMessage,
    SystemMessage,
    CoordinatorMessage,
)
from app.services.redis_manager import redis_manager
from litellm import acompletion
import litellm
from app.schemas.enums import AgentType
from app.utils.track import agent_metrics
from icecream import ic
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.utils.provider_manager import ProviderManager

litellm.callbacks = [agent_metrics]


class LLM:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str,
        task_id: str,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.chat_count = 0
        self.max_tokens: int | None = None  # 添加最大token数限制
        self.task_id = task_id

    async def chat(
        self,
        history: list = None,
        tools: list = None,
        tool_choice: str = None,
        max_retries: int = 8,  # 添加最大重试次数
        retry_delay: float = 1.0,  # 添加重试延迟
        top_p: float | None = None,  # 添加top_p参数,
        agent_name: AgentType = AgentType.SYSTEM,  # CoderAgent or WriterAgent
        sub_title: str | None = None,
    ) -> str:
        logger.info(f"subtitle是:{sub_title}")

        # 验证和修复工具调用完整性
        if history:
            history = self._validate_and_fix_tool_calls(history)

        kwargs = {
            "api_key": self.api_key,
            "model": self.model,
            "messages": history,
            "stream": False,
            "top_p": top_p,
            "metadata": {"agent_name": agent_name},
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        if self.max_tokens:
            kwargs["max_tokens"] = self.max_tokens

        if self.base_url:
            kwargs["base_url"] = self.base_url
        litellm.enable_json_schema_validation = True  # 加入json格式验证

        # 当前使用非流式输出，确保完整响应后再处理
        for attempt in range(max_retries):
            try:
                # completion = self.client.chat.completions.create(**kwargs)
                response = await acompletion(**kwargs)
                logger.info(f"API返回: {response}")
                if not response or not hasattr(response, "choices"):
                    raise ValueError("无效的API响应")
                self.chat_count += 1
                await self.send_message(response, agent_name, sub_title)
                return response
            except Exception as e:
                logger.error(
                    f"LLM调用失败，第{attempt + 1}/{max_retries}次重试: {str(e)}"
                )
                if attempt < max_retries - 1:  # 如果不是最后一次尝试
                    await asyncio.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue
                logger.error(f"LLM调用失败，已达最大重试次数: {max_retries}")
                logger.debug(f"请求参数: {kwargs}")
                raise  # 如果所有重试都失败，则抛出异常

    def _validate_and_fix_tool_calls(self, history: list) -> list:
        """验证并修复工具调用完整性"""
        if not history:
            return history

        ic(f"🔍 开始验证工具调用，历史消息数量: {len(history)}")

        # 查找所有未匹配的tool_calls
        fixed_history = []
        i = 0

        while i < len(history):
            msg = history[i]

            # 如果是包含tool_calls的消息
            if isinstance(msg, dict) and "tool_calls" in msg and msg["tool_calls"]:
                ic(f"📞 发现tool_calls消息在位置 {i}")

                # 检查每个tool_call是否都有对应的response，分别处理
                valid_tool_calls = []
                invalid_tool_calls = []

                for tool_call in msg["tool_calls"]:
                    tool_call_id = tool_call.get("id")
                    ic(f"  检查tool_call_id: {tool_call_id}")

                    if tool_call_id:
                        # 查找对应的tool响应
                        found_response = False
                        for j in range(i + 1, len(history)):
                            if (
                                history[j].get("role") == "tool"
                                and history[j].get("tool_call_id") == tool_call_id
                            ):
                                ic(f"  ✅ 找到匹配响应在位置 {j}")
                                found_response = True
                                break

                        if found_response:
                            valid_tool_calls.append(tool_call)
                        else:
                            ic(f"  ❌ 未找到匹配响应: {tool_call_id}")
                            invalid_tool_calls.append(tool_call)

                # 根据检查结果处理消息
                if valid_tool_calls:
                    # 有有效的tool_calls，保留它们
                    fixed_msg = msg.copy()
                    fixed_msg["tool_calls"] = valid_tool_calls
                    fixed_history.append(fixed_msg)
                    ic(
                        f"  🔧 保留 {len(valid_tool_calls)} 个有效tool_calls，移除 {len(invalid_tool_calls)} 个无效的"
                    )
                else:
                    # 没有有效的tool_calls，移除tool_calls但可能保留其他内容
                    cleaned_msg = {k: v for k, v in msg.items() if k != "tool_calls"}
                    if cleaned_msg.get("content"):
                        fixed_history.append(cleaned_msg)
                        ic("  🔧 移除所有tool_calls，保留消息内容")
                    else:
                        ic("  🗑️ 完全移除空的tool_calls消息")

            # 如果是tool响应消息，检查是否是孤立的
            elif isinstance(msg, dict) and msg.get("role") == "tool":
                tool_call_id = msg.get("tool_call_id")
                ic(f"🔧 检查tool响应消息: {tool_call_id}")

                # 查找对应的tool_calls
                found_call = False
                for j in range(len(fixed_history)):
                    if fixed_history[j].get("tool_calls") and any(
                        tc.get("id") == tool_call_id
                        for tc in fixed_history[j]["tool_calls"]
                    ):
                        found_call = True
                        break

                if found_call:
                    fixed_history.append(msg)
                    ic("  ✅ 保留有效的tool响应")
                else:
                    ic(f"  🗑️ 移除孤立的tool响应: {tool_call_id}")

            else:
                # 普通消息，直接保留
                fixed_history.append(msg)

            i += 1

        if len(fixed_history) != len(history):
            ic(f"🔧 修复完成: {len(history)} -> {len(fixed_history)} 条消息")
        else:
            ic("✅ 验证通过，无需修复")

        return fixed_history

    async def send_message(self, response, agent_name, sub_title=None):
        logger.info(f"subtitle是:{sub_title}")
        content = response.choices[0].message.content

        match agent_name:
            case AgentType.CODER:
                agent_msg: CoderMessage = CoderMessage(content=content)
            case AgentType.WRITER:
                # 处理 Markdown 格式的图片语法
                content, _ = split_footnotes(content)
                content = transform_link(self.task_id, content)
                agent_msg: WriterMessage = WriterMessage(
                    content=content,
                    sub_title=sub_title,
                )
            case AgentType.MODELER:
                agent_msg: ModelerMessage = ModelerMessage(content=content)
            case AgentType.SYSTEM:
                agent_msg: SystemMessage = SystemMessage(content=content)
            case AgentType.COORDINATOR:
                agent_msg: CoordinatorMessage = CoordinatorMessage(content=content)
            case _:
                raise ValueError(f"不支持的agent类型: {agent_name}")

        await redis_manager.publish_message(
            self.task_id,
            agent_msg,
        )


# class DeepSeekModel(LLM):
#     def __init__(
#         self,
#         api_key: str,
#         model: str,
#         base_url: str,
#         task_id: str,
#     ):
#         super().__init__(api_key, model, base_url, task_id)
# self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)


class ManagedLLM(LLM):
    """带提供商管理和速率限制的 LLM"""

    def __init__(
        self,
        provider_manager: "ProviderManager",
        task_id: str,
        agent_name: str,
    ):
        # 使用第一个提供商初始化基类
        first_provider = (
            provider_manager.providers[0] if provider_manager.providers else None
        )
        if not first_provider:
            raise ValueError(f"No providers configured for {agent_name}")

        super().__init__(
            api_key=first_provider.api_key,
            model=first_provider.model,
            base_url=first_provider.base_url,
            task_id=task_id,
        )

        self.provider_manager = provider_manager
        self.agent_name = agent_name
        self.current_provider = first_provider

    async def chat(
        self,
        history: list = None,
        tools: list = None,
        tool_choice: str = None,
        max_retries: int = 8,
        retry_delay: float = 1.0,
        top_p: float | None = None,
        agent_name: AgentType = AgentType.SYSTEM,
        sub_title: str | None = None,
    ) -> str:
        """
        带提供商管理和速率限制的聊天方法

        自动处理：
        - 速率限制检查
        - 提供商故障转移
        - 重试逻辑
        """
        # 估算 token 数量（简单估算：字符数 / 4）
        estimated_tokens = 0
        if history:
            for msg in history:
                content = msg.get("content", "")
                if isinstance(content, str):
                    estimated_tokens += len(content) // 4

        # 尝试所有可用的提供商
        exclude_providers = []
        last_error = None

        for attempt in range(max_retries):
            try:
                # 获取下一个可用的提供商
                provider = await self.provider_manager.get_next_provider(
                    estimated_tokens=estimated_tokens,
                    exclude_providers=exclude_providers,
                )

                if not provider:
                    logger.error(
                        "No available providers, all providers exhausted or rate limited"
                    )
                    if last_error:
                        raise last_error
                    raise Exception("No available providers")

                # 更新当前提供商配置
                self.current_provider = provider
                self.api_key = provider.api_key
                self.model = provider.model
                self.base_url = provider.base_url

                logger.info(
                    f"Using provider: {provider.name} (model: {provider.model}) "
                    f"for {self.agent_name}, attempt {attempt + 1}/{max_retries}"
                )

                # 发送速率限制警告消息
                if attempt > 0:
                    await self._send_rate_limit_warning(provider.name, attempt)

                # 调用父类的 chat 方法
                try:
                    response = await super().chat(
                        history=history,
                        tools=tools,
                        tool_choice=tool_choice,
                        max_retries=1,  # 单个提供商只尝试一次
                        retry_delay=retry_delay,
                        top_p=top_p,
                        agent_name=agent_name,
                        sub_title=sub_title,
                    )

                    # 记录成功
                    actual_tokens = 0
                    if hasattr(response, "usage") and response.usage:
                        actual_tokens = response.usage.total_tokens

                    await self.provider_manager.record_request_result(
                        provider=provider,
                        success=True,
                        actual_tokens=actual_tokens,
                        estimated_tokens=estimated_tokens,
                    )

                    return response

                except Exception as e:
                    last_error = e
                    logger.error(
                        f"Provider {provider.name} failed: {str(e)}, "
                        f"attempt {attempt + 1}/{max_retries}"
                    )

                    # 记录失败
                    await self.provider_manager.record_request_result(
                        provider=provider,
                        success=False,
                    )

                    # 将此提供商加入排除列表
                    exclude_providers.append(provider.get_identifier())

                    # 如果还有重试机会，继续
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        raise

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(f"Retrying after error: {str(e)}")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error(f"All retry attempts exhausted: {str(e)}")
                    raise

        # 如果所有尝试都失败
        if last_error:
            raise last_error
        raise Exception("Failed to complete request after all retries")

    async def _send_rate_limit_warning(self, provider_name: str, attempt: int):
        """发送速率限制警告消息到前端"""
        warning_msg = SystemMessage(
            content=f"⚠️ 速率限制触发，切换到备用提供商: {provider_name} (尝试 {attempt + 1})"
        )
        await redis_manager.publish_message(self.task_id, warning_msg)

    async def get_provider_stats(self):
        """获取提供商统计信息"""
        return await self.provider_manager.get_all_stats()


async def simple_chat(model: LLM, history: list) -> str:
    """
    Description of the function.

    Args:
        model (LLM): 模型
        history (list): 构造好的历史记录（包含system_prompt,user_prompt）

    Returns:
        return_type: Description of the return value.
    """
    kwargs = {
        "api_key": model.api_key,
        "model": model.model,
        "messages": history,
        "stream": False,
    }

    if model.base_url:
        kwargs["base_url"] = model.base_url

    response = await acompletion(**kwargs)

    return response.choices[0].message.content
