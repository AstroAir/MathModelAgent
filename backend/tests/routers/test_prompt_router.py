import pytest


class DummyMessage:
    def __init__(self, content: str):
        self.content = content


class DummyChoice:
    def __init__(self, content: str):
        self.message = DummyMessage(content)


class DummyResponse:
    def __init__(self, content: str):
        self.choices = [DummyChoice(content)]


@pytest.mark.asyncio
async def test_optimize_prompt_success(async_client, monkeypatch):
    """Prompt optimization should return optimized_prompt using mocked LLM."""
    from app.routers import prompt_router

    async def fake_chat(self, history):  # type: ignore[override]
        # echo last user message content as optimized prompt
        last = history[-1]["content"]
        return DummyResponse(f"optimized: {last[:20]}")

    # Patch LLMFactory.create_llm to return object with chat method
    class DummyLLM:
        async def chat(self, history, **kwargs):  # type: ignore[override]
            return await fake_chat(self, history)

    monkeypatch.setattr(
        prompt_router.LLMFactory,
        "create_llm",
        lambda api_key, model, base_url, task_id: DummyLLM(),  # type: ignore[arg-type]
    )

    payload = {"original_prompt": "write a proof", "context": {"level": "easy"}}
    resp = await async_client.post("/api/prompt/optimize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["optimized_prompt"].startswith("optimized:")


@pytest.mark.asyncio
async def test_optimize_prompt_error(async_client, monkeypatch):
    from app.routers import prompt_router

    class FailingLLM:
        async def chat(self, *_, **__):  # type: ignore[override]
            raise RuntimeError("LLM failure")

    monkeypatch.setattr(
        prompt_router.LLMFactory, "create_llm", lambda *_, **__: FailingLLM()
    )

    payload = {"original_prompt": "write a proof", "context": {}}
    resp = await async_client.post("/api/prompt/optimize", json=payload)
    assert resp.status_code == 500
