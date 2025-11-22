"""
配置加载器

支持从 model_config.toml 加载多提供商和多 API Key 配置
"""

import toml
from pathlib import Path
from typing import Dict, List, Optional, Any
from app.utils.provider_manager import ProviderConfig, RotationStrategy
from app.utils.log_util import logger


class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path: str = "backend/app/config/model_config.toml"):
        # 尝试多个可能的路径
        possible_paths = [
            Path(config_path),
            Path("app/config/model_config.toml"),
            Path("backend/app/config/model_config.toml"),
        ]

        self.config_path = None
        for path in possible_paths:
            if path.exists():
                self.config_path = path
                break

        if self.config_path is None:
            self.config_path = possible_paths[0]  # 使用默认路径

        self.config_data = self._load_config()
        self.current_config_name = self._get_current_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return toml.load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return {}

    def _get_current_config(self) -> str:
        """获取当前使用的配置名称"""
        return self.config_data.get("current", {}).get("current", "config1")

    def get_agent_providers(self, agent_name: str) -> List[ProviderConfig]:
        """
        获取指定 Agent 的提供商配置列表

        Args:
            agent_name: Agent 名称（coordinator, modeler, coder, writer）

        Returns:
            List[ProviderConfig]: 提供商配置列表
        """
        agent_name = agent_name.upper()
        current_config = self.config_data.get(self.current_config_name, {})

        providers = []

        # 检查是否有新格式的配置（providers 数组）
        providers_key = f"{agent_name}_PROVIDERS"
        if providers_key in current_config:
            providers_data = current_config[providers_key]
            if isinstance(providers_data, list):
                for idx, provider_data in enumerate(providers_data):
                    provider = self._parse_provider_dict(provider_data, agent_name, idx)
                    if provider:
                        providers.append(provider)

        # 检查是否有多 API Key 配置
        elif f"{agent_name}_API_KEYS" in current_config:
            providers = self._parse_multi_key_config(agent_name, current_config)

        # 回退到单一配置格式
        elif f"{agent_name}_API_KEY" in current_config:
            provider = self._parse_single_config(agent_name, current_config)
            if provider:
                providers.append(provider)

        return providers

    def _parse_provider_dict(
        self,
        provider_data: Dict[str, Any],
        agent_name: str,
        index: int,
    ) -> Optional[ProviderConfig]:
        """解析提供商字典配置"""
        try:
            return ProviderConfig(
                name=provider_data.get("name", f"{agent_name.lower()}_{index}"),
                api_key=provider_data.get("api_key", ""),
                model=provider_data.get("model", ""),
                base_url=provider_data.get("base_url", ""),
                priority=provider_data.get("priority", index + 1),
                rpm=provider_data.get("rpm"),
                tpm=provider_data.get("tpm"),
                rpd=provider_data.get("rpd"),
                enabled=provider_data.get("enabled", True),
            )
        except Exception as e:
            logger.error(f"Failed to parse provider config: {e}")
            return None

    def _parse_multi_key_config(
        self,
        agent_name: str,
        config: Dict[str, Any],
    ) -> List[ProviderConfig]:
        """解析多 API Key 配置格式"""
        providers = []

        api_keys = config.get(f"{agent_name}_API_KEYS", [])
        models = config.get(f"{agent_name}_MODELS", [])
        base_urls = config.get(f"{agent_name}_BASE_URLS", [])
        rpms = config.get(f"{agent_name}_RPMS", [])
        tpms = config.get(f"{agent_name}_TPMS", [])
        rpds = config.get(f"{agent_name}_RPDS", [])

        # 确保是列表
        if not isinstance(api_keys, list):
            api_keys = [api_keys]
        if not isinstance(models, list):
            models = [models] * len(api_keys)
        if not isinstance(base_urls, list):
            base_urls = [base_urls] * len(api_keys)
        if not isinstance(rpms, list):
            rpms = [rpms] * len(api_keys) if rpms else [None] * len(api_keys)
        if not isinstance(tpms, list):
            tpms = [tpms] * len(api_keys) if tpms else [None] * len(api_keys)
        if not isinstance(rpds, list):
            rpds = [rpds] * len(api_keys) if rpds else [None] * len(api_keys)

        for idx, api_key in enumerate(api_keys):
            if not api_key:
                continue

            provider = ProviderConfig(
                name=f"{agent_name.lower()}_{idx}",
                api_key=api_key,
                model=models[idx] if idx < len(models) else models[0],
                base_url=base_urls[idx] if idx < len(base_urls) else base_urls[0],
                priority=idx + 1,
                rpm=rpms[idx] if idx < len(rpms) else None,
                tpm=tpms[idx] if idx < len(tpms) else None,
                rpd=rpds[idx] if idx < len(rpds) else None,
            )
            providers.append(provider)

        return providers

    def _parse_single_config(
        self,
        agent_name: str,
        config: Dict[str, Any],
    ) -> Optional[ProviderConfig]:
        """解析单一配置格式"""
        api_key = config.get(f"{agent_name}_API_KEY")
        model = config.get(f"{agent_name}_MODEL")
        base_url = config.get(f"{agent_name}_BASE_URL")

        if not api_key or not model:
            return None

        return ProviderConfig(
            name=agent_name.lower(),
            api_key=api_key,
            model=model,
            base_url=base_url or "",
            priority=1,
            rpm=config.get(f"{agent_name}_RPM"),
            tpm=config.get(f"{agent_name}_TPM"),
            rpd=config.get(f"{agent_name}_RPD"),
        )

    def get_rotation_strategy(self, agent_name: str) -> RotationStrategy:
        """获取轮询策略"""
        agent_name = agent_name.upper()
        current_config = self.config_data.get(self.current_config_name, {})

        strategy_str = current_config.get(
            f"{agent_name}_ROTATION_STRATEGY", "round-robin"
        )

        try:
            return RotationStrategy(strategy_str.lower())
        except ValueError:
            logger.warning(
                f"Invalid rotation strategy '{strategy_str}', using round-robin"
            )
            return RotationStrategy.ROUND_ROBIN

    def get_retry_config(self, agent_name: str) -> Dict[str, Any]:
        """获取重试配置"""
        agent_name = agent_name.upper()
        current_config = self.config_data.get(self.current_config_name, {})

        return {
            "auto_retry": current_config.get(f"{agent_name}_AUTO_RETRY", True),
            "max_retries": current_config.get(f"{agent_name}_MAX_RETRIES", 3),
            "retry_delay": current_config.get(f"{agent_name}_RETRY_DELAY", 1.0),
        }

    def reload(self):
        """重新加载配置"""
        self.config_data = self._load_config()
        self.current_config_name = self._get_current_config()
        logger.info(f"Config reloaded, current config: {self.current_config_name}")


# 全局配置加载器实例
config_loader = ConfigLoader()


def save_model_config(updates: Dict[str, Any], section: str = "config1") -> None:
    """保存模型相关配置到 TOML 文件。

    仅在给定 section 下更新传入的键，不会删除其他已有配置。
    """

    try:
        # 使用全局 config_loader 的配置数据和路径
        data: Dict[str, Any] = config_loader.config_data or {}

        if section not in data:
            data[section] = {}

        section_data = data.setdefault(section, {})
        for key, value in updates.items():
            section_data[key] = value

        # 写回到配置文件
        with open(config_loader.config_path, "w", encoding="utf-8") as f:  # type: ignore[arg-type]
            toml.dump(data, f)

        # 重新加载内存中的配置
        config_loader.reload()
        logger.info(
            "Model config saved to %s with keys: %s",
            config_loader.config_path,
            ", ".join(updates.keys()),
        )
    except Exception as exc:  # pragma: no cover - 日志和异常路径
        logger.error(f"Failed to save model config: {exc}")
        raise
