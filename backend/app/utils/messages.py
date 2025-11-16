"""Bilingual system messages for workflow"""


def get_message(key: str, language: str = "zh", **kwargs) -> str:
    """Get bilingual system message

    Args:
        key: Message key
        language: Language code ("zh" or "en")
        **kwargs: Format parameters

    Returns:
        Formatted message in specified language
    """
    messages = {
        "zh": {
            "coordinator_start": "识别用户意图和拆解问题ing...",
            "coordinator_complete": "识别用户意图和拆解问题完成,任务转交给建模手",
            "modeler_start": "建模手开始建模ing...",
            "creating_sandbox": "正在创建代码沙盒环境",
            "sandbox_created": "创建完成",
            "init_coder": "初始化代码手",
            "coder_start": "代码手开始求解{key}",
            "coder_success": "代码手求解成功{key}",
            "writer_start": "论文手开始写{key}部分",
            "writer_complete": "论文手完成{key}部分",
            "subtask_failed": "子任务 {key} 失败: {error}",
            "writer_failed": "论文手处理 {key} 部分失败: {error}",
        },
        "en": {
            "coordinator_start": "Analyzing user intent and decomposing problems...",
            "coordinator_complete": "Problem analysis complete, task transferred to modeler",
            "modeler_start": "Modeler starting modeling process...",
            "creating_sandbox": "Creating code sandbox environment",
            "sandbox_created": "Sandbox created successfully",
            "init_coder": "Initializing coder agent",
            "coder_start": "Coder agent solving {key}",
            "coder_success": "Coder agent successfully solved {key}",
            "writer_start": "Writer agent writing {key} section",
            "writer_complete": "Writer agent completed {key} section",
            "subtask_failed": "Subtask {key} failed: {error}",
            "writer_failed": "Writer agent failed to process {key} section: {error}",
        },
    }

    lang = "en" if language == "en" else "zh"
    message = messages[lang].get(key, key)

    if kwargs:
        return message.format(**kwargs)
    return message
