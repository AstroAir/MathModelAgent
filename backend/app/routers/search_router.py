from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchProvider,
    SearchError,
)
from app.tools.search.search_manager import search_manager
from app.config.setting import settings
from app.utils.log_util import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/web", response_model=SearchResponse)
async def perform_web_search(request: SearchRequest):
    """
    Perform a web search using configured providers
    """
    try:
        response = await search_manager.search(request)
        return response
    except SearchError as e:
        logger.error(f"Search error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": e.message,
                "provider": e.provider,
                "error_code": e.error_code,
            },
        )
    except Exception as e:
        logger.error(f"Unexpected search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal search error", "error": str(e)},
        )


@router.post("/content", response_model=Dict[str, str])
async def get_web_content(request: Dict[str, List[str]]):
    """
    Get content for specific URLs (Exa provider only)
    """
    try:
        urls = request.get("urls", [])
        if not urls:
            raise HTTPException(status_code=400, detail="URLs list is required")

        content_map = await search_manager.get_content(urls)
        return content_map
    except SearchError as e:
        logger.error(f"Content retrieval error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": e.message,
                "provider": e.provider,
                "error_code": e.error_code,
            },
        )
    except Exception as e:
        logger.error(f"Unexpected content retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal content retrieval error", "error": str(e)},
        )


@router.post("/similar", response_model=List[SearchResult])
async def find_similar_pages(request: Dict[str, Any]):
    """
    Find similar pages to a given URL (Exa provider only)
    """
    try:
        url = request.get("url")
        num_results = request.get("num_results", 10)

        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        similar_results = await search_manager.find_similar(url, num_results)
        return similar_results
    except SearchError as e:
        logger.error(f"Similar search error: {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": e.message,
                "provider": e.provider,
                "error_code": e.error_code,
            },
        )
    except Exception as e:
        logger.error(f"Unexpected similar search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Internal similar search error", "error": str(e)},
        )


@router.get("/status")
async def get_search_provider_status(provider: Optional[SearchProvider] = None):
    """
    Get status of search providers
    """
    try:
        status = await search_manager.get_provider_status(provider)
        return status
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to get provider status", "error": str(e)},
        )


@router.get("/providers", response_model=List[SearchProvider])
async def get_available_providers():
    """
    Get list of available search providers
    """
    try:
        providers = search_manager.get_available_providers()
        return providers
    except Exception as e:
        logger.error(f"Provider list error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to get available providers", "error": str(e)},
        )


@router.get("/settings")
async def get_search_settings():
    """
    Get current search settings
    """
    try:
        return {
            "default_provider": settings.SEARCH_DEFAULT_PROVIDER,
            "max_results": settings.SEARCH_MAX_RESULTS,
            "timeout": settings.SEARCH_TIMEOUT,
            "enable_fallback": settings.SEARCH_ENABLE_FALLBACK,
            "fallback_providers": settings.SEARCH_FALLBACK_PROVIDERS,
        }
    except Exception as e:
        logger.error(f"Settings retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to get search settings", "error": str(e)},
        )


@router.put("/settings")
async def update_search_settings(settings_update: Dict[str, Any]):
    """
    Update search settings (Note: This would typically require admin permissions)
    """
    try:
        # In a real implementation, you'd want to validate and persist these settings
        # For now, we'll just return the current settings
        logger.info(f"Search settings update requested: {settings_update}")

        # This is a placeholder - in production you'd want to:
        # 1. Validate the settings
        # 2. Update the configuration
        # 3. Restart or reconfigure the search manager

        return {
            "message": "Settings update received",
            "note": "Settings updates require application restart to take effect",
        }
    except Exception as e:
        logger.error(f"Settings update error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to update search settings", "error": str(e)},
        )


@router.post("/test")
async def test_search_provider(request: Dict[str, SearchProvider]):
    """
    Test connectivity to a specific search provider
    """
    try:
        provider = request.get("provider")
        if not provider:
            raise HTTPException(status_code=400, detail="Provider is required")

        if not search_manager.is_provider_available(provider):
            return {
                "success": False,
                "message": f"Provider {provider.value} is not configured or available",
            }

        # Get provider status as a connectivity test
        status = await search_manager.get_provider_status(provider)

        return {
            "success": status.available,
            "message": f"Provider {provider.value} is {'available' if status.available else 'unavailable'}",
            "response_time": status.response_time,
            "configured": status.configured,
            "last_error": status.last_error,
        }
    except Exception as e:
        logger.error(f"Provider test error: {str(e)}")
        return {"success": False, "message": f"Failed to test provider: {str(e)}"}


@router.get("/health")
async def search_health_check():
    """
    Overall search system health check
    """
    try:
        providers = search_manager.get_available_providers()
        statuses = await search_manager.get_provider_status()

        healthy_providers = []
        unhealthy_providers = []

        if isinstance(statuses, dict):
            for provider, status in statuses.items():
                if status.available and status.configured:
                    healthy_providers.append(provider.value)
                else:
                    unhealthy_providers.append(
                        {
                            "provider": provider.value,
                            "error": status.last_error or "Not configured",
                        }
                    )

        overall_health = len(healthy_providers) > 0

        return {
            "healthy": overall_health,
            "total_providers": len(providers),
            "healthy_providers": healthy_providers,
            "unhealthy_providers": unhealthy_providers,
            "message": f"Search system is {'healthy' if overall_health else 'unhealthy'}",
        }
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {"healthy": False, "message": f"Health check failed: {str(e)}"}
