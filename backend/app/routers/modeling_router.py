from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from app.core.workflow import MathModelWorkFlow
from app.schemas.enums import CompTemplate, FormatOutPut
from app.utils.log_util import logger
from app.services.redis_manager import redis_manager
from app.schemas.request import Problem
from app.schemas.response import SystemMessage
from app.utils.common_utils import (
    create_task_id,
    create_work_dir,
    get_current_files,
    md_2_docx,
)
from app.utils.file_utils import (
    is_archive_file,
    extract_archive,
    count_files_in_directory,
)
import os
import asyncio
from fastapi import HTTPException
from icecream import ic
from pydantic import BaseModel
import litellm
from app.config.setting import settings
import requests
from app.models.task_history import TaskHistoryItem, task_history_manager
from app.utils.config_loader import save_model_config
from typing import Any, Dict

router = APIRouter(prefix="/modeling", tags=["modeling"])


def _map_template_to_enum(template: str | None) -> CompTemplate:
    """将前端/测试中的模板字符串映射到枚举值。

    支持："国赛"/"CHINA"/"guosai" -> CHINA，"美赛"/"AMERICAN"/"meisai" -> AMERICAN。
    """

    if not template:
        return CompTemplate.CHINA

    value = template.strip().lower()
    if value in {"国赛", "china", "guosai"}:
        return CompTemplate.CHINA
    if value in {"美赛", "american", "meisai"}:
        return CompTemplate.AMERICAN
    return CompTemplate.CHINA


def _map_format_to_enum(fmt: str | None) -> FormatOutPut:
    """将前端/测试中的输出格式字符串映射到枚举值。

    支持："markdown" -> Markdown, "latex" -> LaTeX。
    """

    if not fmt:
        return FormatOutPut.Markdown

    value = fmt.strip().lower()
    if value in {"markdown", "md"}:
        return FormatOutPut.Markdown
    if value in {"latex", "tex"}:
        return FormatOutPut.LaTeX
    return FormatOutPut.Markdown


class ValidateApiKeyRequest(BaseModel):
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model_id: str


class ValidateOpenalexEmailRequest(BaseModel):
    email: str


class ValidateOpenalexEmailResponse(BaseModel):
    valid: bool
    message: str


class ValidateApiKeyResponse(BaseModel):
    valid: bool
    message: str


class SaveApiConfigRequest(BaseModel):
    coordinator: dict
    modeler: dict
    coder: dict
    writer: dict
    openalex_email: str


class ExampleModelingRequest(BaseModel):
    """兼容示例建模请求的多种字段格式。

    - 测试与前端：example_name/template/language/format_output
    - 旧结构：example_id/source
    """

    example_name: str | None = None
    template: str | None = None
    language: str | None = "zh"
    format_output: str | None = "markdown"

    example_id: str | None = None
    source: str | None = None


