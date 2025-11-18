"""
速率限制和提供商管理 API 路由
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.utils.config_loader import config_loader
from app.utils.provider_manager import ProviderManager
from app.utils.log_util import logger

router = APIRouter(prefix="/api/rate-limit", tags=["rate-limit"])


@router.get("/stats/{agent_name}")
async def get_agent_rate_limit_stats(agent_name: str) -> Dict[str, Any]:
    """
    获取指定 Agent 的速率限制统计信息

    Args:
        agent_name: Agent 名称（coordinator, modeler, coder, writer）

    Returns:
        速率限制统计信息
    """
    try:
        # 加载提供商配置
        providers = config_loader.get_agent_providers(agent_name)

        if not providers:
            return {
                "agent_name": agent_name,
                "providers": [],
                "message": "No providers configured",
            }

        # 创建临时的提供商管理器来获取统计信息
        rotation_strategy = config_loader.get_rotation_strategy(agent_name)
        provider_manager = ProviderManager(
            providers=providers,
            rotation_strategy=rotation_strategy,
        )

        stats = await provider_manager.get_all_stats()

        return {
            "agent_name": agent_name,
            "rotation_strategy": rotation_strategy.value,
            "providers": stats,
        }

    except Exception as e:
        logger.error(f"Failed to get rate limit stats for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_all_rate_limit_stats() -> Dict[str, Any]:
    """
    获取所有 Agent 的速率限制统计信息

    Returns:
        所有 Agent 的速率限制统计信息
    """
    try:
        agents = ["coordinator", "modeler", "coder", "writer"]
        all_stats = {}

        for agent_name in agents:
            try:
                providers = config_loader.get_agent_providers(agent_name)

                if not providers:
                    all_stats[agent_name] = {
                        "providers": [],
                        "message": "No providers configured",
                    }
                    continue

                rotation_strategy = config_loader.get_rotation_strategy(agent_name)
                provider_manager = ProviderManager(
                    providers=providers,
                    rotation_strategy=rotation_strategy,
                )

                stats = await provider_manager.get_all_stats()

                all_stats[agent_name] = {
                    "rotation_strategy": rotation_strategy.value,
                    "providers": stats,
                }

            except Exception as e:
                logger.error(f"Failed to get stats for {agent_name}: {e}")
                all_stats[agent_name] = {"error": str(e)}

        return all_stats

    except Exception as e:
        logger.error(f"Failed to get all rate limit stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload-config")
async def reload_config() -> Dict[str, str]:
    """
    重新加载配置文件

    Returns:
        操作结果
    """
    try:
        config_loader.reload()
        return {
            "status": "success",
            "message": "Configuration reloaded successfully",
            "current_config": config_loader.current_config_name,
        }
    except Exception as e:
        logger.error(f"Failed to reload config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/{agent_name}")
async def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """
    获取指定 Agent 的配置信息

    Args:
        agent_name: Agent 名称（coordinator, modeler, coder, writer）

    Returns:
        Agent 配置信息
    """
    try:
        providers = config_loader.get_agent_providers(agent_name)
        rotation_strategy = config_loader.get_rotation_strategy(agent_name)
        retry_config = config_loader.get_retry_config(agent_name)

        # 隐藏敏感信息（API Key）
        safe_providers = []
        for provider in providers:
            safe_provider = {
                "name": provider.name,
                "model": provider.model,
                "base_url": provider.base_url,
                "priority": provider.priority,
                "rpm": provider.rpm,
                "tpm": provider.tpm,
                "rpd": provider.rpd,
                "enabled": provider.enabled,
                "api_key_preview": f"{provider.api_key[:8]}..."
                if provider.api_key
                else None,
            }
            safe_providers.append(safe_provider)

        return {
            "agent_name": agent_name,
            "rotation_strategy": rotation_strategy.value,
            "retry_config": retry_config,
            "providers": safe_providers,
        }

    except Exception as e:
        logger.error(f"Failed to get config for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
