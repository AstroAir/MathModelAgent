import pytest

from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchProvider,
    SearchProviderStatus,
)


@pytest.mark.asyncio
async def test_web_search_success(async_client, monkeypatch):
    from app.routers import search_router

    async def fake_search(request: SearchRequest):  # type: ignore[override]
        return SearchResponse(
            results=[
                SearchResult(
                    title="Test Result",
                    url="https://example.com",
                    content="content",
                )
            ],
            query=request.query,
            provider=SearchProvider.TAVILY,
            search_time=0.1,
        )

    monkeypatch.setattr(search_router.search_manager, "search", fake_search)

    payload = {"query": "test", "search_type": "general"}
    resp = await async_client.post("/search/web", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "test"
    assert data["provider"] == "tavily"
    assert len(data["results"]) == 1


@pytest.mark.asyncio
async def test_web_search_error(async_client, monkeypatch):
    from app.routers import search_router
    from app.schemas.search import SearchError

    async def fake_search(request):  # type: ignore[override]
        raise SearchError("boom", provider="tavily", error_code="API_ERROR")

    monkeypatch.setattr(search_router.search_manager, "search", fake_search)

    payload = {"query": "test", "search_type": "general"}
    resp = await async_client.post("/search/web", json=payload)
    assert resp.status_code == 400
    data = resp.json()
    assert data["detail"]["error_code"] == "API_ERROR"


@pytest.mark.asyncio
async def test_get_content(async_client, monkeypatch):
    from app.routers import search_router

    async def fake_get_content(urls):  # type: ignore[override]
        return {u: "content" for u in urls}

    monkeypatch.setattr(search_router.search_manager, "get_content", fake_get_content)

    resp = await async_client.post("/search/content", json={"urls": ["https://a"]})
    assert resp.status_code == 200
    assert resp.json()["https://a"] == "content"


@pytest.mark.asyncio
async def test_find_similar(async_client, monkeypatch):
    from app.routers import search_router

    async def fake_similar(url, num_results):  # type: ignore[override]
        return [
            SearchResult(title="t", url=url, content="c"),
        ]

    monkeypatch.setattr(search_router.search_manager, "find_similar", fake_similar)

    resp = await async_client.post(
        "/search/similar", json={"url": "https://a", "num_results": 1}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list) and body[0]["url"] == "https://a"


@pytest.mark.asyncio
async def test_search_settings_and_status(async_client, monkeypatch):
    from app.routers import search_router

    async def fake_status(provider=None):  # type: ignore[override]
        if provider is None:
            return {
                SearchProvider.TAVILY: SearchProviderStatus(
                    provider=SearchProvider.TAVILY,
                    available=True,
                    configured=True,
                    last_error=None,
                )
            }
        return SearchProviderStatus(
            provider=provider,
            available=True,
            configured=True,
            last_error=None,
        )

    monkeypatch.setattr(
        search_router.search_manager, "get_provider_status", fake_status
    )
    monkeypatch.setattr(
        search_router.search_manager,
        "get_available_providers",
        lambda: [SearchProvider.TAVILY],
    )

    resp = await async_client.get("/search/status")
    assert resp.status_code == 200

    resp = await async_client.get("/search/providers")
    assert resp.status_code == 200
    assert resp.json() == ["tavily"]

    resp = await async_client.get("/search/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert "default_provider" in data


@pytest.mark.asyncio
async def test_search_test_and_health(async_client, monkeypatch):
    from app.routers import search_router

    def fake_is_provider_available(provider):  # type: ignore[override]
        return True

    async def fake_status(provider=None):  # type: ignore[override]
        return SearchProviderStatus(
            provider=SearchProvider.TAVILY,
            available=True,
            configured=True,
            last_error=None,
        )

    monkeypatch.setattr(
        search_router.search_manager,
        "is_provider_available",
        fake_is_provider_available,
    )
    monkeypatch.setattr(
        search_router.search_manager, "get_provider_status", fake_status
    )
    monkeypatch.setattr(
        search_router.search_manager,
        "get_available_providers",
        lambda: [SearchProvider.TAVILY],
    )

    resp = await async_client.post("/search/test", json={"provider": "tavily"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True

    # health
    async def fake_statuses(provider=None):  # type: ignore[override]
        return {
            SearchProvider.TAVILY: SearchProviderStatus(
                provider=SearchProvider.TAVILY,
                available=True,
                configured=True,
                last_error=None,
            )
        }

    monkeypatch.setattr(
        search_router.search_manager, "get_provider_status", fake_statuses
    )
    resp = await async_client.get("/search/health")
    assert resp.status_code == 200
    assert resp.json()["healthy"] is True
