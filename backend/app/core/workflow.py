from app.core.agents import WriterAgent, CoderAgent, CoordinatorAgent, ModelerAgent
from app.schemas.request import Problem
from app.schemas.response import SystemMessage, StepMessage
from app.tools.openalex_scholar import OpenAlexScholar
from app.utils.log_util import logger
from app.utils.common_utils import create_work_dir, get_config_template
from app.models.user_output import UserOutput
from app.config.setting import settings
from app.tools.interpreter_factory import create_interpreter
from app.services.redis_manager import redis_manager
from app.tools.notebook_serializer import NotebookSerializer
from app.core.flows import Flows
from app.core.llm.llm_factory import LLMFactory
from app.utils.messages import get_message
from app.utils.language_detector import detect_language_detailed

class WorkFlow:
    """工作流基类，定义工作流的基本接口"""
    def __init__(self):
        """初始化工作流"""
        pass

    def execute(self) -> str:
        """执行工作流，由子类实现具体逻辑"""
        raise NotImplementedError("子类必须实现execute方法")


class MathModelWorkFlow(WorkFlow):
    task_id: str  #
    work_dir: str  # worklow work dir
    ques_count: int = 0  # 问题数量
    questions: dict[str, str | int] = {}  # 问题

    async def execute(self, problem: Problem):
        self.task_id = problem.task_id
        self.work_dir = create_work_dir(self.task_id)
        
        # Auto-detect language if set to "auto"
        if problem.language == "auto":
            detected = detect_language_detailed(problem.ques_all)
            problem.language = detected["language"]
            logger.info(
                f"Auto-detected language: {problem.language} "
                f"(confidence: {detected['confidence']:.2%}, "
                f"Chinese ratio: {detected['chinese_ratio']:.2%})"
            )
            await redis_manager.publish_message(
                self.task_id,
                SystemMessage(
                    content=f"Language auto-detected: {'Chinese' if problem.language == 'zh' else 'English'} "
                    f"(confidence: {detected['confidence']:.0%})"
                ),
            )

        llm_factory = LLMFactory(self.task_id)
        coordinator_llm, modeler_llm, coder_llm, writer_llm = llm_factory.get_all_llms()

        coordinator_agent = CoordinatorAgent(self.task_id, coordinator_llm, language=problem.language)

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content=get_message("coordinator_start", problem.language)),
        )

        try:
            coordinator_response = await coordinator_agent.run(problem.ques_all)
            self.questions = coordinator_response.questions
            self.ques_count = coordinator_response.ques_count
        except Exception as e:
            #  非数学建模问题
            logger.error(f"CoordinatorAgent 执行失败: {e}")
            raise e

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content=get_message("coordinator_complete", problem.language)),
        )

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content=get_message("modeler_start", problem.language)),
        )

        modeler_agent = ModelerAgent(self.task_id, modeler_llm, language=problem.language)

        modeler_response = await modeler_agent.run(coordinator_response)

        user_output = UserOutput(work_dir=self.work_dir, ques_count=self.ques_count)

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content=get_message("creating_sandbox", problem.language)),
        )

        notebook_serializer = NotebookSerializer(work_dir=self.work_dir)
        code_interpreter = await create_interpreter(
            kind="local",
            task_id=self.task_id,
            work_dir=self.work_dir,
            notebook_serializer=notebook_serializer,
            timeout=3000,
        )
        
        scholar = OpenAlexScholar(task_id=self.task_id, email=settings.OPENALEX_EMAIL)

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content=get_message("sandbox_created", problem.language)),
        )

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content=get_message("init_coder", problem.language)),
        )

        # modeler_agent
        coder_agent = CoderAgent(
            task_id=problem.task_id,
            model=coder_llm,
            work_dir=self.work_dir,
            max_chat_turns=settings.MAX_CHAT_TURNS,
            max_retries=settings.MAX_RETRIES,
            code_interpreter=code_interpreter,
            language=problem.language,
        )

        writer_agent = WriterAgent(
            task_id=problem.task_id,
            model=writer_llm,
            comp_template=problem.comp_template,
            format_output=problem.format_output,
            scholar=scholar,
            language=problem.language,
        )

        flows = Flows(self.questions, language=problem.language, work_dir=self.work_dir)

        ################################################ solution steps
        solution_flows = flows.get_solution_flows(self.questions, modeler_response)
        config_template = get_config_template(problem.comp_template, problem.language)

        for key, value in solution_flows.items():
            try:
                # 发送步骤消息：代码手开始求解
                await redis_manager.publish_message(
                    self.task_id,
                    StepMessage(
                        step_name=f"代码手开始求解{key}",
                        step_type="agent",
                        status="processing",
                        agent_type="CoderAgent",
                        content=f"代码手开始求解{key}"
                    ),
                )
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=get_message("coder_start", problem.language, key=key)),
                )

                coder_response = await coder_agent.run(
                    prompt=value["coder_prompt"], subtask_title=key
                )

                # 发送步骤消息：代码手求解成功
                await redis_manager.publish_message(
                    self.task_id,
                    StepMessage(
                        step_name=f"代码手求解成功{key}",
                        step_type="agent",
                        status="completed",
                        agent_type="CoderAgent",
                        content=f"代码手求解成功{key}"
                    ),
                )
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=get_message("coder_success", problem.language, key=key), type="success"),
                )

                writer_prompt = flows.get_writer_prompt(
                    key, coder_response.coder_response, code_interpreter, config_template
                )

                # 发送步骤消息：论文手开始写作
                await redis_manager.publish_message(
                    self.task_id,
                    StepMessage(
                        step_name=f"论文手开始写{key}部分",
                        step_type="agent",
                        status="processing",
                        agent_type="WriterAgent",
                        content=f"论文手开始写{key}部分"
                    ),
                )
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=get_message("writer_start", problem.language, key=key)),
                )

                # 传递创建的图片给writer，用于引用
                writer_response = await writer_agent.run(
                    writer_prompt,
                    available_images=coder_response.created_images,
                    sub_title=key,
                )

                # 发送步骤消息：论文手完成写作
                await redis_manager.publish_message(
                    self.task_id,
                    StepMessage(
                        step_name=f"论文手完成{key}部分",
                        step_type="agent",
                        status="completed",
                        agent_type="WriterAgent",
                        content=f"论文手完成{key}部分"
                    ),
                )
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=get_message("writer_complete", problem.language, key=key)),
                )

                user_output.set_res(key, writer_response)
                
            except Exception as e:
                error_msg = f"处理子任务 {key} 时发生错误: {str(e)}"
                logger.error(error_msg)
                # 发送步骤消息：任务失败
                await redis_manager.publish_message(
                    self.task_id,
                    StepMessage(
                        step_name=f"子任务 {key} 失败",
                        step_type="task",
                        status="failed",
                        content=f"子任务 {key} 失败: {str(e)}",
                        details={"error": str(e)}
                    ),
                )
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=get_message("subtask_failed", problem.language, key=key, error=str(e)), type="error"),
                )
                # 继续处理其他子任务而不是完全停止
                continue

        # 关闭沙盒

        await code_interpreter.cleanup()
        logger.info(user_output.get_res())

        ################################################ write steps

        write_flows = flows.get_write_flows(
            user_output, config_template, problem.ques_all
        )
        for key, value in write_flows.items():
            try:
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=get_message("writer_start", problem.language, key=key)),
                )

                writer_response = await writer_agent.run(prompt=value, sub_title=key)

                user_output.set_res(key, writer_response)
                
            except Exception as e:
                error_msg = f"论文手处理 {key} 部分时发生错误: {str(e)}"
                logger.error(error_msg)
                await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=get_message("writer_failed", problem.language, key=key, error=str(e)), type="error"),
                )
                # 继续处理其他部分
                continue

        logger.info(user_output.get_res())

        user_output.save_result()