@router.post("/save-api-config")
async def save_api_config(payload: Dict[str, Any]):
    """保存验证成功的 API 配置到 settings，并写入 model_config.toml。

    兼容两种请求格式：
    - 扁平结构（测试用）：COORDINATOR_API_KEY、MODELER_MODEL 等
    - 嵌套结构：coordinator/modeler/coder/writer 字段中包含 apiKey/modelId/baseUrl
    """

    try:
        updates: Dict[str, Any] = {}

        # 兼容嵌套结构
        coordinator_cfg = payload.get("coordinator")
        modeler_cfg = payload.get("modeler")
        coder_cfg = payload.get("coder")
        writer_cfg = payload.get("writer")

        if isinstance(coordinator_cfg, dict):
            settings.COORDINATOR_API_KEY = coordinator_cfg.get("apiKey", "")
            settings.COORDINATOR_MODEL = coordinator_cfg.get("modelId", "")
            settings.COORDINATOR_BASE_URL = coordinator_cfg.get("baseUrl", "")
            updates.update(
                {
                    "COORDINATOR_API_KEY": settings.COORDINATOR_API_KEY,
                    "COORDINATOR_MODEL": settings.COORDINATOR_MODEL,
                    "COORDINATOR_BASE_URL": settings.COORDINATOR_BASE_URL,
                }
            )
        else:
            # 扁平结构
            if "COORDINATOR_API_KEY" in payload:
                settings.COORDINATOR_API_KEY = payload.get("COORDINATOR_API_KEY", "")
                updates["COORDINATOR_API_KEY"] = settings.COORDINATOR_API_KEY
            if "COORDINATOR_MODEL" in payload:
                settings.COORDINATOR_MODEL = payload.get("COORDINATOR_MODEL", "")
                updates["COORDINATOR_MODEL"] = settings.COORDINATOR_MODEL
            if "COORDINATOR_BASE_URL" in payload:
                settings.COORDINATOR_BASE_URL = payload.get("COORDINATOR_BASE_URL", "")
                updates["COORDINATOR_BASE_URL"] = settings.COORDINATOR_BASE_URL

        if isinstance(modeler_cfg, dict):
            settings.MODELER_API_KEY = modeler_cfg.get("apiKey", "")
            settings.MODELER_MODEL = modeler_cfg.get("modelId", "")
            settings.MODELER_BASE_URL = modeler_cfg.get("baseUrl", "")
            updates.update(
                {
                    "MODELER_API_KEY": settings.MODELER_API_KEY,
                    "MODELER_MODEL": settings.MODELER_MODEL,
                    "MODELER_BASE_URL": settings.MODELER_BASE_URL,
                }
            )
        else:
            if "MODELER_API_KEY" in payload:
                settings.MODELER_API_KEY = payload.get("MODELER_API_KEY", "")
                updates["MODELER_API_KEY"] = settings.MODELER_API_KEY
            if "MODELER_MODEL" in payload:
                settings.MODELER_MODEL = payload.get("MODELER_MODEL", "")
                updates["MODELER_MODEL"] = settings.MODELER_MODEL
            if "MODELER_BASE_URL" in payload:
                settings.MODELER_BASE_URL = payload.get("MODELER_BASE_URL", "")
                updates["MODELER_BASE_URL"] = settings.MODELER_BASE_URL

        if isinstance(coder_cfg, dict):
            settings.CODER_API_KEY = coder_cfg.get("apiKey", "")
            settings.CODER_MODEL = coder_cfg.get("modelId", "")
            settings.CODER_BASE_URL = coder_cfg.get("baseUrl", "")
            updates.update(
                {
                    "CODER_API_KEY": settings.CODER_API_KEY,
                    "CODER_MODEL": settings.CODER_MODEL,
                    "CODER_BASE_URL": settings.CODER_BASE_URL,
                }
            )
        else:
            if "CODER_API_KEY" in payload:
                settings.CODER_API_KEY = payload.get("CODER_API_KEY", "")
                updates["CODER_API_KEY"] = settings.CODER_API_KEY
            if "CODER_MODEL" in payload:
                settings.CODER_MODEL = payload.get("CODER_MODEL", "")
                updates["CODER_MODEL"] = settings.CODER_MODEL
            if "CODER_BASE_URL" in payload:
                settings.CODER_BASE_URL = payload.get("CODER_BASE_URL", "")
                updates["CODER_BASE_URL"] = settings.CODER_BASE_URL

        if isinstance(writer_cfg, dict):
            settings.WRITER_API_KEY = writer_cfg.get("apiKey", "")
            settings.WRITER_MODEL = writer_cfg.get("modelId", "")
            settings.WRITER_BASE_URL = writer_cfg.get("baseUrl", "")
            updates.update(
                {
                    "WRITER_API_KEY": settings.WRITER_API_KEY,
                    "WRITER_MODEL": settings.WRITER_MODEL,
                    "WRITER_BASE_URL": settings.WRITER_BASE_URL,
                }
            )
        else:
            if "WRITER_API_KEY" in payload:
                settings.WRITER_API_KEY = payload.get("WRITER_API_KEY", "")
                updates["WRITER_API_KEY"] = settings.WRITER_API_KEY
            if "WRITER_MODEL" in payload:
                settings.WRITER_MODEL = payload.get("WRITER_MODEL", "")
                updates["WRITER_MODEL"] = settings.WRITER_MODEL
            if "WRITER_BASE_URL" in payload:
                settings.WRITER_BASE_URL = payload.get("WRITER_BASE_URL", "")
                updates["WRITER_BASE_URL"] = settings.WRITER_BASE_URL

        openalex_email = payload.get("openalex_email") or payload.get("OPENALEX_EMAIL")
        if openalex_email:
            settings.OPENALEX_EMAIL = openalex_email
            updates["OPENALEX_EMAIL"] = openalex_email

        if updates:
            save_model_config(updates)

        return {"success": True, "message": "API configuration saved successfully"}
    except Exception as e:  # pragma: no cover - 错误路径
        logger.error(f"保存配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@router.post("/validate-api-key", response_model=ValidateApiKeyResponse)
async def validate_api_key(request: ValidateApiKeyRequest):
    """
    验证 API Key 的有效性
    """
    try:
        # 使用 litellm 发送测试请求
        await litellm.acompletion(
            model=request.model_id,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=1,
            api_key=request.api_key,
            base_url=request.base_url
            if request.base_url != "https://api.openai.com/v1"
            else None,
        )

        return ValidateApiKeyResponse(valid=True, message="✓ 模型 API 验证成功")
    except Exception as e:
        error_msg = str(e)

        # 解析不同类型的错误
        if "401" in error_msg or "Unauthorized" in error_msg:
            return ValidateApiKeyResponse(valid=False, message="✗ API Key 无效或已过期")
        elif "404" in error_msg or "Not Found" in error_msg:
            return ValidateApiKeyResponse(
                valid=False, message="✗ 模型 ID 不存在或 Base URL 错误"
            )
        elif "429" in error_msg or "rate limit" in error_msg.lower():
            return ValidateApiKeyResponse(
                valid=False, message="✗ 请求过于频繁，请稍后再试"
            )
        elif "403" in error_msg or "Forbidden" in error_msg:
            return ValidateApiKeyResponse(
                valid=False, message="✗ API 权限不足或账户余额不足"
            )
        else:
            return ValidateApiKeyResponse(
                valid=False, message=f"✗ 验证失败: {error_msg[:50]}..."
            )


@router.post("/validate-openalex-email", response_model=ValidateOpenalexEmailResponse)
async def validate_openalex_email(request: ValidateOpenalexEmailRequest):
    """
    验证 OpenAlex Email 的有效性
    """
    try:
        response = requests.get(
            f"https://api.openalex.org/works?mailto={request.email}",
            timeout=10,
        )
        logger.debug(f"OpenAlex Email 验证响应: {response}")
        response.raise_for_status()
        return ValidateOpenalexEmailResponse(
            valid=True, message="✓ OpenAlex Email 验证成功"
        )
    except Exception as e:
        return ValidateOpenalexEmailResponse(
            valid=False, message=f"✗ OpenAlex Email 验证失败: {str(e)}"
        )


@router.post("/example")
async def exampleModeling(
    example_request: ExampleModelingRequest,
    background_tasks: BackgroundTasks,
):
    task_id = create_task_id()
    work_dir = create_work_dir(task_id)

    # 统一 example 名称与来源目录
    example_name = example_request.example_name or example_request.example_id
    source = example_request.source

    if not source:
        # 根据示例名称简单推断来源目录，默认使用 2024 高教杯示例
        if example_name and "2023" in example_name:
            source = "2023华数杯C题"
        elif example_name and "2025" in example_name:
            source = "2025五一杯C题"
        else:
            source = "2024高教杯C题"

    example_dir = os.path.join("app", "example", "example", source)
    ic(example_dir)
    with open(os.path.join(example_dir, "questions.txt"), "r", encoding="utf-8") as f:
        ques_all = f.read()

    current_files = get_current_files(example_dir, "data")
    for file in current_files:
        src_file = os.path.join(example_dir, file)
        dst_file = os.path.join(work_dir, file)
        with open(src_file, "rb") as src, open(dst_file, "wb") as dst:
            dst.write(src.read())

    # 创建任务历史记录
    title = ques_all[:50].strip() + "..." if len(ques_all) > 50 else ques_all.strip()
    task_history = TaskHistoryItem(
        task_id=task_id,
        title=title,
        description=ques_all[:200].strip() + "..."
        if len(ques_all) > 200
        else ques_all.strip(),
        task_type="example",
        comp_template=CompTemplate.CHINA,
        status="processing",
        file_count=len(current_files),
    )
    task_history_manager.add_task(task_history)

    # 存储任务ID和状态
    await redis_manager.set(f"task_id:{task_id}", task_id)
    await redis_manager.set(f"task:{task_id}:status", "pending")

    logger.info(f"Adding background task for task_id: {task_id}")
    # 将任务添加到后台执行
    background_tasks.add_task(
        run_modeling_task_async,
        task_id,
        ques_all,
        CompTemplate.CHINA,
        FormatOutPut.Markdown,
    )
    return {"task_id": task_id, "status": "processing"}


@router.post("")
async def modeling(
    background_tasks: BackgroundTasks,
    problem: str | None = Form(default=None),
    template: str | None = Form(default=None),
    language: str | None = Form(default="zh"),
    format_output: str | None = Form(default="markdown"),
    files: list[UploadFile] = File(default=None),
):
    """建模主入口，与测试使用的 /modeling 表单字段保持兼容。

    - problem: 问题描述（必填）
    - template: 比赛模板（"国赛"/"美赛" 等）
    - language: 语言（"zh"/"en"/"auto"）
    - format_output: 输出格式（"markdown"/"latex" 等）
    """

    if not problem:
        # 与测试期望一致：缺少 problem 时返回 422
        raise HTTPException(status_code=422, detail="Problem description is required")

    task_id = create_task_id()
    work_dir = create_work_dir(task_id)

    ques_all = problem
    comp_template = _map_template_to_enum(template)
    format_enum = _map_format_to_enum(format_output)

    file_count = 0
    archive_files = []  # 记录压缩包文件

    # 如果有上传文件，保存文件
    if files:
        logger.info(f"开始处理上传的文件，工作目录: {work_dir}")
        for file in files:
            try:
                # 确保文件名不为空
                if not file.filename:
                    logger.warning("跳过空文件名")
                    continue

                content = await file.read()
                if not content:
                    logger.warning(f"文件 {file.filename} 内容为空")
                    continue

                # 处理文件路径（支持文件夹结构）
                # 如果文件名包含路径分隔符，创建对应的目录结构
                file_path_parts = file.filename.replace("\\", "/").split("/")
                if len(file_path_parts) > 1:
                    # 有子目录
                    sub_dir = os.path.join(work_dir, *file_path_parts[:-1])
                    os.makedirs(sub_dir, exist_ok=True)
                    data_file_path = os.path.join(work_dir, *file_path_parts)
                else:
                    # 直接在工作目录下
                    data_file_path = os.path.join(work_dir, file.filename)

                logger.info(f"保存文件: {file.filename} -> {data_file_path}")

                # 保存文件
                with open(data_file_path, "wb") as f:
                    f.write(content)
                logger.info(f"成功保存文件: {data_file_path}")

                # 检查是否为压缩包
                if is_archive_file(file.filename):
                    logger.info(f"检测到压缩包: {file.filename}")
                    archive_files.append(data_file_path)
                else:
                    file_count += 1

            except Exception as e:
                logger.error(f"保存文件 {file.filename} 失败: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"保存文件 {file.filename} 失败: {str(e)}"
                )

        # 处理压缩包
        if archive_files:
            logger.info(f"开始解压 {len(archive_files)} 个压缩包")
            for archive_path in archive_files:
                success, error_msg, extracted_files = extract_archive(
                    archive_path, work_dir
                )

                if success:
                    logger.info(
                        f"成功解压 {archive_path}: {len(extracted_files)} 个文件"
                    )
                    file_count += len(extracted_files)

                    # 删除原始压缩包（可选）
                    try:
                        os.remove(archive_path)
                        logger.info(f"已删除原始压缩包: {archive_path}")
                    except Exception as e:
                        logger.warning(f"删除压缩包失败: {str(e)}")
                else:
                    logger.error(f"解压失败 {archive_path}: {error_msg}")
                    # 如果解压失败，至少保留压缩包本身
                    file_count += 1

        # 如果没有压缩包，统计实际文件数
        if not archive_files and file_count == 0:
            file_count = count_files_in_directory(work_dir)

        logger.info(f"文件处理完成，共 {file_count} 个文件")
    else:
        logger.warning("没有上传文件")

    # 创建任务历史记录
    title = ques_all[:50].strip() + "..." if len(ques_all) > 50 else ques_all.strip()
    task_history = TaskHistoryItem(
        task_id=task_id,
        title=title,
        description=ques_all[:200].strip() + "..."
        if len(ques_all) > 200
        else ques_all.strip(),
        task_type="custom",
        comp_template=comp_template,
        status="processing",
        file_count=file_count,
    )
    task_history_manager.add_task(task_history)

    # 存储任务ID和状态
    await redis_manager.set(f"task_id:{task_id}", task_id)
    await redis_manager.set(f"task:{task_id}:status", "pending")

    logger.info(f"Adding background task for task_id: {task_id}")
    # 将任务添加到后台执行
    background_tasks.add_task(
        run_modeling_task_async, task_id, ques_all, comp_template, format_enum
    )
    return {"task_id": task_id, "status": "processing"}


async def run_modeling_task_async(
    task_id: str,
    ques_all: str,
    comp_template: CompTemplate,
    format_output: FormatOutPut,
):
    logger.info(f"run modeling task for task_id: {task_id}")

    problem = Problem(
        task_id=task_id,
        ques_all=ques_all,
        comp_template=comp_template,
        format_output=format_output,
    )

    try:
        # 更新任务状态为运行中
        await redis_manager.set(f"task:{task_id}:status", "running")

        # 发送任务开始状态
        await redis_manager.publish_message(
            task_id,
            SystemMessage(content="任务开始处理"),
        )

        # 给一个短暂的延迟，确保 WebSocket 有机会连接
        await asyncio.sleep(1)

        # 创建任务并等待它完成
        task = asyncio.create_task(MathModelWorkFlow().execute(problem))
        # 设置超时时间（比如 5 小时）
        await asyncio.wait_for(task, timeout=3600 * 5)

        # 更新任务状态为完成
        await redis_manager.set(f"task:{task_id}:status", "completed")

        # 发送任务完成状态
        await redis_manager.publish_message(
            task_id,
            SystemMessage(content="任务处理完成", type="success"),
        )
        # 转换md为docx
        md_2_docx(task_id)

        # 更新任务历史状态为完成
        task_history_manager.update_task(task_id, status="completed")

    except asyncio.TimeoutError:
        error_msg = "任务执行超时（超过5小时）"
        logger.error(f"Task {task_id} timeout: {error_msg}")
        # 更新任务状态为失败
        await redis_manager.set(f"task:{task_id}:status", "failed")
        await redis_manager.publish_message(
            task_id,
            SystemMessage(content=error_msg, type="error"),
        )
        # 更新任务历史状态为失败
        task_history_manager.update_task(task_id, status="failed")
    except Exception as e:
        error_msg = f"任务执行过程中发生错误: {str(e)}"
        logger.error(f"Task {task_id} failed: {error_msg}")
        # 更新任务状态为失败
        await redis_manager.set(f"task:{task_id}:status", "failed")
        await redis_manager.publish_message(
            task_id,
            SystemMessage(content=error_msg, type="error"),
        )
        # 更新任务历史状态为失败
        task_history_manager.update_task(task_id, status="failed")
    finally:
        logger.info(f"Task {task_id} completed or failed, cleaning up...")
