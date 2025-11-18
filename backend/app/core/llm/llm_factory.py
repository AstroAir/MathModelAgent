from app.config.setting import settings
from app.core.llm.llm import LLM, ManagedLLM
from app.utils.config_loader import config_loader
from app.utils.provider_manager import ProviderManager
from app.utils.log_util import logger


class LLMFactory:
    task_id: str
    use_provider_manager: bool

    def __init__(self, task_id: str, use_provider_manager: bool = True) -> None:
        self.task_id = task_id
        self.use_provider_manager = use_provider_manager

    def get_all_llms(self) -> tuple[LLM, LLM, LLM, LLM]:
        """获取所有 Agent 的 LLM 实例"""
        if self.use_provider_manager:
            return self._get_managed_llms()
        else:
            return self._get_simple_llms()

    def _get_managed_llms(
        self,
    ) -> tuple[ManagedLLM, ManagedLLM, ManagedLLM, ManagedLLM]:
        """获取带提供商管理的 LLM 实例"""
        coordinator_llm = self._create_managed_llm("coordinator")
        modeler_llm = self._create_managed_llm("modeler")
        coder_llm = self._create_managed_llm("coder")
        writer_llm = self._create_managed_llm("writer")

        return coordinator_llm, modeler_llm, coder_llm, writer_llm

    def _get_simple_llms(self) -> tuple[LLM, LLM, LLM, LLM]:
        """获取简单的 LLM 实例（向后兼容）"""
        coordinator_llm = LLM(
            api_key=settings.COORDINATOR_API_KEY,
            model=settings.COORDINATOR_MODEL,
            base_url=settings.COORDINATOR_BASE_URL,
            task_id=self.task_id,
        )

        modeler_llm = LLM(
            api_key=settings.MODELER_API_KEY,
            model=settings.MODELER_MODEL,
            base_url=settings.MODELER_BASE_URL,
            task_id=self.task_id,
        )

        coder_llm = LLM(
            api_key=settings.CODER_API_KEY,
            model=settings.CODER_MODEL,
            base_url=settings.CODER_BASE_URL,
            task_id=self.task_id,
        )

        writer_llm = LLM(
            api_key=settings.WRITER_API_KEY,
            model=settings.WRITER_MODEL,
            base_url=settings.WRITER_BASE_URL,
            task_id=self.task_id,
        )

        return coordinator_llm, modeler_llm, coder_llm, writer_llm

    def _create_managed_llm(self, agent_name: str) -> ManagedLLM:
        """创建带提供商管理的 LLM 实例"""
        providers = config_loader.get_agent_providers(agent_name)

        # 如果没有配置提供商，回退到环境变量配置
        if not providers:
            logger.warning(
                f"No providers configured for {agent_name}, falling back to settings"
            )
            return self._create_fallback_llm(agent_name)

        rotation_strategy = config_loader.get_rotation_strategy(agent_name)
        retry_config = config_loader.get_retry_config(agent_name)

        provider_manager = ProviderManager(
            providers=providers,
            rotation_strategy=rotation_strategy,
            auto_retry=retry_config["auto_retry"],
            max_retries=retry_config["max_retries"],
        )

        return ManagedLLM(
            provider_manager=provider_manager,
            task_id=self.task_id,
            agent_name=agent_name,
        )

    def _create_fallback_llm(self, agent_name: str) -> ManagedLLM:
        """创建回退的 LLM 实例（使用环境变量配置）"""
        from app.utils.provider_manager import ProviderConfig

        agent_upper = agent_name.upper()
        api_key = getattr(settings, f"{agent_upper}_API_KEY", "")
        model = getattr(settings, f"{agent_upper}_MODEL", "")
        base_url = getattr(settings, f"{agent_upper}_BASE_URL", "")

        provider = ProviderConfig(
            name=agent_name,
            api_key=api_key,
            model=model,
            base_url=base_url,
            priority=1,
        )

        provider_manager = ProviderManager(
            providers=[provider],
            rotation_strategy="round-robin",
        )

        return ManagedLLM(
            provider_manager=provider_manager,
            task_id=self.task_id,
            agent_name=agent_name,
        )

    @staticmethod
    def create_llm(api_key: str, model: str, base_url: str, task_id: str) -> LLM:
        """Create a single LLM instance with specified parameters"""
        return LLM(
            api_key=api_key,
            model=model,
            base_url=base_url,
            task_id=task_id,
        )
