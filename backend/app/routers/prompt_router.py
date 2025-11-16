from fastapi import APIRouter, HTTPException
from app.schemas.request import PromptOptimizeRequest
from app.schemas.response import PromptOptimizeResponse
from app.core.llm.llm_factory import LLMFactory
from app.config.setting import settings
from app.utils.log_util import logger
import json

router = APIRouter()


@router.post("/api/prompt/optimize", response_model=PromptOptimizeResponse)
async def optimize_prompt(request: PromptOptimizeRequest):
    try:
        # Create LLM instance for prompt optimization
        llm = LLMFactory.create_llm(
            api_key=settings.COORDINATOR_API_KEY,
            model=settings.COORDINATOR_MODEL,
            base_url=settings.COORDINATOR_BASE_URL,
            task_id="prompt_optimization",
        )

        # Construct the optimization prompt
        system_prompt = """You are an expert prompt engineer. Your task is to optimize user prompts to make them clearer, more specific, and more effective for AI assistance.

Given an original prompt and context information, improve the prompt by:
1. Adding clarity and specificity
2. Including relevant context where helpful
3. Structuring the request logically
4. Removing ambiguity
5. Making the intent clearer

Return only the optimized prompt without any additional explanation."""

        context_str = json.dumps(request.context, indent=2, ensure_ascii=False)

        user_prompt = f"""Original prompt: "{request.original_prompt}"

Context information:
{context_str}

Please optimize this prompt to be clearer and more effective."""

        history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # Get optimized prompt from LLM
        response = await llm.chat(history=history)
        optimized_content = response.choices[0].message.content.strip()

        logger.info(
            f"Prompt optimization completed: {request.original_prompt[:50]}... -> {optimized_content[:50]}..."
        )

        return PromptOptimizeResponse(optimized_prompt=optimized_content)

    except Exception as e:
        logger.error(f"Prompt optimization failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Prompt optimization failed: {str(e)}"
        )
